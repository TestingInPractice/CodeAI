"""CodeAI Platform — Knowledge Repository abstraction.

Defines the abstract interface for knowledge persistence.
Implementations: InMemoryKnowledgeRepository (v1), SqliteKnowledgeRepository (future).

Matches CORE_RUNTIME.md §4 exactly.
"""

from abc import ABC, abstractmethod

from scripts.core.types.knowledge import Knowledge


class KnowledgeRepository(ABC):
    """Abstract repository for knowledge items.

    All persistence goes through this interface.
    KnowledgeLayer does NOT know about JSON, SQLite, or filesystem.

    Matches CORE_RUNTIME.md §4: only search() method.
    """

    @abstractmethod
    def search(self, query: str, kind: str | None = None) -> list[Knowledge]:
        """Search knowledge base by text query.

        Args:
            query: Text to search for.
            kind: Optional KnowledgeKind value to filter by.

        Returns:
            List of matching Knowledge items, sorted by relevance.

        Raises:
            KnowledgeError: If search fails.
        """

    @abstractmethod
    def index(self, item: Knowledge) -> None:
        """Index a knowledge item for search.

        Args:
            item: Knowledge item to index.

        Raises:
            KnowledgeError: If indexing fails.
        """

    @abstractmethod
    def index_all(self, items: list[Knowledge]) -> None:
        """Index multiple knowledge items.

        Args:
            items: List of Knowledge items to index.

        Raises:
            KnowledgeError: If indexing fails.
        """

    @abstractmethod
    def count(self) -> int:
        """Return total number of indexed items."""
