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
