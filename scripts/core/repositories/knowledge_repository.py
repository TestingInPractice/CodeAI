"""CodeAI Platform — Knowledge Repository Interface.

Abstract repository for Knowledge persistence.
Implementations: JsonKnowledgeRepository, (future) VectorKnowledgeRepository.
"""

from abc import abstractmethod

from scripts.core.repositories.repository import Repository
from scripts.core.types.knowledge import Knowledge


class KnowledgeRepository(Repository[list[Knowledge]]):
    """Abstract repository for Knowledge persistence.

    Follows Repository Pattern: abstracts data access from business logic.
    Knowledge Layer depends on this interface, not on concrete storage.

    Implementations:
        - JsonKnowledgeRepository: file-based JSON storage
        - (future) VectorKnowledgeRepository: vector DB storage

    Usage:
        repo = JsonKnowledgeRepository(path)
        items = repo.load()
        items.append(new_item)
        repo.save(items)
    """

    @abstractmethod
    def load(self) -> list[Knowledge]:
        """Load all knowledge items.

        Returns:
            List of Knowledge objects. Empty list if no data saved.

        Raises:
            RepositoryError: If load fails.
        """
        ...

    @abstractmethod
    def save(self, items: list[Knowledge]) -> None:
        """Save all knowledge items.

        Overwrites the current state.

        Args:
            items: List of Knowledge to persist.

        Raises:
            RepositoryError: If save fails.
        """
        ...

    @abstractmethod
    def search(self, query: str, kind: str | None = None) -> list[Knowledge]:
        """Search knowledge items.

        Args:
            query: Search query string.
            kind: Optional KnowledgeKind to filter by.

        Returns:
            List of matching Knowledge objects.

        Raises:
            RepositoryError: If search fails.
        """
        ...
