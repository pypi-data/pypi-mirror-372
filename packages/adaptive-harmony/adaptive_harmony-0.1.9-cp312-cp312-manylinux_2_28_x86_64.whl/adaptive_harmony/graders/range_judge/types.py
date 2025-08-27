from pydantic import BaseModel, Field


class ReasonedScore(BaseModel):
    reasoning: str = Field(description="String reasoning to support the rationale behind the score")
    score: int = Field(description="Integer score for the interaction, must be within the specified score range")


class PromptBuildingBlocks(BaseModel):
    context: str
    last_user_turn: str
    last_assistant_turn: str
