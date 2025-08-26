import textwrap
from pydantic import BaseModel
from typing import NamedTuple, TypedDict
from adaptive_harmony import StringThread, StringTurn

from adaptive_harmony.core.structured_output import render_pydantic_model
from adaptive_harmony.core.utils import stringify_thread
from adaptive_harmony.graders.utils import (
    validate_thread_last_assistant,
    separate_context_from_last_user_turn,
)
from adaptive_harmony.graders.range_judge.types import ReasonedScore, PromptBuildingBlocks


class RangeJudgeShot(BaseModel):
    thread: StringThread
    reasoning: str
    score: int

    class Config:
        arbitrary_types_allowed = True


RangeShots = TypedDict("RangeShots", {"reasoning": list[StringTurn], "scoring": list[StringTurn]})


class SubrangeExpectations(NamedTuple):
    subrange: tuple[int, int]
    expectation: str


COMMON_EVALUATION_PROMPT = """You are an expert evaluator of AI-user interactions.
You will be given:
- CONTEXT : previous conversation history, might be empty
- LAST USER INPUT : the latest input from the user
- LAST ASSISTANT OUTPUT : the latest output/answer from the AI
- CRITERIA: the evaluation criteria
- EVALUATION STEPS : logical reasoning steps to take when evaluating the interaction against the CRITERIA
"""


def get_common_user_template(
    context: str, last_user_input: str, assistant_answer: str, criteria: str, evaluation_steps: str
):
    return f"""CONTEXT\n{context}\n
LAST USER INPUT\n{last_user_input}\n
LAST ASSISTANT OUTPUT\n{assistant_answer}\n
CRITERIA\n{criteria}\n
EVALUATION STEPS\n{evaluation_steps}"""


class RangeScorerTemplates:
    @staticmethod
    def get_evaluation_steps(criteria: str) -> StringThread:
        return (
            StringThread()
            .system(
                textwrap.dedent(
                    """\
                    Given an evaluation criteria which outlines how you should judge an interaction between an AI and a user, generate 3-4 concise evaluation steps based on the criteria below.

                    Return your evaluation steps as a numbered list of evaluation steps, such as:

                    Steps list:
                    1. First step
                    2. Second step
                    3. Third step
                    etc.

                    Focus on specific, concise steps that can be objectively followed based on the evaluation criteria provided.
                    Don't return any preamble or explanation, only the list.
                    """
                )
            )
            .user(f"Evaluation Criteria:\n{criteria}\nSteps list:\n")
        )

    @staticmethod
    def get_json_reasoned_score_user(
        context: str, last_user_input: str, assistant_answer: str, criteria: str, evaluation_steps: str
    ):
        common = get_common_user_template(context, last_user_input, assistant_answer, criteria, evaluation_steps)
        return f"{common}\n\nJSON OUTPUT:\n"

    @staticmethod
    def get_json_reasoned_score(
        context: str,
        last_user_input: str,
        assistant_answer: str,
        criteria: str,
        evaluation_steps: str,
        score_range: tuple[int, int],
        json_schema: str,
        subrange_expectations: list[SubrangeExpectations] | None = None,
        shots: list[StringTurn] | None = None,
    ) -> StringThread:
        if subrange_expectations:
            subrange_expectations_str = "which should correspond to:\n" + "\n".join(
                [
                    f"{sub.subrange[0]} - {sub.subrange[1]}: {sub.expectation}"
                    for i, sub in enumerate(subrange_expectations)
                ]
            )
        else:
            subrange_expectations_str = f"where {score_range[1]} indicates strong alignment with the criteria and {score_range[0]} indicates no alignment."

        system_prompt = (
            COMMON_EVALUATION_PROMPT
            + f"""
Your task is to evaluate and score the ASSISTANT ANSWER, strictly following the provided EVALUATION STEPS to evaluate the CRITERIA.
You must respond with a valid JSON object that matches the following schema:

{json_schema}

Your reasoning for the score:
- Be specific and grounded in the EVALUATION STEPS
- Uphold the evaluation objective and nuances expressed in the CRITERIA as the main target
- Mention specific details, strenghts or shortcomings of the answer, referencing relevant details from the input
- Be concise, clear, and focused on the evaluation logic.
- **Never** quote the score itself in the explanation; focus only on reasoning through the evaluation steps

Your final evaluation score must be strictly within the range of [{score_range[0]} - {score_range[1]}], {subrange_expectations_str}

Return only the JSON object after the OUTPUT header, no other text, preamble or explanation.
"""
        )

        user_prompt = RangeScorerTemplates.get_json_reasoned_score_user(
            context, last_user_input, assistant_answer, criteria, evaluation_steps
        )

        shots = shots or []
        return StringThread([("system", system_prompt)] + shots + [("user", user_prompt)])

    @staticmethod
    def get_up_to_score_user(
        context: str, last_user_input: str, assistant_answer: str, criteria: str, evaluation_steps: str, reasoning: str
    ) -> str:
        common = get_common_user_template(context, last_user_input, assistant_answer, criteria, evaluation_steps)
        return f"{common}\n\nREASONING\n{reasoning}\n\nSCORE: "

    @staticmethod
    def get_up_to_score(
        context: str,
        last_user_input: str,
        assistant_answer: str,
        criteria: str,
        evaluation_steps: str,
        score_range: tuple[int, int],
        reasoning: str,
        subrange_expectations: list[SubrangeExpectations] | None = None,
        shots: list[StringTurn] | None = None,
    ) -> StringThread:
        if subrange_expectations:
            subrange_expectations_str = "which should correspond to:\n" + "\n".join(
                [
                    f"{sub.subrange[0]} - {sub.subrange[1]}: {sub.expectation}"
                    for i, sub in enumerate(subrange_expectations)
                ]
            )
        else:
            subrange_expectations_str = f"where {score_range[1]} indicates strong alignment with the evaluation steps and {score_range[0]} indicates no alignment."

        system_prompt = COMMON_EVALUATION_PROMPT + textwrap.dedent(
            f"""\
                - REASONING : the reasoning for the score, following the process described by the EVALUATION STEPS to assess the presented interaction against the CRITERIA

                You must respond only with a score, based on the original CRITERIA and the REASONING for the sample,
                which should justify your score for the sample.

                Your final evaluation score must be strictly within the range of [{score_range[0]} - {score_range[1]}], {subrange_expectations_str}

                Return only the integer score, nothing before or after.
                """
        )
        user_prompt = RangeScorerTemplates.get_up_to_score_user(
            context, last_user_input, assistant_answer, criteria, evaluation_steps, reasoning
        )

        shots = shots or []
        return StringThread([("system", system_prompt)] + shots + [("user", user_prompt)])


