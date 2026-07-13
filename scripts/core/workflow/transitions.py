"""CodeAI Platform — Workflow Transitions.

Description of allowed state transitions.
No execution — only definitions.
"""

from dataclasses import dataclass, field

from scripts.core.enums import PhaseStatus, TaskStatus, WorkflowStatus


@dataclass(frozen=True)
class Transition:
    """Definition of a state transition."""
    from_status: str
    to_status: str
    requires: list[str] = field(default_factory=list)
    guards: list[str] = field(default_factory=list)


# ── Phase Transitions ────────────────────────────────────────────

PHASE_TRANSITIONS: list[Transition] = [
    Transition(
        from_status=PhaseStatus.PENDING.value,
        to_status=PhaseStatus.IN_PROGRESS.value,
        requires=["all dependencies completed", "no active phase"],
        guards=["INV5: task_cycle cannot start until decompose is completed"],
    ),
    Transition(
        from_status=PhaseStatus.IN_PROGRESS.value,
        to_status=PhaseStatus.COMPLETED.value,
        requires=["all tasks completed", "judge_passed=True"],
        guards=["INV3: completed phase requires all tasks completed"],
    ),
    Transition(
        from_status=PhaseStatus.IN_PROGRESS.value,
        to_status=PhaseStatus.FAILED.value,
        requires=["judge_passed=False"],
        guards=[],
    ),
    Transition(
        from_status=PhaseStatus.IN_PROGRESS.value,
        to_status=PhaseStatus.PENDING.value,
        requires=["rollback reason provided"],
        guards=[],
    ),
    Transition(
        from_status=PhaseStatus.FAILED.value,
        to_status=PhaseStatus.PENDING.value,
        requires=["rollback reason provided"],
        guards=[],
    ),
]

# ── Task Transitions ─────────────────────────────────────────────

TASK_TRANSITIONS: list[Transition] = [
    Transition(
        from_status=TaskStatus.PENDING.value,
        to_status=TaskStatus.IN_PROGRESS.value,
        requires=["phase is active"],
        guards=[],
    ),
    Transition(
        from_status=TaskStatus.IN_PROGRESS.value,
        to_status=TaskStatus.COMPLETED.value,
        requires=[],
        guards=[],
    ),
    Transition(
        from_status=TaskStatus.IN_PROGRESS.value,
        to_status=TaskStatus.FAILED.value,
        requires=[],
        guards=[],
    ),
    Transition(
        from_status=TaskStatus.IN_PROGRESS.value,
        to_status=TaskStatus.PENDING.value,
        requires=["rollback"],
        guards=[],
    ),
]

# ── Workflow Transitions ─────────────────────────────────────────

WORKFLOW_TRANSITIONS: list[Transition] = [
    Transition(
        from_status=WorkflowStatus.IDLE.value,
        to_status=WorkflowStatus.RUNNING.value,
        requires=["first phase started"],
        guards=[],
    ),
    Transition(
        from_status=WorkflowStatus.RUNNING.value,
        to_status=WorkflowStatus.PAUSED.value,
        requires=[],
        guards=[],
    ),
    Transition(
        from_status=WorkflowStatus.RUNNING.value,
        to_status=WorkflowStatus.COMPLETED.value,
        requires=["all phases completed"],
        guards=["INV6: complete cannot happen until all phases are completed"],
    ),
    Transition(
        from_status=WorkflowStatus.RUNNING.value,
        to_status=WorkflowStatus.FAILED.value,
        requires=[],
        guards=[],
    ),
    Transition(
        from_status=WorkflowStatus.RUNNING.value,
        to_status=WorkflowStatus.ROLLING_BACK.value,
        requires=["rollback requested"],
        guards=[],
    ),
    Transition(
        from_status=WorkflowStatus.ROLLING_BACK.value,
        to_status=WorkflowStatus.RUNNING.value,
        requires=["rollback completed"],
        guards=[],
    ),
]


def get_valid_transitions(entity: str) -> list[Transition]:
    """Get all valid transitions for an entity type.

    Args:
        entity: One of 'phase', 'task', 'workflow'.

    Returns:
        List of Transition definitions.
    """
    if entity == "phase":
        return PHASE_TRANSITIONS
    elif entity == "task":
        return TASK_TRANSITIONS
    elif entity == "workflow":
        return WORKFLOW_TRANSITIONS
    return []


def can_transition(entity: str, from_status: str, to_status: str) -> bool:
    """Check if a transition is defined.

    Args:
        entity: One of 'phase', 'task', 'workflow'.
        from_status: Current status.
        to_status: Target status.

    Returns:
        True if transition is defined.
    """
    transitions = get_valid_transitions(entity)
    return any(
        t.from_status == from_status and t.to_status == to_status
        for t in transitions
    )
