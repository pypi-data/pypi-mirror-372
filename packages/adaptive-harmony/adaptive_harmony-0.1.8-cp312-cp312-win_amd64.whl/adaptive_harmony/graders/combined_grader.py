from asyncio import gather
from adaptive_harmony.adaptive_harmony import HarmonyClient
from loguru import logger
from typing import Literal, Sequence, Any

from adaptive_harmony import StringThread
from adaptive_harmony.core.structured_output import JsonParseError
from adaptive_harmony.graders.base_grader import Grader, Grade
from adaptive_harmony.graders.exceptions import IgnoreScoreException


class CombinedGrader(Grader):
    """
    Combines grades from multiple graders.
    Aggregates their results using weighted sum or average.
    Ignores failing graders, proceeds calculating the aggregate grade with the rest.
    """

    def __init__(
        self,
        grader_key: str,
        graders: Sequence[Grader],
        weights: list[float] | None = None,
        aggregation_method: Literal["sum", "mean"] = "mean",
        failure_rate_warning_threshold: float = 0.2,
    ):
        super().__init__(grader_key)
        self.graders = graders
        if weights:
            assert len(weights) == len(graders), "Number of weights must match number of graders"
        self.weights = weights or [1.0] * len(graders)
        self.agg_method = aggregation_method
        self.failure_rate_warning_threshold = failure_rate_warning_threshold

    async def setup(self) -> None:
        for grader in self.graders:
            await grader.setup()

    async def teardown(self) -> None:
        for grader in self.graders:
            await grader.teardown()

    async def grade(self, sample: StringThread) -> Grade:

        async def separate_success_from_fail_graders(grader: Grader) -> Grade | None:
            try:
                return await grader.grade(sample)
            except (IgnoreScoreException, JsonParseError):
                # return None if score is supposed to be ignored, or judge output format failure
                return None
            except Exception as e:
                # fail for any other exception
                raise e

        tasks = [separate_success_from_fail_graders(grader) for grader in self.graders]
        results: list[Grade | None] = await gather(*tasks)

        weighted_scores = []
        failed_graders = []

        # Separate successful and failed results
        successful_graders: list[str] = []
        successful_grades: list[Grade] = []
        successful_weights = []

        for result, weight, grader in zip(results, self.weights, self.graders):
            if result is not None:
                # Successful grader
                weighted_score = result.value * weight
                successful_graders.append(grader.grader_key)
                weighted_scores.append(weighted_score)
                successful_grades.append(result)
                successful_weights.append(weight)
            else:
                # Failed grader
                failed_graders.append(grader.grader_key)

        # Fail if no successfull graders
        if not successful_grades:
            raise RuntimeError("All graders failed - cannot compute aggregate grade")

        # Warn if more than a set % of scorers failed
        total_graders = len(self.graders)
        failure_rate = len(failed_graders) / total_graders
        if failure_rate > self.failure_rate_warning_threshold:
            logger.warning(f"{len(failed_graders)}/{total_graders}% of graders failed for sample: {failed_graders}")

        # Aggregate scores
        if self.agg_method == "sum":
            final_score = sum(weighted_scores)
        elif self.agg_method == "mean":
            # For average, we normalize by the sum of successful weights (renormalize)
            final_score = sum(weighted_scores) / sum(successful_weights)
        else:
            raise ValueError(f"Unknown aggregation method: {self.agg_method}")

        # Log the combined score.
        self.add_log({"score": final_score})

        reason = "\n".join(
            [
                f"{grader_key}: {grade.value} - {grade.reasoning}"
                for grader_key, grade in zip(successful_graders, successful_grades)
            ]
        )

        return Grade(
            value=final_score,
            grader_key=self.grader_key,
            reasoning=reason,
        )

    def get_logs(self, clear: bool = False) -> dict[str, Any]:
        # Get our own aggregated logs
        combined_logs = super().get_logs(clear=False)

        # Get logs from all individual scorers
        # If scorer has no logging name, attribute unique id within scorer type group as name
        all_logs = combined_logs
        for grader in self.graders:
            scorer_logs = grader.get_logs(clear=clear)
            all_logs = {
                **all_logs,
                **{f"{grader.grader_key}/{key}": value for key, value in scorer_logs.items()},
            }
        if clear:
            self.clear_logs()
        return all_logs

    def clear_logs(self) -> None:
        super().clear_logs()
        for grader in self.graders:
            grader.clear_logs()
