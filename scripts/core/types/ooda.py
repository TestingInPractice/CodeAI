"""CodeAI Platform — OODA Runtime types."""

from dataclasses import dataclass, field
from uuid import UUID

from scripts.core.serialization import Serializable
from scripts.core.types.common import Artifact


@dataclass
class OODAResult(Serializable):
    """Result of OODA cycle execution."""
    task_id: UUID
    step: str
    success: bool
    outputs: list[Artifact] = field(default_factory=list)
    summary: str = ""
