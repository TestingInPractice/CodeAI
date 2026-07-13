"""CodeAI Platform — OODA Runtime State.

Tracks the state of OODA cycle execution for resume/interrupt support.
"""

from enum import Enum
from uuid import UUID

from scripts.core.serialization import Serializable


class OODAStatus(str, Enum):
    """Status of OODA execution."""
    IDLE = "idle"
    OBSERVE = "observe"
    ORIENT = "orient"
    DECIDE = "decide"
    ACT = "act"
    COMPLETED = "completed"
    INTERRUPTED = "interrupted"
    FAILED = "failed"


class OODARuntimeState(Serializable):
    """Runtime state for a single OODA cycle execution.

    Tracks which step the cycle is on, enabling resume after interruption.
    """

    def __init__(self) -> None:
        self.task_id: UUID | None = None
        self.status: OODAStatus = OODAStatus.IDLE
        self.current_step: str = ""
        self.error: str | None = None

    def start(self, task_id: UUID) -> None:
        """Mark cycle as started."""
        self.task_id = task_id
        self.status = OODAStatus.OBSERVE
        self.current_step = "observe"
        self.error = None

    def advance(self, step: str) -> None:
        """Advance to next step."""
        self.current_step = step
        self.status = OODAStatus(step)

    def complete(self) -> None:
        """Mark cycle as completed."""
        self.status = OODAStatus.COMPLETED
        self.current_step = ""

    def interrupt(self) -> None:
        """Mark cycle as interrupted."""
        self.status = OODAStatus.INTERRUPTED

    def fail(self, error: str) -> None:
        """Mark cycle as failed."""
        self.status = OODAStatus.FAILED
        self.error = error

    def is_running(self) -> bool:
        """Check if cycle is currently running."""
        return self.status in (
            OODAStatus.OBSERVE,
            OODAStatus.ORIENT,
            OODAStatus.DECIDE,
            OODAStatus.ACT,
        )

    def can_resume(self) -> bool:
        """Check if cycle can be resumed."""
        return self.status == OODAStatus.INTERRUPTED
