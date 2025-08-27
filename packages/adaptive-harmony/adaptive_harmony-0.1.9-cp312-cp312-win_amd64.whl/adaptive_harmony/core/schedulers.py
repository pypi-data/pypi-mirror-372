import math
from typing import Callable

Scheduler = Callable[[float], float]


class CosineSchedulerWithoutWarmup:
    def __init__(self, lr=1e-5, decay_factor=10.0) -> None:
        self.max_value = lr
        self.min_value = self.max_value / decay_factor

    def __call__(self, completion_percentage: float) -> float:
        coefficient = 0.5 * (math.cos(math.pi * completion_percentage) + 1.0)
        value_delta = self.max_value - self.min_value
        return self.min_value + coefficient * value_delta


class CombinedSchedule:
    def __init__(self, a: Scheduler, b: Scheduler, change_point: float) -> None:
        self.a = a
        self.b = b
        self.change_point = change_point

    def __call__(self, completion_percentage: float) -> float:
        if completion_percentage < self.change_point:
            return self.a(completion_percentage / self.change_point)
        else:
            return self.b((completion_percentage - self.change_point) / (1 - self.change_point))


class CosineScheduler:
    def __init__(self, lr=1e-5, warmup_percentage=0.1, decay_factor=10.0):
        self.combined = CombinedSchedule(
            lambda x: x * lr, CosineSchedulerWithoutWarmup(lr, decay_factor), warmup_percentage
        )

    def __call__(self, completion_percentage: float) -> float:
        return self.combined(completion_percentage)
