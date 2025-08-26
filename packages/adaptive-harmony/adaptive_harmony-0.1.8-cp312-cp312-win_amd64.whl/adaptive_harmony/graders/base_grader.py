import statistics
from abc import ABC, abstractmethod
from typing import Any, Callable, Awaitable, cast, TYPE_CHECKING

from adaptive_harmony import StringThread, Grade, HarmonyClient
from adaptive_harmony.graders.utils import SuccessJudgeLog, FailedJudgeLog
from adaptive_harmony.logging_table import Table

from adaptive_harmony.runtime.data import (
    AdaptiveGrader,
    CustomJudge,
    PrebuiltJudge,
    RemoteRewardEndpoint,
)

# Add type checking import for type hints only
if TYPE_CHECKING:
    from adaptive_harmony.graders.binary_judge.binary_judge import BinaryJudgeGrader
    from adaptive_harmony.graders.reward_server_grader import RewardServerGrader
    from adaptive_harmony.graders.faithfulness_judge.faithfulness_judge import FaithfulnessGrader


class Grader[LogType](ABC):
    """
    Base Grader to inherit from when building a scoring function.
    """

    def __init__(self, grader_key: str):
        self._logs: list[LogType] = []
        self.grader_key = grader_key

    @abstractmethod
    async def grade(self, sample: StringThread) -> Grade:
        """
        Grade a single sample.
        Returns a single float score, with optional metadata.
        Metadata can be useful for evals when LLM reasoning regarding the score is available.
        """
        pass

    @abstractmethod
    async def setup(self) -> None:
        """
        Setup the grader.
        """
        pass

    @abstractmethod
    async def teardown(self) -> None:
        """
        Teardown the grader.
        """
        pass

    async def score_float_value(self, sample: StringThread) -> float:
        """Returns only the float score from .score"""
        return (await self.grade(sample)).value

    def add_log(self, log_data: LogType) -> None:
        """Add a log entry to the scorer's log collection."""
        self._logs.append(log_data)

    def get_logs(self, clear: bool = False, log_all_samples: bool = False) -> dict[str, float | Table]:
        """
        Get aggregated logs from all score calls.
        Base implementation computes statistics for "score" keys in individual logs.
        If there are none, returns empty dict.
        """
        if not self._logs:
            return {}

        scores = [s for s in [cast(dict[str, Any], log).get("score") for log in self._logs] if s is not None]
        logs = {}
        if scores:
            logs.update(
                dict(
                    **{
                        f"score/{key}": value
                        for key, value in dict(
                            mean=statistics.mean(scores),
                            std=statistics.stdev(scores) if len(scores) > 1 else 0.0,
                            min=min(scores),
                            max=max(scores),
                            count=len(scores),
                        ).items()
                    },
                )
            )
        if clear:
            self.clear_logs()
        return logs

    def clear_logs(self) -> None:
        """
        Clear all accumulated logs.
        """
        self._logs.clear()

    def get_sample_tables(
        self, successful_samples: list[SuccessJudgeLog], failed_samples: list[FailedJudgeLog] | None = None
    ):
        table_logs = {}
        scored_samples = (
            Table()
            .add_column("Prompt", [log["prompt"] for log in successful_samples])
            .add_column("Reasoning", [log.get("reasoning") for log in successful_samples])
            .add_column("Score", [float(log["score"]) for log in successful_samples])
        )
        if failed_samples:

            unscored_samples = (
                Table()
                .add_column("Prompt", [log.get("prompt") for log in failed_samples])
                .add_column("Error", [str(log["error"]) for log in failed_samples])
            )
            table_logs["score/unscored_samples"] = unscored_samples
            table_logs["score/unscored_samples_count"] = len(failed_samples)

        table_logs["score/scored_samples"] = scored_samples
        table_logs["score/scored_samples_count"] = len(successful_samples)
        return table_logs

    @classmethod
    def from_function(
        cls, grader_key: str, async_fn: Callable[[StringThread], Awaitable[float]]
    ) -> "Grader[dict[str, Any]]":
        class FunctionScorer(Grader[dict[str, float]]):
            def __init__(self):
                super().__init__(grader_key)

            async def grade(self, sample: StringThread) -> Grade:
                result = await async_fn(sample)
                grade = Grade(value=result, grader_key=self.grader_key)
                self.add_log({"score": result})
                return grade

            async def setup(self) -> None:
                pass

            async def teardown(self) -> None:
                pass

        return FunctionScorer()

    @classmethod
    def from_config(
        cls, config: AdaptiveGrader, client: HarmonyClient, tp: int | None = None, kv_cache_len: int | None = None
    ) -> "Grader[dict[str, Any]]":

        match config.grader.config.type:
            case "Judge":
                return cls.from_binary_judge(
                    config.grader.key, config.grader.grader_id, config.grader.config, client, tp, kv_cache_len
                )
            case "Prebuilt":
                return cls.from_prebuilt_judge(
                    config.grader.key, config.grader.grader_id, config.grader.config, client, tp, kv_cache_len
                )
            case "Remote":
                return cls.from_remote_reward_endpoint(config.grader.key, config.grader.grader_id, config.grader.config)
            case _:
                raise ValueError(f"Invalid grader type: {config.grader.config.type}")

    @classmethod
    def from_binary_judge(
        cls,
        grader_key: str,
        grader_id: str,
        config: CustomJudge,
        client: HarmonyClient,
        tp: int | None = None,
        kv_cache_len: int | None = None,
    ) -> "Grader[dict[str, Any]]":
        # Import here to avoid circular dependency
        from adaptive_harmony.graders.binary_judge.binary_judge import BinaryJudgeGrader
        from adaptive_harmony.graders.binary_judge.prompts import to_binary_judge_shot

        return BinaryJudgeGrader(
            grader_key=grader_key,
            grader_id=grader_id,
            model_key=config.model_uri,
            client=client,
            criteria=config.criteria,
            shots=[to_binary_judge_shot(example) for example in config.examples],
            tp=tp,
            kv_cache_len=kv_cache_len,
        )

    @classmethod
    def from_prebuilt_judge(
        cls,
        grader_key: str,
        grader_id: str,
        config: PrebuiltJudge,
        client: HarmonyClient,
        tp: int | None = None,
        kv_cache_len: int | None = None,
    ) -> "Grader[dict[str, Any]]":
        match config.prebuilt_config_key:
            case "Faithfulness":
                # Import here to avoid circular dependency
                from adaptive_harmony.graders.faithfulness_judge.faithfulness_judge import FaithfulnessGrader

                return FaithfulnessGrader(
                    grader_key=grader_key,
                    grader_id=grader_id,
                    model_key=config.model_uri,
                    client=client,
                    tp=tp,
                    kv_cache_len=kv_cache_len,
                )
            case "AnswerRelevancy":
                raise NotImplementedError(f"Prebuilt judge {config.prebuilt_config_key} is not implemented")
            case "ContextRelevancy":
                raise NotImplementedError(f"Prebuilt judge {config.prebuilt_config_key} is not implemented")
            case _:
                raise ValueError(f"Invalid prebuilt judge type: {config.prebuilt_config_key}")

    @classmethod
    def from_remote_reward_endpoint(
        cls, grader_key: str, grader_id: str, config: RemoteRewardEndpoint
    ) -> "Grader[dict[str, Any]]":
        # Import here to avoid circular dependency
        from adaptive_harmony.graders.reward_server_grader import RewardServerGrader

        return RewardServerGrader(grader_key=grader_key, grader_id=grader_id, reward_server_ip=config.url)
