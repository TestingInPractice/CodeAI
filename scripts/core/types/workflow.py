"""CodeAI Platform — Workflow Engine types."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from scripts.core.enums import PhaseStatus, TaskStatus
from scripts.core.serialization import Serializable


@dataclass
class Task(Serializable):
    """Task within a phase."""
    uuid: UUID
    title: str
    description: str = ""
    status: TaskStatus = TaskStatus.PENDING
    assigned_role: str = ""
    spec_ref: str = ""
    branch: str | None = None
    dependencies: list[UUID] = field(default_factory=list)


@dataclass
class Phase(Serializable):
    """Workflow phase."""
    id: str
    title: str
    description: str = ""
    status: PhaseStatus = PhaseStatus.PENDING
    depends_on: list[str] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)
    judge_passed: bool = False


@dataclass
class WorkflowState(Serializable):
    """Current state of the workflow pipeline."""
    current_phase: Phase | None = None
    phases: list[Phase] = field(default_factory=list)
    current_task: Task | None = None
    started_at: datetime | None = None
    updated_at: datetime | None = None
