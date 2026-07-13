"""CodeAI Platform — Workflow Engine internal models.

State, transitions, invariants, snapshot, persistence, and transition execution.
"""

from scripts.core.workflow.invariants import (
    check_all_invariants,
    check_completed_requires_all_tasks,
    check_complete_requires_all_phases,
    check_pending_no_completed_tasks,
    check_phase_dependencies,
    check_single_active_phase,
    check_task_cycle_after_decompose,
)
from scripts.core.workflow.snapshot import RollbackEntry, WorkflowSnapshot
from scripts.core.workflow.state import (
    JudgeState,
    PhaseState,
    TaskState,
    WorkflowState,
)
from scripts.core.workflow.transition_executor import TransitionExecutor, TransitionResult
from scripts.core.workflow.transitions import (
    PHASE_TRANSITIONS,
    TASK_TRANSITIONS,
    WORKFLOW_TRANSITIONS,
    Transition,
    can_transition,
    get_valid_transitions,
)
from scripts.core.workflow.workflow_repository import WorkflowRepository

__all__ = [
    # state
    "TaskState",
    "PhaseState",
    "JudgeState",
    "WorkflowState",
    # transitions
    "Transition",
    "PHASE_TRANSITIONS",
    "TASK_TRANSITIONS",
    "WORKFLOW_TRANSITIONS",
    "get_valid_transitions",
    "can_transition",
    # transition executor
    "TransitionExecutor",
    "TransitionResult",
    # invariants
    "check_single_active_phase",
    "check_phase_dependencies",
    "check_completed_requires_all_tasks",
    "check_pending_no_completed_tasks",
    "check_task_cycle_after_decompose",
    "check_complete_requires_all_phases",
    "check_all_invariants",
    # snapshot
    "RollbackEntry",
    "WorkflowSnapshot",
    # persistence
    "WorkflowRepository",
]
