from tqdm.auto import tqdm

from adaptive_harmony import StringThread, DataSet, CosineScheduler, TrainingModel, Logger, JobNotifier, StageNotifier
from adaptive_harmony.core.utils import async_map_batch


class DPO:

    def __init__(
        self,
        dataset: list[tuple[StringThread, StringThread]],  # (positive_sample, negative_sample)
        model: TrainingModel,
        logger: Logger,
        stage_notifier: StageNotifier = JobNotifier().stage_notifier("DPO Training"),
        lr: float = 1e-4,
        samples_per_batch=32,
        max_grad_norm=1.0,
        kl_beta=0.1,
        epochs=1,
    ):
        # Core components
        self.model_ref = None
        self.dataset = DataSet(dataset)
        self.model = model
        self.logger = logger
        self.stage_notifier = stage_notifier
        self.lr_schedule = CosineScheduler(lr)
        self.samples_per_batch = samples_per_batch
        self.max_grad_norm = max_grad_norm

        # DPO HP's
        self.kl_beta = kl_beta
        self.epochs = epochs

    @property
    def training_completion_percentage(self):
        return self.dataset.completion_percentage() / self.epochs

    async def process_sample(self, sample: tuple[StringThread, StringThread]):
        assert self.model_ref is not None, "Calling `process_sample_dpo` before reference model has been set"

        pos, neg = sample
        ref_logprobs_pos = await self.model_ref.logprobs(pos)
        ref_logprobs_neg = await self.model_ref.logprobs(neg)
        await self.model.train_dpo(pos, neg, ref_logprobs_pos, ref_logprobs_neg, self.kl_beta)

    async def run(self):
        self.model_ref = await self.model.clone_inf()

        with tqdm(total=100) as pbar:
            while self.training_completion_percentage < 1.0:
                self.stage_notifier.report_progress(
                    tot_num_samples=len(self.dataset) * self.epochs,
                    processed_num_samples=self.dataset.idx,
                    monitoring_link=self.logger.training_monitoring_link,
                )
                await async_map_batch(self.process_sample, self.dataset, self.samples_per_batch)
                cp = self.training_completion_percentage
                current_lr = self.lr_schedule(self.dataset.completion_percentage())
                pbar.update(cp * 100.0 - pbar.n)
                logs = await self.model.optim_step(current_lr, wd=0, max_grad_norm=self.max_grad_norm)
                self.logger(logs | dict(completion_percentage=cp))
