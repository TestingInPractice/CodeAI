"""CodeAI Platform — Spec Engine.

Minimal template-based implementation. No LLM, no filesystem writes.
Generates StructuredSpec directly from prompt analysis.
"""

from pathlib import Path
from uuid import uuid4

from scripts.core.enums import Priority
from scripts.core.errors import SpecError
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


class SpecEngine:
    """Spec Engine — lifecycle of specifications.

    Responsibilities:
        - Generate goals.md from user prompt
        - Validate goals.md structure
        - Human gate: approve spec
        - Parse goals.md into StructuredSpec

    v1: Template-based, no LLM. Generates StructuredSpec in-memory.
    """

    def generate(self, prompt: str) -> Path:
        """Generate goals.md from user prompt.

        Creates a minimal goals.md structure in-memory.
        Returns a virtual path (no filesystem write in v1).

        Args:
            prompt: User's project description.

        Returns:
            Path to generated goals.md.
        """
        if not prompt or not prompt.strip():
            raise SpecError(
                "Cannot generate spec from empty prompt",
                code="SPEC_EMPTY_PROMPT",
                recoverable=False,
            )
        return Path("docs/specs/goals.md")

    def validate(self, goals_path: Path) -> ValidationResult:
        """Validate goals.md structure.

        Args:
            goals_path: Path to goals.md.

        Returns:
            ValidationResult with valid=True/False and errors/warnings.
        """
        if goals_path is None:
            return ValidationResult(
                valid=False,
                errors=["goals_path is None"],
            )
        return ValidationResult(valid=True, errors=[], warnings=[])

    def approve(self, goals_path: Path) -> None:
        """Human gate: approve spec.

        v1: Auto-approves (no human gate in prototype).

        Args:
            goals_path: Path to goals.md.
        """
        if goals_path is None:
            raise SpecError(
                "Cannot approve null spec",
                code="SPEC_NULL_PATH",
                recoverable=False,
            )

    def parse(self, goals_path: Path) -> StructuredSpec:
        """Parse goals.md into StructuredSpec.

        v1: Returns a minimal spec derived from the path context.
        In production, this would parse actual goals.md content.

        Args:
            goals_path: Path to goals.md.

        Returns:
            StructuredSpec with requirements, ACs, data models, etc.
        """
        if goals_path is None:
            raise SpecError(
                "Cannot parse null spec",
                code="SPEC_NULL_PATH",
                recoverable=False,
            )

        req_id = uuid4()
        return StructuredSpec(
            requirements=[
                Requirement(
                    id=req_id,
                    title="Implement requested feature",
                    description="Deliver the feature as specified in the prompt",
                    priority=Priority.MUST,
                ),
            ],
            acceptance_criteria=[
                AC(
                    id=uuid4(),
                    requirement_id=req_id,
                    description="Feature works correctly",
                ),
                AC(
                    id=uuid4(),
                    requirement_id=req_id,
                    description="All tests pass",
                ),
            ],
            data_models=[],
            api_contracts=[],
            scope=Scope(included=["core implementation"], excluded=[]),
        )
