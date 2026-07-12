"""CodeAI Platform — Spec Engine types."""

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from scripts.core.enums import Priority
from scripts.core.serialization import Serializable


@dataclass(frozen=True)
class Requirement(Serializable):
    """Functional requirement (F-XXX)."""
    id: UUID
    title: str
    description: str
    priority: Priority
    dependencies: list[UUID] = field(default_factory=list)


@dataclass(frozen=True)
class AC(Serializable):
    """Acceptance criterion (AC-XXX)."""
    id: UUID
    requirement_id: UUID
    description: str
    verifiable: bool = True


@dataclass(frozen=True)
class DataModel(Serializable):
    """Data model definition."""
    name: str
    fields: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class APIContract(Serializable):
    """API contract definition."""
    method: str
    path: str
    description: str = ""


@dataclass(frozen=True)
class Scope(Serializable):
    """Project scope."""
    included: list[str] = field(default_factory=list)
    excluded: list[str] = field(default_factory=list)


@dataclass
class StructuredSpec(Serializable):
    """Structured specification parsed from goals.md."""
    requirements: list[Requirement] = field(default_factory=list)
    acceptance_criteria: list[AC] = field(default_factory=list)
    data_models: list[DataModel] = field(default_factory=list)
    api_contracts: list[APIContract] = field(default_factory=list)
    scope: Scope = field(default_factory=Scope)


@dataclass
class ValidationResult(Serializable):
    """Result of spec validation."""
    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
