"""CodeAI Platform — Memory Repository Interface.

Abstract repository for MemoryEntry persistence.
Implementations: JsonMemoryRepository, (future) SqliteMemoryRepository.
"""

from abc import abstractmethod

from scripts.core.repositories.repository import Repository
from scripts.core.types.memory import MemoryEntry


class MemoryRepository(Repository[list[MemoryEntry]]):
    """Abstract repository for MemoryEntry persistence.

    Follows Repository Pattern: abstracts data access from business logic.
    Memory Layer depends on this interface, not on concrete storage.

    Implementations:
        - JsonMemoryRepository: file-based JSON storage
        - (future) SqliteMemoryRepository: SQLite storage

    Usage:
        repo = JsonMemoryRepository(path)
        entries = repo.load()
        entries.append(new_entry)
        repo.save(entries)
    """

    @abstractmethod
    def load(self) -> list[MemoryEntry]:
        """Load all memory entries.

        Returns:
            List of MemoryEntry objects. Empty list if no data saved.

        Raises:
            RepositoryError: If load fails.
        """
        ...

    @abstractmethod
    def save(self, entries: list[MemoryEntry]) -> None:
        """Save all memory entries.

        Overwrites the current state.

        Args:
            entries: List of MemoryEntry to persist.

        Raises:
            RepositoryError: If save fails.
        """
        ...

    @abstractmethod
    def query(self, scope: str = "project") -> list[MemoryEntry]:
        """Query memory entries by scope.

        Args:
            scope: Memory scope to filter by (project, session, etc.).

        Returns:
            List of matching MemoryEntry objects.

        Raises:
            RepositoryError: If query fails.
        """
        ...
