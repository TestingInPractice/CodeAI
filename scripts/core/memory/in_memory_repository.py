"""CodeAI Platform — In-Memory Memory Repository.

v1 implementation for prototypes and testing.
No filesystem, no external dependencies.
"""

from datetime import datetime

from scripts.core.memory.repository import MemoryRepository
from scripts.core.types.memory import MemoryEntry


class InMemoryMemoryRepository(MemoryRepository):
    """In-memory memory persistence."""

    def __init__(self):
        self._store: dict[str, MemoryEntry] = {}

    def store(self, entry: MemoryEntry) -> None:
        self._store[str(entry.id)] = entry

    def load(self, entry_id: str) -> MemoryEntry | None:
        return self._store.get(entry_id)

    def load_all(
        self,
        memory_type: str | None = None,
        scope: str = "project",
    ) -> list[MemoryEntry]:
        entries = list(self._store.values())
        if memory_type is not None:
            entries = [e for e in entries if e.type.value == memory_type]
        entries = [e for e in entries if e.scope == scope]
        entries.sort(key=lambda e: e.timestamp, reverse=True)
        return entries

    def delete(self, entry_id: str) -> bool:
        if entry_id in self._store:
            del self._store[entry_id]
            return True
        return False

    def exists(self, entry_id: str) -> bool:
        return entry_id in self._store

    def count(
        self,
        memory_type: str | None = None,
        scope: str = "project",
    ) -> int:
        return len(self.load_all(memory_type=memory_type, scope=scope))

    def delete_expired(self, before: datetime) -> int:
        to_delete = [
            eid for eid, e in self._store.items()
            if e.timestamp < before
        ]
        for eid in to_delete:
            del self._store[eid]
        return len(to_delete)
