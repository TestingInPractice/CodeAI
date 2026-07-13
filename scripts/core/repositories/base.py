"""CodeAI Platform — Abstract Workflow Repository.

Defines the interface for workflow state persistence.
Implementations: JsonWorkflowRepository, (future) SqliteWorkflowRepository.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from scripts.core.types.workflow import WorkflowSnapshot


class WorkflowRepository(ABC):
    """Abstract repository for WorkflowSnapshot persistence.

    Follows Repository Pattern: abstracts data access from business logic.
    Workflow Engine depends on this interface, not on concrete storage.

    Implementations:
        - JsonWorkflowRepository: file-based JSON storage
        - (future) SqliteWorkflowRepository: SQLite storage

    Usage:
        repo = JsonWorkflowRepository(path)
        snapshot = repo.load()
        snapshot.iteration += 1
        repo.save(snapshot)
    """

    @abstractmethod
    def load(self) -> Optional[WorkflowSnapshot]:
        """Load the current workflow snapshot.

        Returns:
            WorkflowSnapshot if exists, None if no state saved yet.

        Raises:
            RepositoryError: If load fails (corrupted data, I/O error).
        """
        ...

    @abstractmethod
    def save(self, snapshot: WorkflowSnapshot) -> None:
        """Save workflow snapshot.

        Overwrites the current state. Creates file/record if doesn't exist.

        Args:
            snapshot: WorkflowSnapshot to persist.

        Raises:
            RepositoryError: If save fails (I/O error, serialization error).
        """
        ...

    @abstractmethod
    def backup(self, label: str = "") -> str:
        """Create a backup of the current state.

        Backup is a snapshot-in-time copy, independent of future saves.
        Useful before risky operations (rollback, phase transition).

        Args:
            label: Optional label for the backup (e.g., "before-rollback").

        Returns:
            Backup identifier (file path, record ID, etc.).

        Raises:
            RepositoryError: If backup fails.
        """
        ...

    @abstractmethod
    def restore(self, backup_id: str) -> WorkflowSnapshot:
        """Restore state from a backup.

        Replaces current state with the backup contents.

        Args:
            backup_id: Backup identifier returned by backup().

        Returns:
            Restored WorkflowSnapshot.

        Raises:
            RepositoryError: If backup not found or restore fails.
        """
        ...

    @abstractmethod
    def delete(self) -> None:
        """Delete the current workflow state.

        Removes the saved state entirely. After this, load() returns None.

        Raises:
            RepositoryError: If delete fails.
        """
        ...

    @abstractmethod
    def list_backups(self) -> list[dict]:
        """List all available backups.

        Returns:
            List of backup metadata dicts with keys:
            - id: backup identifier
            - label: backup label
            - created_at: ISO timestamp
            - size: file size in bytes (if applicable)
        """
        ...
