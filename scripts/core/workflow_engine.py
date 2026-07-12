"""CodeAI Platform — Workflow Engine (stub)."""

from scripts.core.types import Phase


class WorkflowEngine:
    """Workflow Engine — pipeline state management.

    Responsibilities:
        - Manage state.json (current phase, status, judge verdict)
        - Control transitions between phases
        - Enforce invariants (INV1-INV6)
        - Entry/exit gates

    API:
        start(phase) -> None
        next() -> Phase | None
        complete(phase, judge_passed) -> None
        rollback(phase, reason) -> None
    """

    def start(self, phase: str) -> None:
        """Start a phase.

        Args:
            phase: Phase ID to start.
        """
        raise NotImplementedError

    def next(self) -> Phase | None:
        """Find next ready phase (pending, all deps completed).

        Returns:
            Next ready Phase or None.
        """
        raise NotImplementedError

    def complete(self, phase: str, judge_passed: bool) -> None:
        """Complete a phase (requires judge_passed=True).

        Args:
            phase: Phase ID to complete.
            judge_passed: Whether judge passed for this phase.
        """
        raise NotImplementedError

    def rollback(self, phase: str, reason: str) -> None:
        """Rollback a phase (by Judge Engine decision).

        Args:
            phase: Phase ID to rollback.
            reason: Reason for rollback.
        """
        raise NotImplementedError
