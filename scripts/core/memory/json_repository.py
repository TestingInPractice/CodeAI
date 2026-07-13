"""CodeAI Platform — JSON Memory Repository.

Persists MemoryEntry objects as JSON files.
One file per project scope. No SQLite, no Vector DB, no LLM.
"""

import json
from datetime import datetime
from pathlib import Path

from scripts.core.errors import MemoryError
from scripts.core.memory.repository import MemoryRepository
from scripts.core.types.memory import MemoryEntry


class JsonMemoryRepository(MemoryRepository):
    """JSON file-based memory persistence.

    Storage layout:
        {base_path}/
            project/
                memory.json    # all entries for project scope
            global/
                memory.json    # all entries for global scope

    Usage:
        repo = JsonMemoryRepository(Path(".codeai/memory"))
        repo.store(entry)
        loaded = repo.load(entry_id)
    """

    def __init__(self, base_path: Path) -> None:
        """Initialize JSON repository.

        Args:
            base_path: Root directory for memory storage.
                       Creates subdirectories per scope.
        """
        self._base_path = base_path
        self._base_path.mkdir(parents=True, exist_ok=True)

    def store(self, entry: MemoryEntry) -> None:
        """Persist a memory entry to JSON file.

        Args:
            entry: MemoryEntry to store.

        Raises:
            MemoryError: If write fails.
        """
        try:
            data = self._read_scope(entry.scope)
            entry_dict = entry.to_dict()
            data[str(entry.id)] = entry_dict
            self._write_scope(entry.scope, data)
        except MemoryError:
            raise
        except Exception as e:
            raise MemoryError(
                f"Failed to store entry: {e}",
                code="MEM_STORE_FAILED",
                recoverable=True,
                context={"entry_id": str(entry.id), "scope": entry.scope},
                cause=e,
            ) from e

    def load(self, entry_id: str) -> MemoryEntry | None:
        """Load a single entry by ID from all scopes.

        Args:
            entry_id: UUID string of the entry to load.

        Returns:
            MemoryEntry if found, None otherwise.

        Raises:
            MemoryError: If read fails.
        """
        try:
            for scope in ("project", "global"):
                data = self._read_scope(scope)
                if entry_id in data:
                    return MemoryEntry.from_dict(data[entry_id])
            return None
        except MemoryError:
            raise
        except Exception as e:
            raise MemoryError(
                f"Failed to load entry: {e}",
                code="MEM_LOAD_FAILED",
                recoverable=True,
                context={"entry_id": entry_id},
                cause=e,
            ) from e

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
            MemoryError: If read fails.
        """
        try:
            data = self._read_scope(scope)
            entries = []
            for entry_dict in data.values():
                entry = MemoryEntry.from_dict(entry_dict)
                if memory_type is not None and entry.type.value != memory_type:
                    continue
                entries.append(entry)
            entries.sort(key=lambda e: e.timestamp, reverse=True)
            return entries
        except MemoryError:
            raise
        except Exception as e:
            raise MemoryError(
                f"Failed to load entries: {e}",
                code="MEM_LOAD_FAILED",
                recoverable=True,
                context={"scope": scope, "memory_type": memory_type},
                cause=e,
            ) from e

    def delete(self, entry_id: str) -> bool:
        """Delete an entry by ID from all scopes.

        Args:
            entry_id: UUID string of the entry to delete.

        Returns:
            True if deleted, False if not found.

        Raises:
            MemoryError: If delete fails.
        """
        try:
            deleted = False
            for scope in ("project", "global"):
                data = self._read_scope(scope)
                if entry_id in data:
                    del data[entry_id]
                    self._write_scope(scope, data)
                    deleted = True
            return deleted
        except MemoryError:
            raise
        except Exception as e:
            raise MemoryError(
                f"Failed to delete entry: {e}",
                code="MEM_DELETE_FAILED",
                recoverable=True,
                context={"entry_id": entry_id},
                cause=e,
            ) from e

    def exists(self, entry_id: str) -> bool:
        """Check if an entry exists in any scope.

        Args:
            entry_id: UUID string of the entry to check.

        Returns:
            True if exists, False otherwise.

        Raises:
            MemoryError: If check fails.
        """
        try:
            for scope in ("project", "global"):
                data = self._read_scope(scope)
                if entry_id in data:
                    return True
            return False
        except MemoryError:
            raise
        except Exception as e:
            raise MemoryError(
                f"Failed to check existence: {e}",
                code="MEM_LOAD_FAILED",
                recoverable=True,
                context={"entry_id": entry_id},
                cause=e,
            ) from e

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
        try:
            data = self._read_scope(scope)
            if memory_type is None:
                return len(data)
            count = 0
            for entry_dict in data.values():
                if entry_dict.get("type") == memory_type:
                    count += 1
            return count
        except MemoryError:
            raise
        except Exception as e:
            raise MemoryError(
                f"Failed to count entries: {e}",
                code="MEM_LOAD_FAILED",
                recoverable=True,
                context={"scope": scope, "memory_type": memory_type},
                cause=e,
            ) from e

    def delete_expired(self, before: datetime) -> int:
        """Delete entries older than the given timestamp.

        Args:
            before: Delete entries with timestamp < before.

        Returns:
            Number of entries deleted.

        Raises:
            MemoryError: If delete fails.
        """
        try:
            total_deleted = 0
            for scope in ("project", "global"):
                data = self._read_scope(scope)
                to_delete = []
                for entry_id, entry_dict in data.items():
                    ts_str = entry_dict.get("timestamp")
                    if ts_str:
                        ts = datetime.fromisoformat(ts_str)
                        if ts < before:
                            to_delete.append(entry_id)
                for entry_id in to_delete:
                    del data[entry_id]
                    total_deleted += 1
                if to_delete:
                    self._write_scope(scope, data)
            return total_deleted
        except MemoryError:
            raise
        except Exception as e:
            raise MemoryError(
                f"Failed to delete expired: {e}",
                code="MEM_DELETE_FAILED",
                recoverable=True,
                context={"before": before.isoformat()},
                cause=e,
            ) from e

    def _scope_path(self, scope: str) -> Path:
        """Get file path for a scope."""
        scope_dir = self._base_path / scope
        scope_dir.mkdir(parents=True, exist_ok=True)
        return scope_dir / "memory.json"

    def _read_scope(self, scope: str) -> dict[str, dict]:
        """Read all entries for a scope."""
        path = self._scope_path(scope)
        if not path.exists():
            return {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}

    def _write_scope(self, scope: str, data: dict[str, dict]) -> None:
        """Write all entries for a scope."""
        path = self._scope_path(scope)
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise MemoryError(
                f"Failed to write scope: {e}",
                code="MEM_STORE_FAILED",
                recoverable=True,
                context={"scope": scope},
                cause=e,
            ) from e
