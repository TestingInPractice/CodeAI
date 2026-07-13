"""CodeAI Platform — Transition Executor.

Validates and executes state transitions.
No business logic — only transition mechanics.
"""

from dataclasses import dataclass

from scripts.core.enums import PhaseStatus, TaskStatus, WorkflowStatus
from scripts.core.errors import WorkflowError
from scripts.core.workflow.invariants import (
    check_all_invariants,
    check_completed_requires_all_tasks,
    check_complete_requires_all_phases,
    check_phase_dependencies,
    check_single_active_phase,
)
from scripts.core.workflow.state import PhaseState, TaskState, WorkflowState
from scripts.core.workflow.transitions import Transition, can_transition


@dataclass(frozen=True)
class TransitionResult:
    """Result of a transition validation."""
    valid: bool
    errors: list[str]


class TransitionExecutor:
    """Validates state transitions without modifying state.

    Usage:
        executor = TransitionExecutor()
        result = executor.validate(state, "phase", "p1", "start")
        if result.valid:
            # Apply transition
        else:
            # Handle errors
    """

    def validate_phase_transition(
        self,
        state: WorkflowState,
        phase_id: str,
        to_status: str,
    ) -> TransitionResult:
        """Validate a phase transition.

        Args:
            state: Current workflow state.
            phase_id: ID of phase to transition.
            to_status: Target status.

        Returns:
            TransitionResult with validation status.
        """
        errors = []

        phase = next((p for p in state.phases if p.id == phase_id), None)
        if phase is None:
            return TransitionResult(
                valid=False,
                errors=[f"Phase '{phase_id}' not found"],
            )

        from_status = phase.status.value

        # Check if transition is defined
        if not can_transition("phase", from_status, to_status):
            errors.append(f"Invalid transition: {from_status} -> {to_status}")

        # Check guards based on target status
        if to_status == PhaseStatus.IN_PROGRESS.value:
            # Can only start if no active phase
            if not check_single_active_phase(state):
                errors.append("INV1: Another phase is already active")

            # Check dependencies
            if not check_phase_dependencies(state, phase_id):
                errors.append(f"Phase '{phase_id}': unmet dependencies")

        elif to_status == PhaseStatus.COMPLETED.value:
            # Check all tasks completed
            if not check_completed_requires_all_tasks(phase):
                incomplete = [t for t in phase.tasks if t.status != TaskStatus.COMPLETED]
                errors.append(f"INV3: {len(incomplete)} task(s) not completed")

        elif to_status == PhaseStatus.PENDING.value:
            # Rollback: only allowed from IN_PROGRESS or FAILED
            if phase.status not in (PhaseStatus.IN_PROGRESS, PhaseStatus.FAILED):
                errors.append(f"Cannot rollback from {phase.status.value}")

        return TransitionResult(
            valid=len(errors) == 0,
            errors=errors,
        )

    def validate_task_transition(
        self,
        state: WorkflowState,
        task_id: str,
        to_status: str,
    ) -> TransitionResult:
        """Validate a task transition.

        Args:
            state: Current workflow state.
            task_id: UUID of task to transition.
            to_status: Target status.

        Returns:
            TransitionResult with validation status.
        """
        errors = []

        if state.current_phase is None:
            return TransitionResult(
                valid=False,
                errors=["No active phase"],
            )

        task = next(
            (t for t in state.current_phase.tasks if t.uuid == task_id),
            None,
        )
        if task is None:
            return TransitionResult(
                valid=False,
                errors=[f"Task '{task_id}' not found in active phase"],
            )

        from_status = task.status.value

        # Check if transition is defined
        if not can_transition("task", from_status, to_status):
            errors.append(f"Invalid transition: {from_status} -> {to_status}")

        return TransitionResult(
            valid=len(errors) == 0,
            errors=errors,
        )

    def validate_workflow_transition(
        self,
        state: WorkflowState,
        to_status: str,
    ) -> TransitionResult:
        """Validate a workflow-level transition.

        Args:
            state: Current workflow state.
            to_status: Target status.

        Returns:
            TransitionResult with validation status.
        """
        errors = []

        from_status = state.workflow_status.value

        # Check if transition is defined
        if not can_transition("workflow", from_status, to_status):
            errors.append(f"Invalid transition: {from_status} -> {to_status}")

        # Check guards
        if to_status == WorkflowStatus.COMPLETED.value:
            if not check_complete_requires_all_phases(state):
                errors.append("INV6: Not all phases completed")

        return TransitionResult(
            valid=len(errors) == 0,
            errors=errors,
        )
