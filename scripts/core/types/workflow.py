"""CodeAI Platform — Workflow Engine types."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID

from scripts.core.enums import PhaseStatus, TaskStatus, WorkflowStatus
from scripts.core.serialization import Serializable
from scripts.core.types.judge import Verdict


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


@dataclass(frozen=True)
class RollbackEntry(Serializable):
    """Snapshot of a rolled-back phase state.

    Stores everything needed to understand what was rolled back
    and why, and to restore the phase if needed.
    """
    phase_id: str
    reason: str
    phase_status: PhaseStatus
    tasks_before: list[dict[str, Any]]
    judge_passed: bool
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class WorkflowSnapshot(Serializable):
    """Full workflow state snapshot at a point in time.

    Captures the complete workflow context for persistence,
    debugging, and state recovery. Ready for JSON serialization.

    Note: context field uses lazy import to avoid circular dependency
    with ProjectContext (types/project.py imports types/workflow.py).
    """
    context: Any = None
    phase: Phase | None = None
    task: Task | None = None
    status: WorkflowStatus = WorkflowStatus.IDLE
    iteration: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    judge_verdict: Verdict | None = None
    rollback_stack: list[RollbackEntry] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any], strict: bool = False) -> WorkflowSnapshot:
        """Deserialize with lazy ProjectContext import.

        Overrides base from_dict to handle circular dependency:
        ProjectContext is imported lazily when needed.
        """
        from scripts.core.types.project import ProjectContext

        if not data:
            return cls()

        known_fields = {f.name for f in __import__("dataclasses").fields(cls)}
        unknown = set(data.keys()) - known_fields
        if unknown:
            import warnings
            msg = f"Unknown fields in WorkflowSnapshot.from_dict(): {unknown}"
            if strict:
                raise ValueError(msg)
            warnings.warn(msg, stacklevel=2)

        raw_context = data.get("context")
        context = ProjectContext.from_dict(raw_context) if raw_context else None

        raw_phase = data.get("phase")
        phase = Phase.from_dict(raw_phase) if raw_phase else None

        raw_task = data.get("task")
        task = Task.from_dict(raw_task) if raw_task else None

        raw_verdict = data.get("judge_verdict")
        verdict = Verdict.from_dict(raw_verdict) if raw_verdict else None

        raw_stack = data.get("rollback_stack", [])
        stack = [RollbackEntry.from_dict(e) for e in raw_stack]

        return cls(
            context=context,
            phase=phase,
            task=task,
            status=WorkflowStatus(data["status"]),
            iteration=data.get("iteration", 0),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now(),
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else datetime.now(),
            judge_verdict=verdict,
            rollback_stack=stack,
        )
