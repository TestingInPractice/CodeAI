"""CodeAI Platform — Exception Hierarchy.

All errors inherit from CodeAIError. Each error carries:
    - message: human-readable description
    - code: stable error code (DOMAIN_NNN)
    - recoverable: can the caller retry safely?
    - context: execution context at failure point
    - cause: wrapped original exception
"""

from typing import Any


class CodeAIError(Exception):
    """Base exception for all CodeAI errors."""

    def __init__(
        self,
        message: str,
        code: str,
        recoverable: bool = False,
        context: dict[str, Any] | None = None,
        cause: Exception | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.recoverable = recoverable
        self.context = context or {}
        self.cause = cause

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"message={self.message!r}, "
            f"code={self.code!r}, "
            f"recoverable={self.recoverable})"
        )


class SpecError(CodeAIError):
    """Spec Engine errors (validation, generation, parsing)."""
    pass


class WorkflowError(CodeAIError):
    """Workflow Engine errors (invariant violation, invalid transition)."""
    pass


class OODAError(CodeAIError):
    """OODA Runtime errors (agent failure, timeout, invalid output)."""
    pass


class KnowledgeError(CodeAIError):
    """Knowledge Layer errors (search failure, MCP connection)."""
    pass


class MemoryError(CodeAIError):
    """Memory Layer errors (storage failure, corruption)."""
    pass


class JudgeError(CodeAIError):
    """Judge Engine errors (evaluation failure, rubric not found)."""
    pass


class ValidationError(CodeAIError):
    """Schema/type validation errors."""
    pass


class ConfigurationError(CodeAIError):
    """Configuration errors (missing file, invalid setting)."""
    pass


class InfrastructureError(CodeAIError):
    """Infrastructure errors (filesystem, network, process)."""
    pass


class RepositoryError(CodeAIError):
    """Repository errors (load, save, backup, restore failures)."""
    pass
