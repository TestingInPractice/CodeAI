"""CodeAI Platform — Data Types and Interfaces.

Re-exports all types for backward-compatible imports:
    from scripts.core.types import Task, Phase, Verdict, ...
"""

from scripts.core.enums import (
    EventType,
    KnowledgeKind,
    KnowledgeType,
    MemoryType,
    PhaseStatus,
    Priority,
    RouteTarget,
    TaskStatus,
    VerdictStatus,
    WorkflowStatus,
)
from scripts.core.types.common import Artifact, Event, RuntimeContext
from scripts.core.types.judge import (
    Rubric,
    RubricCriterion,
    RouteAction,
    Score,
    Verdict,
)
from scripts.core.types.knowledge import Context, Knowledge
from scripts.core.types.memory import MemoryEntry
from scripts.core.types.ooda import OODAResult
from scripts.core.types.project import ProjectContext
from scripts.core.types.spec import (
    AC,
    APIContract,
    DataModel,
    FieldDefinition,
    Requirement,
    Scope,
    StructuredSpec,
    ValidationResult,
)
from scripts.core.types.workflow import (
    JudgeState,
    Phase,
    PhaseState,
    RollbackEntry,
    Task,
    TaskState,
    WorkflowSnapshot,
    WorkflowState,
)

__all__ = [
    # enums
    "EventType",
    "KnowledgeKind",
    "KnowledgeType",
    "MemoryType",
    "PhaseStatus",
    "Priority",
    "RouteTarget",
    "TaskStatus",
    "VerdictStatus",
    "WorkflowStatus",
    # common
    "Artifact",
    "Event",
    "RuntimeContext",
    # spec
    "Requirement",
    "AC",
    "FieldDefinition",
    "DataModel",
    "APIContract",
    "Scope",
    "StructuredSpec",
    "ValidationResult",
    # workflow
    "Task",
    "Phase",
    "WorkflowState",
    "PhaseState",
    "TaskState",
    "JudgeState",
    "RollbackEntry",
    "WorkflowSnapshot",
    # ooda
    "OODAResult",
    # knowledge
    "Knowledge",
    "Context",
    # memory
    "MemoryEntry",
    # judge
    "Verdict",
    "Score",
    "RouteAction",
    "RubricCriterion",
    "Rubric",
    # project
    "ProjectContext",
]
