import numpy as np
from dataclasses import dataclass
from typing import TypeAlias
from numpy.typing import NDArray

from adaptive_harmony import (
    StringThread,
    DataSet,
    CosineScheduler,
    TrainingModel,
    Logger,
    TokenizedThread,
    JobNotifier,
    StageNotifier,
)
from adaptive_harmony.common.validation import run_validation
from adaptive_harmony.core.utils import async_map_batch, async_map, log_args, get_minibatches
from adaptive_harmony.metric_logger import StdoutLogger
from adaptive_harmony.graders import Grader


FloatArray = TypeAlias = NDArray[np.float32]


@dataclass
class Sample:
    sample: TokenizedThread
    logprobs: list[float]
    ref_logprobs: list[float]
    advantage: float
    score: float
    kl_div: list[float]
    gen_len: float


class GRPO:
    @log_args
    def __init__(
        self,
        dataset: list[StringThread],
        model: TrainingModel,
        grader: Grader,
        logger: Logger = StdoutLogger(),
        stage_notifier: StageNotifier = JobNotifier().stage_notifier("GRPO Training"),
        validation_dataset: list[StringThread] | None = None,
        validation_frequency: float = 0.2,
        max_num_grpo_steps: int | None = None,
        completions_per_sample=8,
        lr: float = 7.5e-7,
        samples_per_batch=128,
        samples_per_mini_batch=128,
        mini_epochs_per_batch=1,
        max_grad_norm=1.0,
        clip_range=0.1,
        kl_beta=0.01,
        weight_decay=0,
    ):
        # Core components
        self.dataset = DataSet(dataset, allow_looping=True)
        self.model = model
        self.grader = grader
        self.scoring_fn = grader.score_float_value
        self.logger = logger
        self.stage_notifier = stage_notifier
        # Validation data/params
        self.validation_dataset = validation_dataset
        self.validation_frequency = validation_frequency
        self.last_validation_percentage = -1.0  # Validation will run before training starts
        # GRPO HP's
        self.max_num_batches = max_num_grpo_steps
        self.completions_per_sample = completions_per_sample
        self.lr_schedule = CosineScheduler(lr)
        self.samples_per_batch = samples_per_batch // completions_per_sample
        self.samples_per_mini_batch = samples_per_mini_batch
        self.total_num_samples = (
            self.max_num_batches * self.samples_per_batch if self.max_num_batches else len(self.dataset)
        )
        self.max_grad_norm = max_grad_norm
        self.clip_range = clip_range
        self.kl_beta = kl_beta
        self.weight_decay = weight_decay
        self.mini_epochs_per_batch = mini_epochs_per_batch

        self.num_batches_processed = 0

    @property
    def training_completion_percentage(self):
        return (
            self.dataset.completion_percentage()
            if self.max_num_batches is None
            else min(self.num_batches_processed / self.max_num_batches, 1.0)
        )

    async def gen_data(self, sample: StringThread) -> list[Sample]:
        assert self.model_ref is not None, "Calling `gen_data` before reference model has been set"

        all_samples = await async_map(self.model.generate_tokens, [sample] * self.completions_per_sample)
        string_samples = await async_map(self.model.detokenize_thread, all_samples)
        all_scores = np.array(await async_map(self.scoring_fn, string_samples), dtype=np.float32)

        advantages: FloatArray = all_scores - all_scores.mean()
        advantages /= advantages.std() + 1e-8

        logprobs = await async_map(self.model.logprobs_per_token, all_samples)
        ref_logprobs = await async_map(self.model_ref.logprobs_per_token, all_samples)
        kl = np.array(np.concatenate(logprobs), dtype=np.float32) - np.array(
            np.concatenate(ref_logprobs), dtype=np.float32
        )

        samples = []
        for i in range(len(logprobs)):
            samples.append(
                Sample(
                    sample=all_samples[i],
                    logprobs=logprobs[i],
                    ref_logprobs=ref_logprobs[i],
                    advantage=advantages[i],
                    score=all_scores[i],
                    kl_div=kl[i],
                    gen_len=all_samples[i].len_last_turn(),
                )
            )
        return samples

    async def train_sample(self, sample: Sample):
        await self.model.train_grpo(
            sample.sample,
            sample.logprobs,
            sample.ref_logprobs,
            [sample.advantage] * len(sample.logprobs),
            self.clip_range,
            self.kl_beta,
        )

    async def run(self):
        self.model_ref = await self.model.clone_inf()

        while self.training_completion_percentage < 1.0:
            self.stage_notifier.report_progress(
                tot_num_samples=self.total_num_samples,
                processed_num_samples=self.dataset.idx,
                monitoring_link=self.logger.training_monitoring_link,
            )
            self.num_batches_processed += 1

            # Run validation if needed
            should_run_validation = (
                self.validation_dataset is not None
                and self.training_completion_percentage - self.last_validation_percentage >= self.validation_frequency
            )
            if should_run_validation:
                assert self.validation_dataset is not None, "validation_samples must be set"
                val_logs = await run_validation(self.validation_dataset, self.model, self.scoring_fn)
                val_scorer_logs = self.grader.get_logs(clear=True)
                val_logs = {  # Join all validation logs
                    **val_logs,
                    **{"validation/completion_percentage": self.training_completion_percentage},
                    **{f"validation/rewards/{key}": value for key, value in val_scorer_logs.items()},
                }
                self.logger(val_logs)
                self.last_validation_percentage = self.training_completion_percentage

            # Generate training samples
            data = await async_map_batch(self.gen_data, self.dataset, self.samples_per_batch)
            scorer_logs = self.grader.get_logs(clear=True)
            batch_logs = {
                **{f"rewards/{key}": value for key, value in scorer_logs.items()},
                **self.get_train_batch_logs(data),
            }

            current_lr = self.lr_schedule(self.training_completion_percentage)

            # Train on generated samples
            flattened_data = sum([inner_list for inner_list in data], start=[])
            minibatches = get_minibatches(flattened_data, self.samples_per_mini_batch, self.mini_epochs_per_batch)
            for idx, mini_batch in enumerate(minibatches):
                await async_map(self.train_sample, mini_batch)
                optim_logs = await self.model.optim_step(
                    current_lr, wd=self.weight_decay, max_grad_norm=self.max_grad_norm
                )
                if idx == len(minibatches) - 1:
                    # only log tables and full batch-related logs on the final minibatch
                    self.logger(optim_logs | batch_logs)
                else:
                    self.logger(optim_logs)

        self.logger.close()

    def get_train_batch_logs(self, data: list[list[Sample]]) -> dict:
        return {
            **dict(
                completion_percentage=self.training_completion_percentage,
                percentage_no_advantages=np.mean(
                    [all(sample.advantage == batch[0].advantage for sample in batch) for batch in data]
                ).item(),
                score_mean=np.mean([[sample.score for sample in batch] for batch in data]).item(),
                score_std=np.std([[sample.score for sample in batch] for batch in data]).item(),
                kl_div=np.mean(np.concatenate([[sample.kl_div for sample in batch] for batch in data])).item(),
                advantages=np.mean(np.concatenate([[sample.advantage for sample in batch] for batch in data])).item(),
                generation_length=np.mean([np.mean([sample.gen_len for sample in batch]) for batch in data]).item(),
                logprobs=np.mean(
                    np.concatenate([np.concatenate([sample.logprobs for sample in batch]) for batch in data])
                ).item(),
                ref_logprobs=np.mean(
                    np.concatenate([np.concatenate([sample.ref_logprobs for sample in batch]) for batch in data])
                ).item(),
            ),
            **{"training/completion_percentage": self.training_completion_percentage},
        }
