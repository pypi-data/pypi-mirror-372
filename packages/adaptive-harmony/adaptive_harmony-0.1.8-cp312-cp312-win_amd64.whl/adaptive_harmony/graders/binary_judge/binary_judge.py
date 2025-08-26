from adaptive_harmony.adaptive_harmony import HarmonyClient
from pydantic import BaseModel, Field
from typing import Literal, TypedDict
from random import shuffle
import json

from adaptive_harmony import StringThread, InferenceModel
from adaptive_harmony.core.structured_output import JsonParseError, render_pydantic_model, render_schema
from adaptive_harmony.core.utils import SingleTurnShot, stringify_thread
from adaptive_harmony.logging_table import Table
from adaptive_harmony.graders import Grader, Grade
from adaptive_harmony.graders.binary_judge.prompts import BinaryJudgeShot, SYSTEM, USER, DEFAULT_SHOTS
from adaptive_harmony.graders.exceptions import IgnoreScoreException
from adaptive_harmony.graders.utils import (
    validate_thread_last_assistant,
    separate_context_from_last_user_turn,
    SuccessJudgeLog,
    FailedJudgeLog,
)


class BinaryJudgeOutput(BaseModel):
    reasoning: str = Field(description="Reasoning to support the rationale behind the score")
    score: Literal["PASS", "FAIL", "NA"] = Field(description="The score for the sample")


class ScoresMap(TypedDict):
    PASS: float
    FAIL: float


