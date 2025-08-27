from adaptive_harmony.adaptive_harmony import HarmonyClient
import pysbd
from typing import Literal
from pydantic import BaseModel, Field


from adaptive_harmony import InferenceModel, StringThread
from adaptive_harmony.core.structured_output import JsonParseError
from adaptive_harmony.core.utils import stringify_thread
from adaptive_harmony.graders import Grader, Grade
from adaptive_harmony.graders.exceptions import IgnoreScoreException
from adaptive_harmony.graders.faithfulness_judge.prompts import SYSTEM, USER
from adaptive_harmony.graders.utils import (
    validate_thread_last_assistant,
    separate_context_from_last_user_turn,
    sample_score_distribution,
    SuccessJudgeLog,
    FailedJudgeLog,
)
from adaptive_harmony.logging_table import Table


class SingleStatementFaithfulnessJudgeOutput(BaseModel):
    statement_idx: int = Field(description="The original index of the sentence being scored")
    reasoning: str = Field(description="Reasoning to support the rationale behind the score")
    score: Literal["1", "0"] = Field(
        description="The score of the sample, 1 if the statement is fully supported by the context, 0 if it is not"
    )


class FaithfulnessScorerOutput(BaseModel):
    all_statements_scoring: list[SingleStatementFaithfulnessJudgeOutput] = Field(
        description="An array of objects, each analyzing a single statement from the original list of statements"
    )


SupportedLanguages = Literal[
    "en",
    "hi",
    "mr",
    "zh",
    "es",
    "am",
    "ar",
    "hy",
    "bg",
    "ur",
    "ru",
    "pl",
    "fa",
    "nl",
    "da",
    "fr",
    "my",
    "el",
    "it",
    "ja",
    "de",
    "kk",
    "sk",
]


class FaithfulnessGrader(Grader):
    """
    Scores each sentence in the last assistant turn as fully supported by the context or not (1 or 0).
    The context is the rest of the thread, excluding the system prompt.
    The final score is the average of each sentence.
    Requires an input language code to split the sentences.
    """

    def __init__(
        self,
        model_key: str,
        client: HarmonyClient,
        tp: int | None = None,
        kv_cache_len: int | None = None,
        language: SupportedLanguages = "en",
        grader_key: str = "faithfulness_judge",
        grader_id: str | None = None,
    ):
        super().__init__(grader_key)
        self._logs: list[SuccessJudgeLog | FailedJudgeLog] = []  # already created in super, this is for typing
        self.model_key = model_key
        self.client = client
        self.tp = tp
        self.kv_cache_len = kv_cache_len
        self.judge_is_spawned = False
        self.model: InferenceModel
        self.language = language
        self.sentence_splitter = pysbd.Segmenter(language=language)
        self.grader_id_or_key = grader_id or grader_key

    async def setup(self) -> None:
        model = (
            self.client.model(self.model_key, self.kv_cache_len)
            if self.kv_cache_len is not None
            else self.client.model(self.model_key)
        )
        if self.tp is not None:
            model = model.tp(self.tp)
        self.model = await model.spawn_inference(self.grader_key)
        self.judge_is_spawned = True

    async def teardown(self) -> None:
        if self.judge_is_spawned:
            await self.model.dealloc()
        self.judge_is_spawned = False

    async def grade(self, sample: StringThread) -> Grade:
        if self.model is None:
            raise RuntimeError("Model not initialized, run grader.setup() before grading")

        # Split response into sentences
        validate_thread_last_assistant(sample)
        # Separate conversation context from last user turn
        context_turns, user_question = separate_context_from_last_user_turn(sample)
        completion = sample.last_content()
        split_sentences = self.sentence_splitter.segment(completion)
        sentences = [f"{i}: {sentence.strip()}" for i, sentence in enumerate(split_sentences) if sentence.strip()]
        sentences_judge_str = "\n".join(sentences)

        # Build prompt
        context_str = stringify_thread(StringThread(context_turns))
        judge_thread = (
            StringThread()
            .system(SYSTEM.format(json_schema=self.model.render_schema(FaithfulnessScorerOutput)))
            .user(USER.format(context=context_str, user_question=user_question, sentences=sentences_judge_str))
        )
        judge_str_prompt = stringify_thread(judge_thread, sep=f"\n\n{'-'*10}\n\n")
        # Generate response
        try:
            _, parsed_response = await self.model.temperature(0.0).generate_and_validate(
                judge_thread, FaithfulnessScorerOutput
            )
        except JsonParseError as e:
            self.add_log({"prompt": judge_str_prompt, "error": f"{str(e)}\n\nCOMPLETION:\n{e.completion}"})
            raise
        except Exception as e:
            self.add_log({"prompt": judge_str_prompt, "error": str(e)})
            raise

        # Raise error if judge failed to judge any sentence
        n_judged_sentences = len(parsed_response.all_statements_scoring)
        if n_judged_sentences != len(sentences):
            raise IgnoreScoreException(
                f"Number of sentences in the response ({n_judged_sentences})"
                f"does not match the number of sentences in the input ({len(sentences)})"
            )
        # Calculate avg score
        score = round(
            sum([float(judgement.score) for judgement in parsed_response.all_statements_scoring]) / n_judged_sentences,
            3,
        )
        # Add per sentence reasoning and score metadata
        metadata = [
            dict(
                sentence_idx=judgement.statement_idx,
                reasoning=judgement.reasoning,
                score=judgement.score,
            )
            for judgement in parsed_response.all_statements_scoring
        ]
        merged_reasoning_traces = "\n-".join(
            [judgement.reasoning for judgement in parsed_response.all_statements_scoring]
        )
        self.add_log({"score": score, "prompt": judge_str_prompt, "reasoning": merged_reasoning_traces})

        return Grade(value=score, grader_key=self.grader_id_or_key, reasoning=merged_reasoning_traces)

    def add_log(self, log: SuccessJudgeLog | FailedJudgeLog) -> None:
        self._logs.append(log)

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
