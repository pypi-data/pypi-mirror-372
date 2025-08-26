from dataclasses import dataclass, field


@dataclass
class ResponseAccumulator:
    total_num_chunks: int = 0
    chunks_received: list[str] = field(default_factory=list)

    def add_chunk(self, chunk: str):
        self.chunks_received.append(chunk)

    def is_complete(self) -> bool:
        return len(self.chunks_received) == self.total_num_chunks

    def get_full_data(self) -> str | None:
        if self.is_complete():
            return "".join(self.chunks_received)
        return None
