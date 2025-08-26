from adaptive_harmony import StageNotifier


class SimpleTrainingProgressNotifier:
    def __init__(self, job_notifier: StageNotifier, monitoring_link=None):
        self.job_notifier = job_notifier
        self.monitoring_link = monitoring_link

    def __enter__(self):
        self.job_notifier.report_training_progress(0, 0, self.monitoring_link)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.job_notifier.report_training_progress(0, 1, self.monitoring_link)

    async def __aenter__(self):
        self.job_notifier.report_training_progress(0, 0, self.monitoring_link)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.job_notifier.report_training_progress(0, 1, self.monitoring_link)
