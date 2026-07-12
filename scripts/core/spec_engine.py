"""CodeAI Platform — Spec Engine (stub)."""

from pathlib import Path

from scripts.core.types import StructuredSpec, ValidationResult


class SpecEngine:
    """Spec Engine — lifecycle of specifications.

    Responsibilities:
        - Generate goals.md from user prompt
        - Validate goals.md structure (F-XXX, AC-XXX, etc.)
        - Human gate: approve spec
        - Parse goals.md into StructuredSpec

    API:
        generate(prompt) -> Path
        validate(goals_path) -> ValidationResult
        approve(goals_path) -> None
        parse(goals_path) -> StructuredSpec
    """

    def generate(self, prompt: str) -> Path:
        """Generate goals.md from user prompt.

        Args:
            prompt: User's project description.

        Returns:
            Path to generated goals.md.
        """
        raise NotImplementedError

    def validate(self, goals_path: Path) -> ValidationResult:
        """Validate goals.md structure.

        Args:
            goals_path: Path to goals.md.

        Returns:
            ValidationResult with valid=True/False and errors/warnings.
        """
        raise NotImplementedError

    def approve(self, goals_path: Path) -> None:
        """Human gate: put spec on approval.

        Args:
            goals_path: Path to goals.md.
        """
        raise NotImplementedError

    def parse(self, goals_path: Path) -> StructuredSpec:
        """Parse goals.md into StructuredSpec.

        Args:
            goals_path: Path to goals.md.

        Returns:
            StructuredSpec with requirements, ACs, data models, etc.
        """
        raise NotImplementedError
