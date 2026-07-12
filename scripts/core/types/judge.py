"""CodeAI Platform — Judge Engine types."""

from dataclasses import dataclass, field
from uuid import UUID

from scripts.core.enums import RouteTarget, VerdictStatus
from scripts.core.serialization import Serializable


@dataclass
class Verdict(Serializable):
    """Judge verdict."""
    overall: VerdictStatus
    scores: dict[str, float] = field(default_factory=dict)
    failures: list[str] = field(default_factory=list)
    confidence: float = 0.0


@dataclass
class Score(Serializable):
    """Individual judge score."""
    value: float
    breakdown: dict[str, float] = field(default_factory=dict)
    judge: str = ""


@dataclass
class RouteAction(Serializable):
    """Routing decision from Judge Engine."""
    target: RouteTarget
    reason: str = ""
    task_id: UUID | None = None
    phase_id: str | None = None


@dataclass(frozen=True)
class RubricCriterion(Serializable):
    """Single rubric criterion."""
    id: str
    label: str
    weight: int = 1
    scale: int = 5
    pass_threshold: int = 3
    critical: bool = False


@dataclass
class Rubric(Serializable):
    """Evaluation rubric."""
    name: str
    criteria: list[RubricCriterion] = field(default_factory=list)
