"""CodeAI Platform — Knowledge Layer types."""

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from scripts.core.enums import KnowledgeKind, KnowledgeType
from scripts.core.serialization import Serializable


@dataclass(frozen=True)
class Knowledge(Serializable):
    """Single knowledge item from Knowledge Layer."""
    id: UUID
    source: str
    kind: KnowledgeKind
    content: str
    score: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Context(Serializable):
    """Context retrieved from Knowledge Layer."""
    context_type: KnowledgeType
    items: list[Knowledge] = field(default_factory=list)
    summary: str = ""
