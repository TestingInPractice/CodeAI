"""CodeAI Platform — Spec Engine types."""

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from scripts.core.enums import Priority
from scripts.core.serialization import Serializable


@dataclass(frozen=True, slots=True)
class Requirement(Serializable):
    """Functional requirement (F-XXX)."""
    id: UUID
    title: str
    description: str
    priority: Priority
    dependencies: list[UUID] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class AC(Serializable):
    """Acceptance criterion (AC-XXX)."""
    id: UUID
    requirement_id: UUID
    description: str
    verifiable: bool = True


@dataclass(frozen=True, slots=True)
class FieldDefinition(Serializable):
    """Single field definition in a data model."""
    name: str
    type: str
    required: bool = True
    description: str = ""
    default: str | None = None


@dataclass(frozen=True, slots=True)
class DataModel(Serializable):
    """Data model definition."""
    name: str
    fields: list[FieldDefinition] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class APIContract(Serializable):
    """API contract definition."""
    method: str
    path: str
    operation_id: str = ""
    request_model: str = ""
    response_model: str = ""
    status_codes: list[int] = field(default_factory=list)
    auth_required: bool = False
    description: str = ""


@dataclass(frozen=True, slots=True)
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
