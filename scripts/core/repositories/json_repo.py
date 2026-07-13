"""CodeAI Platform — JSON Workflow Repository.

File-based persistence for WorkflowSnapshot using JSON.
Swap to SqliteWorkflowRepository without changing Workflow Engine.
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from scripts.core.repositories.base import WorkflowRepository
from scripts.core.types.workflow import WorkflowSnapshot


class JsonWorkflowRepository(WorkflowRepository):
    """JSON file-based repository for workflow state.

    Storage layout:
        <state_dir>/
            state.json          ← current state
            backups/
                <timestamp>_<label>.json  ← backups

    Args:
        state_dir: Directory for state files (e.g., ".workflow").
        state_filename: Name of the state file (default: "state.json").

    Usage:
        repo = JsonWorkflowRepository(Path(".workflow"))
        snapshot = repo.load()
        # ... modify snapshot ...
        repo.save(snapshot)
        repo.backup(label="before-rollback")
    """

    def __init__(
        self,
        state_dir: Path,
        state_filename: str = "state.json",
    ) -> None:
        """Initialize JSON repository.

        Args:
            state_dir: Directory for state files.
            state_filename: Name of the state file.
        """
        self._state_dir = Path(state_dir)
        self._state_file = self._state_dir / state_filename
        self._backups_dir = self._state_dir / "backups"

    def load(self) -> Optional[WorkflowSnapshot]:
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
                f"Failed to load state from {self._state_file}: {e}",
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
                f"Failed to save state to {self._state_file}: {e}",
                code="REPO_SAVE_FAILED",
                recoverable=True,
                cause=e,
            ) from e

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
                # Save empty snapshot as backup
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

            # Save restored state as current
            self.save(snapshot)
            return snapshot

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise RepositoryError(
                f"Failed to restore from backup {backup_id}: {e}",
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

    def list_backups(self) -> list[dict]:
        """List all available backups.

        Scans backups/ directory for .json files.

        Returns:
            List of dicts with id, label, created_at, size.
        """
        if not self._backups_dir.exists():
            return []

        backups = []
        for f in sorted(self._backups_dir.glob("*.json"), reverse=True):
            # Parse timestamp and label from filename
            # Format: YYYYMMDD_HHMMSS_label.json
            stem = f.stem
            parts = stem.split("_", 2)
            timestamp_str = "_".join(parts[:2]) if len(parts) >= 2 else stem
            label = parts[2] if len(parts) >= 2 else "backup"

            try:
                created_at = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
            except ValueError:
                created_at = datetime.fromtimestamp(f.stat().st_mtime)

            backups.append({
                "id": str(f),
                "label": label,
                "created_at": created_at.isoformat(),
                "size": f.stat().st_size,
            })

        return backups


class RepositoryError(Exception):
    """Repository operation error.

    Attributes:
        message: Human-readable error description.
        code: Stable error code for programmatic handling.
        recoverable: Whether the operation can be retried safely.
        cause: Original exception that caused this error.
    """

    def __init__(
        self,
        message: str,
        code: str = "REPO_ERROR",
        recoverable: bool = False,
        cause: Exception | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.recoverable = recoverable
        self.cause = cause

    def __repr__(self) -> str:
        return (
            f"RepositoryError("
            f"message={self.message!r}, "
            f"code={self.code!r}, "
            f"recoverable={self.recoverable})"
        )
