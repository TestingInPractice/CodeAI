"""CodeAI Platform — Workflow Invariants.

Functions to check workflow invariants.
No business logic — only validation.
"""

from scripts.core.enums import PhaseStatus, TaskStatus
from scripts.core.workflow.state import PhaseState, TaskState, WorkflowState


def check_single_active_phase(state: WorkflowState) -> bool:
    """INV1: Only one phase can be active at a time.

    Returns:
        True if invariant holds.
    """
    active_phases = [
        p for p in state.phases
        if p.status == PhaseStatus.IN_PROGRESS
    ]
    return len(active_phases) <= 1


def check_phase_dependencies(state: WorkflowState, phase_id: str) -> bool:
    """INV2: Phase dependencies must be completed before starting.

    Args:
        state: Current workflow state.
        phase_id: ID of phase to check.

    Returns:
        True if all dependencies are completed.
    """
    phase = next((p for p in state.phases if p.id == phase_id), None)
    if phase is None:
        return False

    for dep_id in phase.depends_on:
        dep = next((p for p in state.phases if p.id == dep_id), None)
        if dep is None or dep.status != PhaseStatus.COMPLETED:
            return False

    return True


def check_completed_requires_all_tasks(phase: PhaseState) -> bool:
    """INV3: Completed phase requires all tasks completed.

    Args:
        phase: Phase to check.

    Returns:
        True if invariant holds.
    """
    if phase.status != PhaseStatus.COMPLETED:
        return True

    return all(t.status == TaskStatus.COMPLETED for t in phase.tasks)


def check_pending_no_completed_tasks(phase: PhaseState) -> bool:
    """INV4: Pending phase cannot have completed tasks.

    Args:
        phase: Phase to check.

    Returns:
        True if invariant holds.
    """
    if phase.status != PhaseStatus.PENDING:
        return True

    return not any(t.status == TaskStatus.COMPLETED for t in phase.tasks)


def check_task_cycle_after_decompose(state: WorkflowState, phase_id: str) -> bool:
    """INV5: task_cycle cannot start until decompose is completed.

    Args:
        state: Current workflow state.
        phase_id: ID of phase to check.

    Returns:
        True if invariant holds.
    """
    phase = next((p for p in state.phases if p.id == phase_id), None)
    if phase is None:
        return False

    # Find decompose phase
    decompose = next((p for p in state.phases if "decompose" in p.id.lower()), None)
    if decompose is None:
        return True  # No decompose phase, allow

    return decompose.status == PhaseStatus.COMPLETED


def check_complete_requires_all_phases(state: WorkflowState) -> bool:
    """INV6: Complete cannot happen until all phases are completed.

    Args:
        state: Current workflow state.

    Returns:
        True if invariant holds.
    """
    return all(
        p.status in (PhaseStatus.COMPLETED, PhaseStatus.FAILED)
        for p in state.phases
    )


def check_all_invariants(state: WorkflowState) -> list[str]:
    """Check all invariants and return violation messages.

    Args:
        state: Current workflow state.

    Returns:
        List of violation messages. Empty if all invariants hold.
    """
    violations = []

    if not check_single_active_phase(state):
        violations.append("INV1: Multiple active phases")

    for phase in state.phases:
        if phase.status == PhaseStatus.IN_PROGRESS:
            if not check_phase_dependencies(state, phase.id):
                violations.append(f"Phase '{phase.id}': unmet dependencies")

        if not check_completed_requires_all_tasks(phase):
            violations.append(f"Phase '{phase.id}': completed but tasks incomplete")

        if not check_pending_no_completed_tasks(phase):
            violations.append(f"Phase '{phase.id}': pending but has completed tasks")

    if not check_complete_requires_all_phases(state):
        violations.append("INV6: Not all phases completed")

    return violations
