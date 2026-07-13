"""CodeAI Platform — Repository Pattern for persistence.

Provides abstract interfaces and concrete implementations for
data access. Swappable without changing business logic.
"""

from scripts.core.repositories.base import WorkflowRepository
from scripts.core.repositories.json_repo import JsonWorkflowRepository
from scripts.core.repositories.repository import Repository
from scripts.core.repositories.workflow_repository import WorkflowRepository as WorkflowRepositoryInterface
from scripts.core.repositories.memory_repository import MemoryRepository
from scripts.core.repositories.knowledge_repository import KnowledgeRepository

__all__ = [
    "Repository",
    "WorkflowRepository",
    "WorkflowRepositoryInterface",
    "JsonWorkflowRepository",
    "MemoryRepository",
    "KnowledgeRepository",
]
