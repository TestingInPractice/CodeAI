"""CodeAI Platform — Workflow State Model.

Internal state representation for Workflow Engine.
No business logic — only data structures.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID

from scripts.core.enums import PhaseStatus, TaskStatus, VerdictStatus, WorkflowStatus
from scripts.core.serialization import Serializable


@dataclass
class TaskState(Serializable):
    """State of a single task."""
    uuid: UUID
    title: str
    status: TaskStatus = TaskStatus.PENDING
    assigned_role: str = ""
    spec_ref: str = ""
    branch: str | None = None
    dependencies: list[UUID] = field(default_factory=list)


@dataclass
class PhaseState(Serializable):
    """State of a single phase."""
    id: str
    title: str
    status: PhaseStatus = PhaseStatus.PENDING
    depends_on: list[str] = field(default_factory=list)
    tasks: list[TaskState] = field(default_factory=list)
    judge_passed: bool = False


@dataclass
class JudgeState(Serializable):
    """State of the Judge Engine evaluation."""
    overall: VerdictStatus | None = None
    scores: dict[str, float] = field(default_factory=dict)
    failures: list[str] = field(default_factory=list)
    confidence: float = 0.0


@dataclass
class WorkflowState(Serializable):
    """Complete workflow state at a point in time.

    This is the internal state model for Workflow Engine.
    No business logic — only data structures.
    """
    current_phase: PhaseState | None = None
    current_task: TaskState | None = None
    phases: list[PhaseState] = field(default_factory=list)
    workflow_status: WorkflowStatus = WorkflowStatus.IDLE
    judge_status: JudgeState | None = None
    iteration: int = 0
    rollback_stack: list[dict[str, Any]] = field(default_factory=list)
    started_at: datetime | None = None
    updated_at: datetime | None = None
