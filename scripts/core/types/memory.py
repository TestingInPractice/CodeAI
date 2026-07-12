"""CodeAI Platform — Memory Layer types."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID

from scripts.core.enums import MemoryType
from scripts.core.serialization import Serializable


@dataclass
class MemoryEntry(Serializable):
    """Single memory entry."""
    id: UUID
    type: MemoryType
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)
