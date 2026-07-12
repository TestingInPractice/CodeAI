"""CodeAI Platform — Common types (shared across subsystems)."""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from scripts.core.serialization import Serializable


@dataclass
class Artifact(Serializable):
    """Output artifact from OODA execution."""
    name: str
    path: Path
    type: str
    checksum: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Event(Serializable):
    """Event published to Event Bus."""
    name: str
    source: str
    event_id: UUID = field(default_factory=uuid4)
    correlation_id: UUID | None = None
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class RuntimeContext(Serializable):
    """Runtime context for current execution.

    Tracks project environment and OODA agent tracing.
    Workflow state (current_phase, current_task) lives in WorkflowState.
    """
    project_root: Path
    branch: str = ""
    iteration: int = 0
    variables: dict[str, Any] = field(default_factory=dict)
    current_agent: str = ""
    current_role: str = ""
    session_id: UUID | None = None
