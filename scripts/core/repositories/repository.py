"""CodeAI Platform — Base Repository Interface.

Abstract base class for all repositories.
Follows Repository Pattern: abstracts data access from business logic.
"""

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class Repository(ABC, Generic[T]):
    """Abstract base repository.

    Defines the common interface for all repositories.
    Each concrete repository implements storage-specific logic.

    Type Parameters:
        T: The type of entity this repository manages.

    Implementations:
        - WorkflowRepository: workflow state persistence
        - MemoryRepository: memory entries persistence
        - KnowledgeRepository: knowledge items persistence
    """

    @abstractmethod
    def load(self) -> T | None:
        """Load the current entity.

        Returns:
            Entity if exists, None if no data saved yet.

        Raises:
            RepositoryError: If load fails.
        """
        ...

    @abstractmethod
    def save(self, entity: T) -> None:
        """Save entity.

        Overwrites the current state. Creates record if doesn't exist.

        Args:
            entity: Entity to persist.

        Raises:
            RepositoryError: If save fails.
        """
        ...

    @abstractmethod
    def delete(self) -> None:
        """Delete the current entity.

        Removes the saved state entirely. After this, load() returns None.

        Raises:
            RepositoryError: If delete fails.
        """
        ...
