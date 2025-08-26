from pydantic import BaseModel
import json
import re
from typing import Self, Literal

from adaptive_harmony import StringThread


class InputConfig(BaseModel):
    @classmethod
    def load_from_file(cls, json_file) -> Self:
        with open(json_file, "r") as f:
            data = json.load(f)
        return cls.model_validate(data)


# Helper classes for inputs
class AdaptiveDataset(BaseModel):
    file: str


class ChatMessage(BaseModel):
    role: str
    content: str
    metadata: dict | None


class CustomJudgeExample(BaseModel):
    input: list[ChatMessage]
    reasoning: str | None
    output: str
    is_pass: bool


class CustomJudge(BaseModel):
    type: Literal["Judge"] = "Judge"
    model_uri: str
    criteria: str
    examples: list[CustomJudgeExample]


class PrebuiltJudge(BaseModel):
    type: Literal["Prebuilt"] = "Prebuilt"
    model_uri: str
    prebuilt_config_key: str


class RemoteRewardEndpoint(BaseModel):
    type: Literal["Remote"] = "Remote"
    url: str
    version: str
    description: str


class GraderConfig(BaseModel):
    grader_id: str
    key: str
    metric_id: str
    name: str
    config: CustomJudge | PrebuiltJudge | RemoteRewardEndpoint


class AdaptiveGrader(BaseModel):
    grader: GraderConfig

    def __hash__(self):
        return hash(self.grader.grader_id)


class AdaptiveModel(BaseModel):
    path: str
    model_key: str | None = None

    def __hash__(self):
        return hash((self.path, self.model_key))

    def __repr__(self) -> str:

        # Redact api_key in the path if present, show only last 3 chars
        def redact_api_key(match):
            key = match.group(2)
            if len(key) > 3:
                redacted = "<REDACTED>" + key[-3:]
            else:
                redacted = "<REDACTED>"
            return f"{match.group(1)}{redacted}"

        redacted_path = re.sub(r"(api_key=)([^&]+)", redact_api_key, self.path)
        return f"AdaptiveModel(path='{redacted_path}')"
