"""CodeAI Platform — Memory Repository abstraction.

Defines the abstract interface for memory persistence.
Implementations: JsonMemoryRepository (v1), SqliteMemoryRepository (future).
"""

from abc import ABC, abstractmethod
from datetime import datetime

from scripts.core.types.memory import MemoryEntry


class MemoryRepository(ABC):
    """Abstract repository for memory entries.

    All persistence goes through this interface.
    MemoryLayer does NOT know about JSON, SQLite, or filesystem.
    """

    @abstractmethod
    def store(self, entry: MemoryEntry) -> None:
        """Persist a memory entry.

        Args:
            entry: MemoryEntry to store. Must have id and timestamp set.

        Raises:
            MemoryError: If storage fails.
        """

    @abstractmethod
    def load(self, entry_id: str) -> MemoryEntry | None:
        """Load a single entry by ID.

        Args:
            entry_id: UUID string of the entry to load.

        Returns:
            MemoryEntry if found, None otherwise.

        Raises:
            MemoryError: If load fails.
        """

    @abstractmethod
    def load_all(
        self,
        memory_type: str | None = None,
        scope: str = "project",
    ) -> list[MemoryEntry]:
        """Load all entries matching filters.

        Args:
            memory_type: Filter by MemoryType value (None = all types).
            scope: Filter by scope (default: "project").

        Returns:
            List of matching entries, sorted by timestamp descending.

        Raises:
            MemoryError: If load fails.
        """

    @abstractmethod
    def delete(self, entry_id: str) -> bool:
        """Delete an entry by ID.

        Args:
            entry_id: UUID string of the entry to delete.

        Returns:
            True if deleted, False if not found.

        Raises:
            MemoryError: If delete fails.
        """

    @abstractmethod
    def exists(self, entry_id: str) -> bool:
        """Check if an entry exists.

        Args:
            entry_id: UUID string of the entry to check.

        Returns:
            True if exists, False otherwise.

        Raises:
            MemoryError: If check fails.
        """

    @abstractmethod
    def count(
        self,
        memory_type: str | None = None,
        scope: str = "project",
    ) -> int:
        """Count entries matching filters.

        Args:
            memory_type: Filter by MemoryType value (None = all types).
            scope: Filter by scope (default: "project").

        Returns:
            Count of matching entries.

        Raises:
            MemoryError: If count fails.
        """

    @abstractmethod
    def delete_expired(self, before: datetime) -> int:
        """Delete entries older than the given timestamp.

        Args:
            before: Delete entries with timestamp < before.

        Returns:
            Number of entries deleted.

        Raises:
            MemoryError: If delete fails.
        """
