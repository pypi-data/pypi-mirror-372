import numpy as np
from dataclasses import dataclass

from adaptive_harmony import (
    StringThread,
    DataSet,
    CosineScheduler,
    TrainingModel,
    Logger,
    TokenizedThread,
    CombinedSchedule,
    JobNotifier,
    InferenceModel,
    StageNotifier,
)
from adaptive_harmony.common.validation import run_validation
from adaptive_harmony.core import rl_utils
from adaptive_harmony.core.utils import async_map_batch, get_minibatches, async_map, log_args
from adaptive_harmony.metric_logger import StdoutLogger
from adaptive_harmony.graders import Grader


@dataclass
class Sample:
    sample: TokenizedThread
    string_sample: StringThread
    logprobs: list[float]
    ref_logprobs: list[float]
    advantages: list[float]
    returns: list[float]
    score: float
    kl_div: list[float]
    values: list[float]
    kl_pen: float
    cumulative_reward: float


class PPO:
    @log_args
    def __init__(
        self,
        dataset: list[StringThread],
        model: TrainingModel,
        value_model: TrainingModel,
        grader: Grader,
        logger: Logger = StdoutLogger(),
        stage_notifier: StageNotifier = JobNotifier().stage_notifier("PPO Training"),
        validation_dataset: list[StringThread] | None = None,
        validation_frequency: float = 0.2,
        max_num_ppo_steps: int | None = None,
        value_only_fraction=0.25,
        lr_policy: float = 0.75e-6,
        lr_value: float = 1e-6,
        samples_per_batch=128,
        samples_per_mini_batch=128,
        mini_epochs_per_batch=1,
        max_grad_norm=1.0,
        clip_range=0.1,
        kl_beta=0.1,
        gae_lambda=0.95,
        gae_gamma=1.0,
        weight_decay: float = 0,
    ):
        # Core components
        self.model_ref: InferenceModel | None = None  # Instantiated when run() is called
        self.dataset = DataSet(dataset, allow_looping=True)
        self.model = model
        self.value_model = value_model
        self.grader = grader
        self.scoring_fn = grader.score_float_value
        self.logger = logger
        self.stage_notifier = stage_notifier
        # Validation data/params
        self.validation_dataset = validation_dataset
        self.validation_frequency = validation_frequency
        self.last_validation_percentage = -1.0
        # PPO HP's
        self.max_num_batches = max_num_ppo_steps
        self.lr_schedule_policy = CombinedSchedule(lambda _: 0, CosineScheduler(lr_policy), value_only_fraction)
        self.lr_schedule_value = CosineScheduler(lr_value)
        self.samples_per_batch = samples_per_batch
        self.samples_per_mini_batch = samples_per_mini_batch
        self.total_num_samples = (
            self.max_num_batches * self.samples_per_batch if self.max_num_batches else len(self.dataset)
        )
        self.mini_epochs_per_batch = mini_epochs_per_batch
        self.max_grad_norm = max_grad_norm
        self.clip_range = clip_range
        self.kl_beta = kl_beta
        self.gae_lambda = gae_lambda
        self.gae_gamma = gae_gamma
        self.weight_decay = weight_decay

        self.num_batches_processed = 0

    @property
    def training_completion_percentage(self):
        return (
            self.dataset.completion_percentage()
            if self.max_num_batches is None
            else min(self.num_batches_processed / self.max_num_batches, 1.0)
        )

    async def generate_sample(self, prompt: StringThread):
        assert self.model_ref is not None, "Calling `generate_sample` before reference model has been set"

        sample = await self.model.generate_tokens(prompt)
        string_sample = await self.model.detokenize_thread(sample)
        score = await self.scoring_fn(string_sample)
        values = await self.value_model.score(sample)

        logprobs = await self.model.logprobs_per_token(sample)
        ref_logprobs = await self.model_ref.logprobs_per_token(sample)

        kl = np.array(logprobs, dtype=np.float32) - np.array(ref_logprobs, dtype=np.float32)
        kl_pen = -kl * self.kl_beta
        rewards = np.array(kl_pen)
        rewards[-1] += score

        advantages = rl_utils.gae_advantages(values, rewards.tolist(), self.gae_lambda, self.gae_gamma)
        returns = rl_utils.discounted_cumulative_rewards(rewards.tolist(), self.gae_gamma)

        return Sample(
            sample=sample,
            string_sample=string_sample,
            logprobs=logprobs,
            ref_logprobs=ref_logprobs,
            advantages=advantages,
            returns=returns,
            score=score,
            values=values,
            cumulative_reward=sum(rewards),
            kl_div=kl.tolist(),
            kl_pen=np.sum(kl_pen).item(),
        )

    async def train_ppo(self, sample: Sample):
        await self.model.train_ppo(sample.sample, sample.logprobs, sample.advantages, self.clip_range)

    async def train_value(self, sample: Sample):
        await self.value_model.train_mse_per_token(sample.sample, sample.returns)

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
                val_logs = {
                    **val_logs,
                    **{"validation/completion_percentage": self.training_completion_percentage},
                    **{f"validation/rewards/{key}": value for key, value in val_scorer_logs.items()},
                }
                self.logger(val_logs)
                self.last_validation_percentage = self.training_completion_percentage

            # Generate training samples
            data = await async_map_batch(
                self.generate_sample,
                self.dataset,
                self.samples_per_batch,
            )
            scorer_logs = self.grader.get_logs(clear=True)
            batch_logs = {
                **{f"rewards/{key}": value for key, value in scorer_logs.items()},
                **self.get_train_batch_logs(data),
            }

            lr_policy = self.lr_schedule_policy(self.training_completion_percentage)
            lr_value = self.lr_schedule_value(self.training_completion_percentage)

            # Train on generated samples
            if lr_policy > 0:
                minibatches = get_minibatches(data, self.samples_per_mini_batch, self.mini_epochs_per_batch)
                for idx, mini_batch in enumerate(minibatches):
                    await async_map(self.train_ppo, mini_batch)
                    optim_logs = await self.model.optim_step(
                        lr_policy, wd=self.weight_decay, max_grad_norm=self.max_grad_norm
                    )
                    if idx == len(minibatches) - 1:
                        # only log tables and full batch-related logs on the final minibatch
                        self.logger(optim_logs | batch_logs)
                    else:
                        self.logger(optim_logs)

            for mini_batch in get_minibatches(data, self.samples_per_mini_batch, self.mini_epochs_per_batch):
                await async_map(self.train_value, mini_batch)
                batch_logs |= await self.value_model.optim_step(lr_value, wd=0, max_grad_norm=self.max_grad_norm)
                self.logger(batch_logs)

        self.logger.close()

    def get_train_batch_logs(self, data: list[Sample]) -> dict:
        returns = np.concatenate([batch.returns for batch in data])
        cur_values = np.concatenate([batch.values for batch in data])

        var_return = returns.var()
        mean_error = ((cur_values - returns) ** 2).mean()
        explained_variance = (1 - mean_error / (var_return + 1e-8)).item()

        logs = dict(
            completion_percentage=self.training_completion_percentage,
            score_mean=np.mean([batch.score for batch in data]).item(),
            score_std=np.std([batch.score for batch in data]).item(),
            returns=np.mean(np.concatenate([batch.returns for batch in data])),
            kl_div=np.mean(np.concatenate([batch.kl_div for batch in data])),
            advantages=np.mean(np.concatenate([batch.advantages for batch in data])),
            generation_length=np.mean([batch.sample.len_last_turn() for batch in data]),
            logprobs=np.mean(np.concatenate([batch.logprobs for batch in data])),
            ref_logprobs=np.mean(np.concatenate([batch.ref_logprobs for batch in data])),
            kl_penalty=np.mean([batch.kl_pen for batch in data]),
            explained_variance=explained_variance,
            cumulative_reward=np.mean([batch.cumulative_reward for batch in data]),
        ) | {
            "training/completion_percentage": self.training_completion_percentage
        }  # to have an comparable axis with prior runs

        return logs
