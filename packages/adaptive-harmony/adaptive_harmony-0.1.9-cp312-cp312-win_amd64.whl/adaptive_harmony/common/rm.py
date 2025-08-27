from tqdm.auto import tqdm
from adaptive_harmony import StringThread, DataSet, CosineScheduler, TrainingModel, Logger, StageNotifier, JobNotifier
from adaptive_harmony.core.utils import async_map_batch
from adaptive_harmony.metric_logger import StdoutLogger


class RewardModelling:

    def __init__(
        self,
        dataset: list[tuple[StringThread, StringThread]] | list[StringThread],
        model: TrainingModel,
        logger: Logger = StdoutLogger(),
        job_notifier: StageNotifier = JobNotifier().stage_notifier("Reward Model Training"),
        lr: float = 1e-06,
        samples_per_batch: int = 64,
        max_grad_norm: float = 1.0,
        epochs: int = 1,
    ):
        self.dataset: DataSet[StringThread | tuple[StringThread, StringThread]] = DataSet(dataset, allow_looping=True)
        self.lr_schedule = CosineScheduler(lr)
        self.model = model
        self.logger = logger
        self.job_notifier = job_notifier
        self.samples_per_batch = samples_per_batch
        self.max_grad_norm = max_grad_norm
        self.epochs = epochs

    @property
    def training_completion_percentage(self):
        return self.dataset.completion_percentage() / self.epochs

    async def train_rm(self, sample: tuple[StringThread, StringThread] | StringThread):
        # having both preference and metric feedback in dataset likely will never happen, but it's possible
        if isinstance(sample, tuple):
            await self.model.train_ranking(sample[0], sample[1])
        else:
            target_value = sample.metadata["res"]
            await self.model.train_mse(sample, target_value)

    async def run(self):
        with tqdm(total=100) as pbar:
            while self.training_completion_percentage < 1.0:
                self.job_notifier.report_progress(
                    tot_num_samples=len(self.dataset) * self.epochs,
                    processed_num_samples=self.dataset.idx,
                    monitoring_link=self.logger.training_monitoring_link,
                )
                await async_map_batch(self.train_rm, self.dataset, self.samples_per_batch)
                cp = self.training_completion_percentage
                current_lr = self.lr_schedule(cp)
                pbar.update(cp * 100.0 - pbar.n)

                logs = await self.model.optim_step(current_lr, wd=0, max_grad_norm=self.max_grad_norm)

                self.logger(logs | dict(completion_percentage=cp))