def get_prompt_building_blocks(thread: StringThread) -> PromptBuildingBlocks:
    validate_thread_last_assistant(thread)
    context_turns, last_user_turn = separate_context_from_last_user_turn(thread)
    context_str = stringify_thread(StringThread(context_turns))
    last_assistant_turn = thread.last_content()
    assert last_user_turn, "There must be at least one user turn"
    return PromptBuildingBlocks(
        context=context_str, last_user_turn=last_user_turn, last_assistant_turn=last_assistant_turn
    )


def create_shots(criteria: str, evaluation_steps: str, shots: list[RangeJudgeShot]) -> RangeShots:
    reasoning_shots: list[StringTurn] = []
    scoring_shots: list[StringTurn] = []
    for shot in shots:
        prompt_components = get_prompt_building_blocks(shot.thread)
        reasoning_shots.extend(
            [
                StringTurn(
                    role="user",
                    content=RangeScorerTemplates.get_json_reasoned_score_user(
                        prompt_components.context,
                        prompt_components.last_user_turn,
                        prompt_components.last_assistant_turn,
                        criteria,
                        evaluation_steps,
                    ),
                ),
                StringTurn(
                    role="assistant",
                    content=render_pydantic_model(ReasonedScore(reasoning=shot.reasoning, score=shot.score)),
                ),
            ]
        )
        scoring_shots.extend(
            [
                StringTurn(
                    role="user",
                    content=RangeScorerTemplates.get_up_to_score_user(
                        prompt_components.context,
                        prompt_components.last_user_turn,
                        prompt_components.last_assistant_turn,
                        criteria,
                        evaluation_steps,
                        shot.reasoning,
                    ),
                ),
                StringTurn(role="assistant", content=str(shot.score)),
            ]
        )

    return {"reasoning": reasoning_shots, "scoring": scoring_shots}
