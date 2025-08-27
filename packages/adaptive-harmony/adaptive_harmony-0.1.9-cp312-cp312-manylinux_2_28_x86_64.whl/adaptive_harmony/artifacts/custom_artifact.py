import uuid
from adaptive_harmony.adaptive_harmony import (
    JobArtifact,
)
from adaptive_harmony.runtime.context import RecipeContext


class CustomArtifact:
    def __init__(self, name: str, ctx: RecipeContext, file: str | None = None) -> None:
        self._base = JobArtifact(
            id=str(uuid.uuid4()),
            name=name,
            kind="custom",
            uri=f"file://{file}" if file else None,
        )
        self.ctx = ctx
        self.ctx.job.register_artifact(self._base)

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

    def write_file(self, file_path: str) -> None:
        self.ctx.file_storage.write(file_path, self.uri)

    def append_file(self, file_path: str) -> None:
        self.ctx.file_storage.append(file_path, self.uri)

    def read_file(self, file_path: str) -> bytes:
        return self.ctx.file_storage.read(file_path)

    def __repr__(self):
        return f"EvaluationArtifact(id={self.id}, name={self.name}, kind={self.kind}, uri={self.uri})"
