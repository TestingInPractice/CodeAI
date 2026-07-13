"""CodeAI Platform — Enumerations."""

from enum import Enum


class Priority(str, Enum):
    """Requirement priority."""
    MUST = "must"
    SHOULD = "should"
    COULD = "could"
    NICE = "nice"


class TaskStatus(str, Enum):
    """Task status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"


class PhaseStatus(str, Enum):
    """Phase status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class VerdictStatus(str, Enum):
    """Judge verdict status."""
    PASS = "PASS"
    PASS_WITH_CONCERNS = "PASS_WITH_CONCERNS"
    FAIL = "FAIL"


class RouteTarget(str, Enum):
    """Judge routing target."""
    OODA = "ooda"
    SPEC = "spec"
    WORKFLOW = "workflow"


class MemoryType(str, Enum):
    """Memory entry type."""
    PROJECT_HISTORY = "project_history"
    JUDGE_HISTORY = "judge_history"
    ITERATIONS = "iterations"
    DECISIONS = "decisions"
    LONG_TERM = "long_term"
    USER_PREFERENCES = "user_preferences"
    LEARNED_PATTERNS = "learned_patterns"


class KnowledgeType(str, Enum):
    """Knowledge context type."""
    ARCHITECTURE = "architecture"
    BEST_PRACTICE = "best_practice"
    REFERENCE = "reference"
    TOOL = "tool"
    PATTERN = "pattern"


class KnowledgeKind(str, Enum):
    """Knowledge item kind."""
    SPEC = "spec"
    ADR = "adr"
    CODE = "code"
    DOCUMENT = "document"
    ARTICLE = "article"
    TEST = "test"
    API = "api"
    MEMORY = "memory"


class WorkflowStatus(str, Enum):
    """Overall workflow pipeline status."""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLING_BACK = "rolling_back"


class EventType(str, Enum):
    """All events in the CodeAI Platform.

    Naming convention: SUBSYSTEM_ACTION
    """
    # Spec Engine
    SPEC_CREATED = "spec.created"
    SPEC_VALIDATED = "spec.validated"
    SPEC_APPROVED = "spec.approved"

    # Workflow Engine
    PHASE_STARTED = "phase.started"
    PHASE_COMPLETED = "phase.completed"
    PHASE_FAILED = "phase.failed"
    PHASE_ROLLBACK = "phase.rollback"

    # Task lifecycle
    TASK_STARTED = "task.started"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"
    TASK_INTERRUPTED = "task.interrupted"

    # Judge Engine
    JUDGE_PASSED = "judge.passed"
    JUDGE_FAILED = "judge.failed"
    JUDGE_ROUTED = "judge.routed"

    # Knowledge Layer
    KNOWLEDGE_REQUESTED = "knowledge.requested"
    KNOWLEDGE_RETRIEVED = "knowledge.retrieved"

    # Memory Layer
    MEMORY_STORED = "memory.stored"
    MEMORY_LOADED = "memory.loaded"