class BinaryJudgeGrader(Grader):
    """
    Binary judge for scoring samples as PASS, FAIL or NA using few-shot prompting.
    If custom shots are provided, they are used instead of the default shots.
    """

    def __init__(
        self,
        grader_key: str,
        model_key: str,
        client: HarmonyClient,
        criteria: str,
        tp: int | None = None,
        kv_cache_len: int | None = None,
        max_gen_length: int | None = None,
        shots: list[BinaryJudgeShot] | None = None,
        grader_id: str | None = None,
    ):
        super().__init__(grader_key)
        self._logs: list[SuccessJudgeLog | FailedJudgeLog] = []  # type: ignore[assignment]
        self.criteria = criteria
        self.model_key = model_key
        self.client = client
        self.tp = tp
        self.kv_cache_len = kv_cache_len
        self.max_gen_length = max_gen_length
        self.judge_is_spawned = False
        self.model: InferenceModel
        # Score mapping
        self.scores_map: ScoresMap = {"PASS": 1.0, "FAIL": 0.0}
        self.grader_id_or_key = grader_id or grader_key

        self._original_shots = shots or DEFAULT_SHOTS
        self._shots = self._format_user_shots(shots or DEFAULT_SHOTS)

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
    def shots(self) -> list[BinaryJudgeShot]:
        return self._original_shots

    @shots.setter
    def shots(self, shots: list[BinaryJudgeShot]):
        self._original_shots = shots
        self._shots = self._format_user_shots(shots)

    @staticmethod
    def _extract_user_template_kwargs(thread: StringThread) -> dict[str, str]:

        validate_thread_last_assistant(thread)
        # Separate conversation context from last user turn
        context_turns, user_question = separate_context_from_last_user_turn(thread)
        context_str = stringify_thread(StringThread(context_turns))
        completion = thread.last_content()

        assert user_question, "There must be at least one user turn"
        return dict(
            context=context_str,
            user_question=user_question,
            completion=completion,
        )

    def _get_placeholder_reasoning(self, score: Literal["PASS", "FAIL", "NA"]) -> str:
        if score == "PASS":
            return "The completions complies with the criteria"
        elif score == "FAIL":
            return "The completion does not comply with the criteria"
        else:
            return "The criteria is not applicable to the completion"

    def _format_user_shots(self, shots: list[BinaryJudgeShot]) -> list[SingleTurnShot]:
        """
        Turn a possibly multi turn example into a single turn one,
        with appropriate kwargs to format the task's prompt templates
        """
        new_shots: list[SingleTurnShot] = []
        for shot in shots:
            placeholder_reasoning = self._get_placeholder_reasoning(shot.score)

            user_template_kwargs = self._extract_user_template_kwargs(shot.thread)
            user_template_kwargs["criteria"] = shot.criteria or self.criteria
            single_turn_shot = SingleTurnShot(
                user=user_template_kwargs,
                assistant={
                    "json_answer": render_pydantic_model(
                        BinaryJudgeOutput(
                            reasoning=shot.reasoning or placeholder_reasoning,
                            score=shot.score,
                        )
                    )
                },
            )
            new_shots.append(single_turn_shot)

        return new_shots

    def _get_judge_prompt(self, thread: StringThread) -> StringThread:
        """Build the judging prompt for a given sample."""
        # build the real user template kwargs
        user_template_kwargs = self._extract_user_template_kwargs(thread)
        user_template_kwargs["criteria"] = self.criteria
        # system kwarg
        output_json_schema = render_schema(BinaryJudgeOutput)

        # system
        prompt = StringThread().system(SYSTEM.format(json_schema=output_json_schema))
        # shots
        for shot in self._shots:
            prompt = prompt.user(USER.format(**shot["user"]))
            prompt = prompt.assistant(shot["assistant"]["json_answer"])
        # real input
        prompt = prompt.user(USER.format(**user_template_kwargs))

        return prompt

    async def grade(self, sample: StringThread) -> Grade:
        if not self.judge_is_spawned:
            raise RuntimeError("Model not initialized, run grader.setup() before grading")

        judging_prompt = self._get_judge_prompt(sample)
        str_prompt = stringify_thread(judging_prompt, sep=f"\n\n{'-'*10}\n\n")

        try:
            _, parsed_output = await self.model.temperature(0.0).generate_and_validate(
                judging_prompt, BinaryJudgeOutput
            )
        except JsonParseError as e:
            self.add_log({"prompt": str_prompt, "error": f"{str(e)}\n\nCOMPLETION:\n{e.completion}"})
            raise
        except Exception as e:
            self.add_log({"prompt": str_prompt, "error": str(e)})
            raise

        float_score = self.scores_map.get(parsed_output.score)

        # NA case, ignore score
        if float_score is None:
            self.add_log({"prompt": str_prompt, "error": f"Non applicable score: {parsed_output.reasoning}"})
            raise IgnoreScoreException(f"Non applicable score: {parsed_output.reasoning}")

        else:
            grade = Grade(value=float_score, grader_key=self.grader_id_or_key, reasoning=parsed_output.reasoning)
            self.add_log({"score": float_score, "prompt": str_prompt, "reasoning": parsed_output.reasoning})

            return grade

    def add_log(self, log: SuccessJudgeLog | FailedJudgeLog) -> None:  # type: ignore[override]
        self._logs.append(log)

    def get_logs(self, clear: bool = False, log_all_samples: bool = False) -> dict[str, float | Table]:
        # Only clear logs at the end if clear is True
        logs = super().get_logs(clear=False)

        # get sample of PASS and FAIL samples to log in table
        successfully_scored_samples = [log for log in self._logs if "score" in log]
        if not log_all_samples:
            shuffle(successfully_scored_samples)
            samples_score_0 = [log for log in successfully_scored_samples if log["score"] == self.scores_map["FAIL"]][
                :5
            ]
            samples_score_1 = [log for log in successfully_scored_samples if log["score"] == self.scores_map["PASS"]][
                :5
            ]
            subset_successfully_scored_samples = samples_score_0 + samples_score_1
        else:
            subset_successfully_scored_samples = successfully_scored_samples

        # get failed samples to log in table
        failed_scored_samples = [log for log in self._logs if "error" in log]

        sample_logs = self.get_sample_tables(subset_successfully_scored_samples, failed_scored_samples)
        logs.update(sample_logs)

        if clear:
            self.clear_logs()

        return logs

    @classmethod
    def from_playground_export(
        cls, grader_key: str, model_key: str, client: HarmonyClient, shots: list[dict]
    ) -> "BinaryJudgeGrader":
        """
        Create a BinaryJudgeScorer from a list of shots exported from the Playground.

        Example of shots:
        [
            {
                "criteria": "The assistant should give a number between 1 and 10",
                "judgement": "{\n  \"reasoning\": \"The given completion is a number, but it is not between 1 and 10.\",\n  \"score\": \"FAIL\"\n}",
                "thread": [
                    [
                        "user",
                        "Give me a number"
                    ],
                    [
                        "assistant",
                        "12"
                    ]
                ]
            },
            ...
        ]
        """
        if not shots:
            raise ValueError("No shots provided")

        criteria = shots[0]["criteria"]
        for shot in shots:
            if shot["criteria"] != criteria:
                raise ValueError("All shots do not have the same criteria")

        formatted_shots = []
        for shot in shots:
            judgement = json.loads(shot["judgement"])
            formatted_shots.append(
                BinaryJudgeShot(
                    criteria=shot["criteria"],
                    reasoning=judgement["reasoning"],
                    score=judgement["score"],
                    thread=StringThread([tuple(turn) for turn in shot["thread"]]),
                )
            )

        return cls(
            grader_key=grader_key,
            model_key=model_key,
            client=client,
            criteria=criteria,
            shots=formatted_shots,
        )
