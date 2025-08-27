from dataclasses import dataclass

from schemas.process_type import ProcessType


@dataclass(frozen=True)
class Process:
    pid: int
    command: str
    type: ProcessType
    priority: int | None
