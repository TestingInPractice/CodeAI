"""CodeAI Platform — Workflow Repository (JSON Implementation).

File-based persistence for WorkflowSnapshot using JSON.
No business logic — only data access.
"""

import json
import shutil
from datetime import datetime
from pathlib import Path

from scripts.core.errors import RepositoryError
from scripts.core.repositories.repository import Repository
from scripts.core.workflow.snapshot import WorkflowSnapshot


class WorkflowRepository(Repository[WorkflowSnapshot]):
    """JSON file-based repository for workflow state.

    Storage layout:
        <state_dir>/
            state.json          ← current state
            backups/
                <timestamp>_<label>.json  ← backups

    Args:
        state_dir: Directory for state files (e.g., ".workflow").

    Usage:
        repo = WorkflowRepository(Path(".workflow"))
        snapshot = repo.load()
        # ... modify snapshot ...
        repo.save(snapshot)
        repo.backup(label="before-rollback")
    """

    def __init__(self, state_dir: Path) -> None:
        """Initialize repository.

        Args:
            state_dir: Directory for state files.
        """
        self._state_dir = Path(state_dir)
        self._state_file = self._state_dir / "state.json"
        self._backups_dir = self._state_dir / "backups"

    def load(self) -> WorkflowSnapshot | None:
        """Load workflow state from state.json.

        Returns:
            WorkflowSnapshot if file exists, None if not found.

        Raises:
            RepositoryError: If file is corrupted or cannot be parsed.
        """
        if not self._state_file.exists():
            return None

        try:
            data = json.loads(self._state_file.read_text(encoding="utf-8"))
            return WorkflowSnapshot.from_dict(data)
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise RepositoryError(
                f"Failed to load state: {e}",
                code="REPO_LOAD_FAILED",
                recoverable=False,
                cause=e,
            ) from e

    def save(self, snapshot: WorkflowSnapshot) -> None:
        """Save workflow state to state.json.

        Creates directories if they don't exist.
        Overwrites existing file.

        Args:
            snapshot: WorkflowSnapshot to persist.

        Raises:
            RepositoryError: If serialization or write fails.
        """
        try:
            self._state_dir.mkdir(parents=True, exist_ok=True)
            data = snapshot.to_dict()
            self._state_file.write_text(
                json.dumps(data, indent=2, ensure_ascii=False, default=str),
                encoding="utf-8",
            )
        except (OSError, TypeError) as e:
            raise RepositoryError(
                f"Failed to save state: {e}",
                code="REPO_SAVE_FAILED",
                recoverable=True,
                cause=e,
            ) from e

    def exists(self) -> bool:
        """Check if state file exists.

        Returns:
            True if state.json exists.
        """
        return self._state_file.exists()

    def backup(self, label: str = "") -> str:
        """Create a backup of the current state.

        Copies state.json to backups/<timestamp>_<label>.json.
        If no state exists, creates empty backup.

        Args:
            label: Optional label (e.g., "before-rollback").

        Returns:
            Backup file path as string.

        Raises:
            RepositoryError: If backup creation fails.
        """
        try:
            self._backups_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_label = label.replace(" ", "_").replace("/", "-") if label else "backup"
            backup_name = f"{timestamp}_{safe_label}.json"
            backup_path = self._backups_dir / backup_name

            if self._state_file.exists():
                shutil.copy2(self._state_file, backup_path)
            else:
                empty = WorkflowSnapshot()
                backup_path.write_text(
                    json.dumps(empty.to_dict(), indent=2, ensure_ascii=False, default=str),
                    encoding="utf-8",
                )

            return str(backup_path)

        except OSError as e:
            raise RepositoryError(
                f"Failed to create backup: {e}",
                code="REPO_BACKUP_FAILED",
                recoverable=True,
                cause=e,
            ) from e

    def restore(self, backup_id: str) -> WorkflowSnapshot:
        """Restore state from a backup.

        Reads backup file and writes to state.json.
        Returns the restored snapshot.

        Args:
            backup_id: Full path to backup file (from backup()).

        Returns:
            Restored WorkflowSnapshot.

        Raises:
            RepositoryError: If backup not found or corrupted.
        """
        backup_path = Path(backup_id)

        if not backup_path.exists():
            raise RepositoryError(
                f"Backup not found: {backup_id}",
                code="REPO_BACKUP_NOT_FOUND",
                recoverable=False,
            )

        try:
            data = json.loads(backup_path.read_text(encoding="utf-8"))
            snapshot = WorkflowSnapshot.from_dict(data)

            self.save(snapshot)
            return snapshot

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise RepositoryError(
                f"Failed to restore from backup: {e}",
                code="REPO_RESTORE_FAILED",
                recoverable=False,
                cause=e,
            ) from e

    def delete(self) -> None:
        """Delete the current workflow state.

        Removes state.json. Does not delete backups.

        Raises:
            RepositoryError: If deletion fails.
        """
        try:
            if self._state_file.exists():
                self._state_file.unlink()
        except OSError as e:
            raise RepositoryError(
                f"Failed to delete state: {e}",
                code="REPO_DELETE_FAILED",
                recoverable=True,
                cause=e,
            ) from e
