"""CodeAI Platform — Workflow Engine (state machine).

Manages the lifecycle of the workflow pipeline:
- Phases: pending → in_progress → completed / failed
- Transitions enforced by invariants (INV1-INV6)

Autonomous — no dependencies on persistence, OODA, Judge, or Spec Engine.
Persistence is handled externally via WorkflowRepository.
"""

from datetime import datetime

from scripts.core.enums import PhaseStatus, TaskStatus, WorkflowStatus
from scripts.core.errors import WorkflowError
from scripts.core.workflow.invariants import (
    check_completed_requires_all_tasks,
    check_complete_requires_all_phases,
    check_pending_no_completed_tasks,
    check_phase_dependencies,
    check_single_active_phase,
    check_task_cycle_after_decompose,
)
from scripts.core.workflow.state import PhaseState, TaskState, WorkflowState


class WorkflowEngine:
    """Workflow Engine — pipeline state machine.

    Manages the lifecycle of the workflow pipeline:
    - Phases: pending → in_progress → completed / failed
    - Transitions enforced by invariants (INV1-INV6)

    Public API (frozen):
        start(phase)
        next()
        complete(phase, judge_passed)
        rollback(phase, reason)

    Invariants:
        INV1: implement-spec-stage cannot be active without tasks
        INV2: Phase dependencies must be completed
        INV3: Completed phase requires all tasks completed
        INV4: Pending phase cannot have completed tasks
        INV5: task_cycle cannot start until decompose is completed
        INV6: Complete cannot happen until all phases are completed

    Guards (not invariants):
        G1: Only one phase can be active at a time (concurrency guard)

    Persistence:
        Handled externally via WorkflowRepository.
        WorkflowEngine does NOT know about JSON, SQLite, or filesystem.
    """

    def __init__(self, state: WorkflowState | None = None) -> None:
        """Initialize Workflow Engine.

        Args:
            state: Initial workflow state. If None, creates empty state.
        """
        self._state = state or WorkflowState()

    def start(self, phase: str) -> None:
        """Start a phase.

        Transitions phase from PENDING to IN_PROGRESS.
        Only one phase can be active at a time.
        All phase dependencies must be completed.

        Args:
            phase: Identifier of the phase to start.

        Raises:
            WorkflowError: If phase cannot be started.
        """
        # Check phase exists
        phase_obj = next((p for p in self._state.phases if p.id == phase), None)
        if phase_obj is None:
            raise WorkflowError(
                f"Phase '{phase}' not found",
                code="WF_PHASE_NOT_FOUND",
                recoverable=False,
                context={"phase_id": phase},
            )

        # Check status
        if phase_obj.status != PhaseStatus.PENDING:
            raise WorkflowError(
                f"Cannot start phase '{phase}': status is '{phase_obj.status.value}', expected 'pending'",
                code="WF_PHASE_WRONG_STATUS",
                recoverable=True,
                context={"phase_id": phase, "status": phase_obj.status.value},
            )

        # Check dependencies
        for dep_id in phase_obj.depends_on:
            dep = next((p for p in self._state.phases if p.id == dep_id), None)
            if dep is None:
                raise WorkflowError(
                    f"Dependency '{dep_id}' not found for phase '{phase}'",
                    code="WF_DEP_NOT_FOUND",
                    recoverable=False,
                    context={"phase_id": phase, "dependency": dep_id},
                )
            if dep.status != PhaseStatus.COMPLETED:
                raise WorkflowError(
                    f"Cannot start phase '{phase}': dependency '{dep_id}' is '{dep.status.value}', expected 'completed'",
                    code="WF_DEP_NOT_COMPLETED",
                    recoverable=True,
                    context={"phase_id": phase, "dependency": dep_id, "dep_status": dep.status.value},
                )

        # Check INV1: implement-spec-stage requires tasks
        if "implement" in phase.lower() and not phase_obj.tasks:
            raise WorkflowError(
                f"Cannot start phase '{phase}': implement-spec-stage requires tasks (INV1)",
                code="WF_INV1_NO_TASKS",
                recoverable=True,
                context={"phase_id": phase},
            )

        # Check INV5: task_cycle requires decompose completed
        if "task_cycle" in phase.lower():
            if not check_task_cycle_after_decompose(self._state, phase):
                raise WorkflowError(
                    f"Cannot start phase '{phase}': task_cycle requires decompose completed (INV5)",
                    code="WF_INV5_DECOMPOSE_PENDING",
                    recoverable=True,
                    context={"phase_id": phase},
                )

        # Check single active phase (concurrency guard)
        if self._state.current_phase is not None:
            raise WorkflowError(
                f"Cannot start phase '{phase}': phase '{self._state.current_phase.id}' is already active",
                code="WF_PHASE_ACTIVE",
                recoverable=True,
                context={"phase_id": phase, "active": self._state.current_phase.id},
            )

        phase_obj.status = PhaseStatus.IN_PROGRESS
        self._state.current_phase = phase_obj
        self._state.workflow_status = WorkflowStatus.RUNNING
        self._state.started_at = datetime.now()
        self._state.updated_at = datetime.now()

    def next(self) -> PhaseState | None:
        """Find the next ready phase.

        Returns the first PENDING phase with all dependencies completed.
        If a phase is currently IN_PROGRESS, returns None.

        Returns:
            Next ready PhaseState, or None.
        """
        if self._state.current_phase is not None:
            return None

        for phase in self._state.phases:
            if phase.status != PhaseStatus.PENDING:
                continue

            if check_phase_dependencies(self._state, phase.id):
                return phase

        return None

    def complete(self, phase: str, judge_passed: bool) -> None:
        """Complete a phase.

        Transitions phase from IN_PROGRESS to COMPLETED.
        Requires:
            - Phase must be IN_PROGRESS
            - All tasks must be COMPLETED (INV3)
            - judge_passed must be True

        Args:
            phase: Identifier of the phase to complete.
            judge_passed: Whether Judge Engine passed this phase.

        Raises:
            WorkflowError: If phase cannot be completed.
        """
        # Find phase
        phase_obj = next(
            (p for p in self._state.phases if p.id == phase), None
        )
        if phase_obj is None:
            raise WorkflowError(
                f"Phase '{phase}' not found",
                code="WF_PHASE_NOT_FOUND",
                recoverable=False,
                context={"phase_id": phase},
            )

        # Check status
        if phase_obj.status != PhaseStatus.IN_PROGRESS:
            raise WorkflowError(
                f"Cannot complete phase '{phase}': status is '{phase_obj.status.value}', expected 'in_progress'",
                code="WF_PHASE_WRONG_STATUS",
                recoverable=True,
                context={"phase_id": phase, "status": phase_obj.status.value},
            )

        # Check all tasks completed (INV3)
        incomplete_tasks = [
            t for t in phase_obj.tasks
            if t.status != TaskStatus.COMPLETED
        ]
        if incomplete_tasks:
            task_ids = [t.uuid for t in incomplete_tasks]
            raise WorkflowError(
                f"Cannot complete phase '{phase}': {len(incomplete_tasks)} task(s) not completed",
                code="WF_TASKS_INCOMPLETE",
                recoverable=True,
                context={"phase_id": phase, "incomplete_tasks": task_ids},
            )

        # Judge must pass
        if not judge_passed:
            raise WorkflowError(
                f"Cannot complete phase '{phase}': judge did not pass",
                code="WF_JUDGE_FAILED",
                recoverable=True,
                context={"phase_id": phase},
            )

        phase_obj.status = PhaseStatus.COMPLETED
        phase_obj.judge_passed = True
        self._state.current_phase = None
        self._state.updated_at = datetime.now()

        if check_complete_requires_all_phases(self._state):
            self._state.workflow_status = WorkflowStatus.COMPLETED

    def rollback(self, phase: str, reason: str) -> None:
        """Rollback a phase.

        Resets phase to PENDING, resets all tasks to PENDING.
        Pushes current state onto rollback_stack for history.

        Args:
            phase: Identifier of the phase to rollback.
            reason: Reason for rollback.

        Raises:
            WorkflowError: If phase cannot be rolled back.
        """
        # Find phase
        phase_obj = next(
            (p for p in self._state.phases if p.id == phase), None
        )
        if phase_obj is None:
            raise WorkflowError(
                f"Phase '{phase}' not found",
                code="WF_PHASE_NOT_FOUND",
                recoverable=False,
                context={"phase_id": phase},
            )

        # Check status
        if phase_obj.status not in (PhaseStatus.IN_PROGRESS, PhaseStatus.FAILED):
            raise WorkflowError(
                f"Cannot rollback phase '{phase}': status is '{phase_obj.status.value}', expected 'in_progress' or 'failed'",
                code="WF_PHASE_WRONG_STATUS",
                recoverable=True,
                context={"phase_id": phase, "status": phase_obj.status.value},
            )

        # Save snapshot before rollback
        tasks_before = [
            {"uuid": t.uuid, "title": t.title, "status": t.status.value}
            for t in phase_obj.tasks
        ]
        entry = {
            "phase_id": phase,
            "reason": reason,
            "phase_status": phase_obj.status.value,
            "tasks_before": tasks_before,
            "judge_passed": phase_obj.judge_passed,
        }
        self._state.rollback_stack.append(entry)

        # Reset phase
        phase_obj.status = PhaseStatus.PENDING
        phase_obj.judge_passed = False

        # Reset all tasks in phase
        for task in phase_obj.tasks:
            task.status = TaskStatus.PENDING

        # Check INV4: pending phase cannot have completed tasks (defensive guard)
        if not check_pending_no_completed_tasks(phase_obj):
            raise WorkflowError(
                f"INV4 violated: pending phase '{phase}' has completed tasks after rollback",
                code="WF_INV4_PENDING_COMPLETED_TASKS",
                recoverable=False,
                context={"phase_id": phase},
            )

        # Clear current state if this was the active phase
        if self._state.current_phase is not None and self._state.current_phase.id == phase:
            self._state.current_phase = None

        self._state.updated_at = datetime.now()
        self._state.workflow_status = WorkflowStatus.ROLLING_BACK

    @property
    def state(self) -> WorkflowState:
        """Return current workflow state (read-only access)."""
        return self._state
