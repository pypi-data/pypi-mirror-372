from typing import Any, TypeVar, Generic
from pydantic import BaseModel as PydanticBaseModel, model_validator, ConfigDict


class BaseModel(PydanticBaseModel):
    model_config = ConfigDict(extra="forbid")


MetadataType = TypeVar("MetadataType", bound=BaseModel)


class Turn(BaseModel):
    """@public"""

    role: str
    content: str


class Request(BaseModel):
    """@public"""

    turns: list[Turn]
    metadata: dict[str, Any] | None = None
    id: int | None = None


class Response(BaseModel):
    """@public"""

    reward: float
    metadata: dict[str, Any]
    id: int | None = None


class MetadataValidationResponse(BaseModel):
    """@public"""

    is_valid: bool
    error_message: str | None = None


class ServerInfo(BaseModel):
    """@public"""

    version: str
    name: str
    description: str
