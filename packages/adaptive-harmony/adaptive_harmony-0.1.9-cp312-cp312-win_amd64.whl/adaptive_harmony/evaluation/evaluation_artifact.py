from typing import List, Self
import uuid
import logging
from adaptive_harmony import (
    EvalSample,
)
from adaptive_harmony.adaptive_harmony import EvaluationArtifactBase
from adaptive_harmony.runtime.context import RecipeContext

logger = logging.getLogger(__name__)


class EvaluationArtifact:
    def __init__(self, name: str, ctx: RecipeContext) -> None:
        self._base = EvaluationArtifactBase(name, str(uuid.uuid4()))
        self.ctx = ctx
        self.ctx.job.register_artifact(self._base.artifact)

    @property
    def id(self) -> str:
        return self._base.id

    @property
    def name(self) -> str:
        return self._base.name

    @property
    def kind(self) -> str:
        return self._base.kind

    @property
    def uri(self) -> str:
        return self._base.uri

    def add_samples(self, samples: List[EvalSample]) -> Self:
        """Add evaluation samples to this artifact.

        Args:
            samples: List of evaluation samples to add

        Returns:
            Self for method chaining

        Raises:
            ValueError: If samples list is empty
            Exception: If serialization or storage fails
        """
        if not samples:
            raise ValueError("Cannot add empty samples list")

        try:
            samples_json = self._base.samples_to_adaptive_json(samples)
            for json_str in samples_json:
                self.ctx.file_storage.append(json_str + "\n", self.uri)
            logger.debug(f"Added {len(samples)} samples to artifact {self.id}")
        except Exception as e:
            logger.error(f"Failed to add samples to artifact {self.id}: {e}")
            raise

        return self

    def __repr__(self):
        return f"EvaluationArtifact(id={self.id}, name={self.name}, kind={self.kind}, uri={self.uri})"
