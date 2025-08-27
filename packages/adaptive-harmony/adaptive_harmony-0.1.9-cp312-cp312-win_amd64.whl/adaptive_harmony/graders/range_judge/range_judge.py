import asyncio
from adaptive_harmony.adaptive_harmony import HarmonyClient
import numpy as np
from pydantic import BaseModel, Field


from adaptive_harmony import InferenceModel, StringThread, StringTurn
from adaptive_harmony.core.structured_output import JsonParseError, render_pydantic_model
from adaptive_harmony.core.utils import stringify_thread
from adaptive_harmony.logging_table import Table
from adaptive_harmony.graders import Grader, Grade
from adaptive_harmony.graders.range_judge.prompts import (
    ReasonedScore,
    RangeScorerTemplates,
    SubrangeExpectations,
    RangeJudgeShot,
    get_prompt_building_blocks,
    create_shots,
)
from adaptive_harmony.graders.utils import (
    sample_score_distribution,
    SuccessJudgeLog,
    FailedJudgeLog,
)


class RangeJudgeGrader(Grader[SuccessJudgeLog | FailedJudgeLog]):
    """
    Scores a thread in a range of integer scores, based on a list of evaluation steps.
    If evaluation steps are not provided, they are generated from the criteria.
    The final score is computed as a weighted average of all possible scores,
    where the weights are the logprobs of each score.
    You can pass subrange_expectations to the scorer, to help the judge
    understand the correspondence between score subranges and expected quality levels.
    """

    def __init__(
        self,
        grader_key: str,
        model_key: str,
        client: HarmonyClient,
        criteria: str,
        score_range: tuple[int, int] = (1, 5),
        evaluation_steps: list[str] | None = None,
        subrange_expectations: list[SubrangeExpectations] | None = None,
        shots: list[RangeJudgeShot] | None = None,
        normalize_score: bool = True,
        kv_cache_len: int | None = None,
        tp: int | None = None,
        max_gen_length: int | None = None,
    ):
        assert model_key.startswith("model_registry://"), "External models cannot be used in RangeJudgeScorer"

        super().__init__(grader_key)
        self.model_key = model_key
        self.kv_cache_len = kv_cache_len
        self.tp = tp
        self.max_gen_length = max_gen_length
        self.model: InferenceModel
        self.criteria = criteria
        self.client = client
        self.score_range = score_range
        self.min_score, self.max_score = score_range
        self.subrange_expectations = subrange_expectations
        self._shots = shots
        self.normalize_score = normalize_score
        self.judge_is_spawned = False

        if evaluation_steps is None:
            self._str_evaluation_steps = None
            self._list_eval_steps = None
        else:
            self._str_evaluation_steps = "\n".join([f"{i + 1}: {step}" for i, step in enumerate(evaluation_steps)])
            self._list_eval_steps = evaluation_steps

    async def setup(self) -> None:
        gen_params = {
            k: v
            for k, v in {
                "kv_cache_len": self.kv_cache_len,
                "tokens_to_generate": self.max_gen_length,
            }.items()
            if v is not None
        }
        model = self.client.model(self.model_key, **gen_params)
        if self.tp is not None:
            model = model.tp(self.tp)
        self.model = await model.spawn_inference(self.grader_key)
        self.judge_is_spawned = True

    async def teardown(self) -> None:
        if self.judge_is_spawned:
            await self.model.dealloc()
        self.judge_is_spawned = False

    @property
    def evaluation_steps(self) -> list[str] | None:
        return self._list_eval_steps

    @property
    def str_evaluation_steps(self) -> str | None:
        return self._str_evaluation_steps

    @evaluation_steps.setter
    def evaluation_steps(self, steps: list[str]):
        self._list_eval_steps = steps
        self._str_evaluation_steps = "\n".join([f"{i + 1}: {step}" for i, step in enumerate(steps)])

    async def generate_evaluation_steps(self) -> list[str]:
        thread = await self.model.temperature(0.0).generate(RangeScorerTemplates.get_evaluation_steps(self.criteria))
        self._str_evaluation_steps = thread.last_content()
        self._list_eval_steps = self._str_evaluation_steps.split("\n")
        assert self.evaluation_steps
        return self.evaluation_steps

    async def grade(self, sample: StringThread) -> Grade:
        if not self.judge_is_spawned:
            raise RuntimeError("Model not initialized, run grader.setup() before grading")

        if self.evaluation_steps is None:
            if self._shots is not None:
                raise ValueError(
                    "You cannot pass shots without specifying evaluations steps, since your shots' reasoning must match the steps"
                )
            await self.generate_evaluation_steps()

        # Format shots into both user turn formats (for first reasoned scoring step, and for last logprobs scoring step)
        assert self.str_evaluation_steps

        shots = create_shots(self.criteria, self.str_evaluation_steps, self._shots) if self._shots is not None else {}

        # Separate relevant parts of the prompt turns
        prompt_components = get_prompt_building_blocks(sample)
        # Get reasoned scoring thread
        eval_thread = RangeScorerTemplates.get_json_reasoned_score(
            context=prompt_components.context,
            last_user_input=prompt_components.last_user_turn,
            assistant_answer=prompt_components.last_assistant_turn,
            criteria=self.criteria,
            evaluation_steps=self.str_evaluation_steps,
            score_range=self.score_range,
            json_schema=self.model.render_schema(ReasonedScore),
            subrange_expectations=self.subrange_expectations,
            shots=shots.get("reasoning"),
        )
        eval_str_prompt = stringify_thread(eval_thread, sep=f"\n\n{'-'*10}\n\n")
        try:
            _, reasoned_score = await self.model.temperature(0.0).generate_and_validate(eval_thread, ReasonedScore)
        except JsonParseError as e:
            self.add_log({"prompt": eval_str_prompt, "error": f"{str(e)}\n\nCOMPLETION:\n{e.completion}"})
            raise
        except Exception as e:
            self.add_log({"prompt": eval_str_prompt, "error": str(e)})
            raise

        # Get a prompt that includes the reasoning for the sample, all the way to form-filling the score
        up_to_score_thread = RangeScorerTemplates.get_up_to_score(
            context=prompt_components.context,
            last_user_input=prompt_components.last_user_turn,
            assistant_answer=prompt_components.last_assistant_turn,
            criteria=self.criteria,
            evaluation_steps=self.str_evaluation_steps,
            score_range=self.score_range,
            reasoning=reasoned_score.reasoning,
            subrange_expectations=self.subrange_expectations,
            shots=shots.get("scoring"),
        )

        # Get logprobs for each possible final score
        possible_score_ints = [s for s in range(self.min_score, self.max_score + 1)]
        logprobs = await asyncio.gather(
            *[self.model.temperature(0.0).logprobs(up_to_score_thread.assistant(f"{s}")) for s in possible_score_ints]
        )

        # Convert to probabilities and compute weighted average
        probs = np.exp(logprobs - np.logaddexp.reduce(logprobs))
        weighted_score = np.average(possible_score_ints, weights=probs)

        final_score: float = weighted_score
        if self.normalize_score:  # normalize to 0-1 range
            final_score = (weighted_score - self.min_score) / (self.max_score - self.min_score)

        str_prompt = stringify_thread(eval_thread, sep=f"\n\n{'-'*10}\n\n")
        self.add_log({"score": final_score, "prompt": str_prompt, "reasoning": reasoned_score.reasoning})

        metadata = dict(
            criteria=self.criteria,
            raw_avg_score=float(weighted_score),
            scale_range=(self.min_score, self.max_score),
            score_probabilities={str(score): float(prob) for score, prob in zip(possible_score_ints, probs)},
            evaluation_steps=self.evaluation_steps,
            reasoning=reasoned_score.reasoning,
        )

        return Grade(value=float(final_score), grader_key=self.grader_key, reasoning=reasoned_score.reasoning)

    def add_log(self, log_data: SuccessJudgeLog | FailedJudgeLog) -> None:
        self._logs.append(log_data)

    def get_logs(self, clear: bool = False, log_all_samples: bool = False) -> dict[str, float | Table]:
        # Only clear logs at the end if clear is True
        logs = super().get_logs(clear=False)

        successfully_scored_samples = [log for log in self._logs if "score" in log]

        # stratified sample range of scores to see high and low
        if not log_all_samples:
            subset_successfully_scored_samples = sample_score_distribution(successfully_scored_samples, 15)
        else:
            # if we have fewer than 15 samples or we want to log all samples, take them all
            subset_successfully_scored_samples = successfully_scored_samples

        failed_scored_samples = [log for log in self._logs if "error" in log]

        sample_logs = self.get_sample_tables(subset_successfully_scored_samples, failed_scored_samples)

        logs.update(sample_logs)

        if clear:
            self.clear_logs()

        return logs
