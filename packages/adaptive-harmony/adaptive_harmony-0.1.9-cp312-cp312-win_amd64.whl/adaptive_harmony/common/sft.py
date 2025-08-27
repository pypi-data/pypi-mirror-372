from tqdm.auto import tqdm
from adaptive_harmony import StringThread, DataSet, CosineScheduler, TrainingModel, Logger, JobNotifier, StageNotifier
from adaptive_harmony.core.utils import async_map_batch
from adaptive_harmony.metric_logger import StdoutLogger
from adaptive_harmony.graders import Grader
from adaptive_harmony.common.validation import run_validation


class SFT:

    def __init__(
        self,
        dataset: list[StringThread],
        model: TrainingModel,
        logger: Logger = StdoutLogger(),
        stage_notifier: StageNotifier = JobNotifier().stage_notifier("SFT Training"),
        lr: float = 1e-5,
        samples_per_batch=512,  # axel magic number: "pretty well validated across different scales"
        max_grad_norm=1.0,
        epochs: int = 1,
        validation_frequency: float = 0.2,
        validation_dataset: list[StringThread] | None = None,
        grader: Grader | None = None,
        weight_decay: float = 0,
    ):
        self.dataset = DataSet(dataset)
        self.lr_schedule = CosineScheduler(lr)
        self.model = model
        self.logger = logger
        self.stage_notifier = stage_notifier
        self.samples_per_batch = samples_per_batch
        self.max_grad_norm = max_grad_norm
        self.epochs = epochs
        self.weight_decay = weight_decay

        self.last_validation_percentage = -1.0  # validation at first step
        self.validation_frequency = validation_frequency
        self.validation_dataset = validation_dataset
        self.grader = grader
        self.scoring_fn = grader.score_float_value if grader else None

    @property
    def training_completion_percentage(self):
        return self.dataset.completion_percentage() / self.epochs

    async def run(self):
        with tqdm(total=100) as pbar:
            while self.training_completion_percentage < 1.0:

                should_run_validation = (
                    self.validation_dataset is not None
                    and self.grader is not None
                    and self.training_completion_percentage - self.last_validation_percentage
                    >= self.validation_frequency
                )
                if should_run_validation:
                    val_logs = await run_validation(self.validation_dataset, self.model, self.scoring_fn)
                    val_scorer_logs = self.grader.get_logs(clear=True)
                    val_logs = {
                        **val_logs,
                        **{"validation/completion_percentage": self.training_completion_percentage},
                        **{f"validation/rewards/{key}": value for key, value in val_scorer_logs.items()},
                    }
                    self.logger(val_logs)
                    self.last_validation_percentage = self.training_completion_percentage

                self.stage_notifier.report_progress(
                    tot_num_samples=len(self.dataset) * self.epochs,
                    processed_num_samples=self.dataset.idx,
                    monitoring_link=self.logger.training_monitoring_link,
                )
                await async_map_batch(self.model.train_language_modelling, self.dataset, self.samples_per_batch)
                cp = self.training_completion_percentage
                current_lr = self.lr_schedule(cp)
                pbar.update(cp * 100.0 - pbar.n)

                logs = await self.model.optim_step(current_lr, wd=self.weight_decay, max_grad_norm=self.max_grad_norm)

                self.logger(logs | dict(completion_percentage=cp))
