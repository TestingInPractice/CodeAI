"""CodeAI Platform — Workflow Snapshot.

Full serializable snapshot of workflow state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from scripts.core.enums import WorkflowStatus
from scripts.core.serialization import Serializable
from scripts.core.workflow.state import (
    JudgeState,
    PhaseState,
    TaskState,
    WorkflowState,
)


@dataclass
class RollbackEntry(Serializable):
    """Record of a rollback operation."""
    phase_id: str
    reason: str
    phase_status: str
    tasks_before: list[dict[str, Any]]
    judge_passed: bool
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class WorkflowSnapshot(Serializable):
    """Full workflow state snapshot at a point in time.

    Captures the complete workflow context for persistence,
    debugging, and state recovery.
    """
    state: WorkflowState = field(default_factory=WorkflowState)
    status: WorkflowStatus = WorkflowStatus.IDLE
    iteration: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    rollback_stack: list[RollbackEntry] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "state": self.state.to_dict() if self.state else None,
            "status": self.status.value,
            "iteration": self.iteration,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "rollback_stack": [e.to_dict() for e in self.rollback_stack],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WorkflowSnapshot:
        """Deserialize from dictionary."""
        if not data:
            return cls()

        state_data = data.get("state")
        state = WorkflowState.from_dict(state_data) if state_data else WorkflowState()

        rollback_data = data.get("rollback_stack", [])
        rollback_stack = [RollbackEntry.from_dict(e) for e in rollback_data]

        return cls(
            state=state,
            status=WorkflowStatus(data.get("status", "idle")),
            iteration=data.get("iteration", 0),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now(),
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else datetime.now(),
            rollback_stack=rollback_stack,
        )
