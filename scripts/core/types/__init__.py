"""CodeAI Platform — Data Types and Interfaces.

Re-exports all types for backward-compatible imports:
    from scripts.core.types import Task, Phase, Verdict, ...
"""

from scripts.core.enums import (
    KnowledgeKind,
    KnowledgeType,
    MemoryType,
    PhaseStatus,
    Priority,
    RouteTarget,
    TaskStatus,
    VerdictStatus,
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
    Requirement,
    Scope,
    StructuredSpec,
    ValidationResult,
)
from scripts.core.types.workflow import Phase, Task, WorkflowState

__all__ = [
    # enums
    "KnowledgeKind",
    "KnowledgeType",
    "MemoryType",
    "PhaseStatus",
    "Priority",
    "RouteTarget",
    "TaskStatus",
    "VerdictStatus",
    # common
    "Artifact",
    "Event",
    "RuntimeContext",
    # spec
    "Requirement",
    "AC",
    "DataModel",
    "APIContract",
    "Scope",
    "StructuredSpec",
    "ValidationResult",
    # workflow
    "Task",
    "Phase",
    "WorkflowState",
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
