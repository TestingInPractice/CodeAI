"""CodeAI Platform — Memory Layer.

Orchestrator for memory operations. Sits on top of MemoryRepository.
No file I/O, no persistence — all delegated to the injected repository.

Public API matches CORE_RUNTIME.md §2.5 exactly.
"""

import hashlib
from datetime import datetime, timedelta

from scripts.core.enums import MemoryType
from scripts.core.errors import MemoryError
from scripts.core.memory.repository import MemoryRepository
from scripts.core.types.memory import MemoryEntry

# ---------------------------------------------------------------------------
# Retention policy (MEMORY_LAYER_DESIGN.md §7)
# ---------------------------------------------------------------------------

_RETENTION_POLICY: dict[str, dict] = {
    "project_history":  {"max": 1000, "ttl_days": 90,   "permanent": False},
    "judge_history":    {"max": 500,  "ttl_days": 90,   "permanent": False},
    "iterations":       {"max": 100,  "ttl_days": 30,   "permanent": False},
    "decisions":        {"max": None, "ttl_days": None,  "permanent": True},
    "learned_patterns": {"max": 200,  "ttl_days": 60,   "permanent": False},
    "long_term":        {"max": None, "ttl_days": None,  "permanent": True},
    "user_preferences": {"max": None, "ttl_days": None,  "permanent": True},
}

_VALID_SCOPES = ("project", "global")
_MAX_LOAD_LIMIT = 500


class MemoryLayer:
    """Orchestrator for memory operations.

    Responsibilities (MEMORY_LAYER_DESIGN.md §3):
    - Validate entries (MINV-1, MINV-8)
    - Compute content hashes (MINV-2)
    - Deduplicate on store (MINV-3)
    - Enforce retention / GC (MINV-5)
    - Filter expired entries on load (MINV-4)
    - Text search + recency sort (§10)
    - Template-based summarization (§4)

    Does NOT:
    - Access filesystem directly (Repository Pattern)
    - Call LLMs (template-based summarize in v1)
    - Couple to other subsystems
    """

    def __init__(self, repository: MemoryRepository) -> None:
        """Initialize with injected repository.

        Args:
            repository: MemoryRepository implementation (Json, InMemory, etc.)
        """
        self._repo = repository

    # ------------------------------------------------------------------
    # Public API (frozen — CORE_RUNTIME.md §2.5)
    # ------------------------------------------------------------------

    def store(self, entry: MemoryEntry) -> None:
        """Store a memory entry.

        Validates invariants, computes content hash, deduplicates,
        enforces retention policy, then persists via repository.

        Args:
            entry: MemoryEntry to store.

        Raises:
            MemoryError: On validation failure or persistence error.
        """
        self._validate_entry(entry)
        self._ensure_content_hash(entry)

        # Dedup check (MINV-3): same type + content_hash → merge
        duplicate = self._find_duplicate(entry)
        if duplicate is not None:
            self._merge_entries(duplicate, entry)
            return

        # Persist new entry
        try:
            self._repo.store(entry)
        except MemoryError:
            raise
        except Exception as e:
            raise MemoryError(
                f"Failed to store entry: {e}",
                code="MEM_STORE_FAILED",
                recoverable=True,
                context={"entry_type": entry.type.value, "scope": entry.scope},
                cause=e,
            ) from e

        # Enforce retention (lazy GC)
        self._enforce_retention(entry.type.value, entry.scope)

        # Extension point: emit "memory.stored" event (Event Bus v2)
        # self._emit("memory.stored", {"entry_id": str(entry.id), "type": entry.type.value})

    def load(self, query: str, scope: str = "project") -> list[MemoryEntry]:
        """Load entries matching query, filtered by scope.

        Performs case-insensitive substring match on content.
        Returns entries sorted by recency (timestamp descending).

        Args:
            query: Text to search for in entry content.
            scope: Filter by scope (default: "project").

        Returns:
            List of matching entries, most recent first.

        Raises:
            MemoryError: On repository failure.
        """
        self._validate_scope(scope)

        try:
            all_entries = self._repo.load_all(scope=scope)
        except MemoryError:
            raise
        except Exception as e:
            raise MemoryError(
                f"Failed to load entries: {e}",
                code="MEM_LOAD_FAILED",
                recoverable=True,
                context={"query": query, "scope": scope},
                cause=e,
            ) from e

        # Filter expired (MINV-4)
        now = datetime.now()
        active = [e for e in all_entries if not self._is_expired(e, now)]

        # Text match (§10: case-insensitive substring)
        query_lower = query.lower()
        matched = [e for e in active if query_lower in e.content.lower()]

        # Sort by recency (§10: timestamp descending)
        matched.sort(key=lambda e: e.timestamp, reverse=True)

        # Cap at MAX_LOAD_LIMIT (MINV-6)
        return matched[:_MAX_LOAD_LIMIT]

    def summarize(self, scope: str = "project", depth: str = "brief") -> str:
        """Summarize stored memory for the given scope.

        v1: Template-based summarization (no LLM).
        - "brief": count per type, 1-2 sentences
        - "detailed": per-type paragraph with recent entries
        - "full": structured markdown report with all entries

        Args:
            scope: Filter by scope (default: "project").
            depth: Summary depth: "brief", "detailed", or "full".

        Returns:
            Summary string. Never empty for non-empty store (MINV-7).

        Raises:
            MemoryError: On repository failure.
        """
        self._validate_scope(scope)
        self._validate_depth(depth)

        try:
            all_entries = self._repo.load_all(scope=scope)
        except MemoryError:
            raise
        except Exception as e:
            raise MemoryError(
                f"Failed to summarize: {e}",
                code="MEM_SUMMARIZE_FAILED",
                recoverable=True,
                context={"scope": scope},
                cause=e,
            ) from e

        if not all_entries:
            return "No entries found."

        # Filter expired
        now = datetime.now()
        active = [e for e in all_entries if not self._is_expired(e, now)]

        if not active:
            return "No active entries found."

        # Group by type
        grouped = self._group_by_type(active)

        if depth == "brief":
            return self._summarize_brief(grouped)
        if depth == "detailed":
            return self._summarize_detailed(grouped)
        if depth == "full":
            return self._summarize_full(grouped, scope)

        return self._summarize_brief(grouped)

    # ------------------------------------------------------------------
    # Validation (MINV-1, MINV-8)
    # ------------------------------------------------------------------

    def _validate_entry(self, entry: MemoryEntry) -> None:
        """Validate entry invariants before store."""
        if not entry.id:
            raise MemoryError(
                "Invalid entry: id is missing",
                code="MEM_INVALID_ENTRY",
                recoverable=False,
                context={"field": "id"},
            )
        if not entry.type:
            raise MemoryError(
                "Invalid entry: type is missing",
                code="MEM_INVALID_ENTRY",
                recoverable=False,
                context={"field": "type"},
            )
        if not entry.content:
            raise MemoryError(
                "Invalid entry: content is empty",
                code="MEM_INVALID_ENTRY",
                recoverable=False,
                context={"field": "content"},
            )
        if entry.scope not in _VALID_SCOPES:
            raise MemoryError(
                f"Invalid scope: {entry.scope!r} (must be 'project' or 'global')",
                code="MEM_INVALID_ENTRY",
                recoverable=False,
                context={"field": "scope", "value": entry.scope},
            )

    def _validate_scope(self, scope: str) -> None:
        """Validate scope parameter (MINV-8)."""
        if scope not in _VALID_SCOPES:
            raise MemoryError(
                f"Invalid scope: {scope!r} (must be 'project' or 'global')",
                code="MEM_INVALID_ENTRY",
                recoverable=False,
                context={"field": "scope", "value": scope},
            )

    def _validate_depth(self, depth: str) -> None:
        """Validate summarize depth parameter."""
        if depth not in ("brief", "detailed", "full"):
            raise MemoryError(
                f"Invalid depth: {depth!r} (must be 'brief', 'detailed', or 'full')",
                code="MEM_INVALID_ENTRY",
                recoverable=False,
                context={"field": "depth", "value": depth},
            )

    # ------------------------------------------------------------------
    # Content hash (MINV-2)
    # ------------------------------------------------------------------

    def _ensure_content_hash(self, entry: MemoryEntry) -> None:
        """Compute content_hash if not already set."""
        if not entry.content_hash:
            raw = entry.content.lower().strip()
            entry.content_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()

    # ------------------------------------------------------------------
    # Deduplication (MINV-3, §9 exceptions)
    # ------------------------------------------------------------------

    def _find_duplicate(self, entry: MemoryEntry) -> MemoryEntry | None:
        """Find existing entry with same type + content_hash.

        Exceptions (§9):
        - iterations: never deduplicated
        - project_history with different phase_id: never deduplicated
        """
        if entry.type == MemoryType.ITERATIONS:
            return None

        try:
            candidates = self._repo.load_all(
                memory_type=entry.type.value,
                scope=entry.scope,
            )
        except MemoryError:
            raise
        except Exception as e:
            raise MemoryError(
                f"Failed to check duplicates: {e}",
                code="MEM_LOAD_FAILED",
                recoverable=True,
                context={"entry_type": entry.type.value},
                cause=e,
            ) from e

        for candidate in candidates:
            if str(candidate.id) == str(entry.id):
                continue
            if candidate.content_hash != entry.content_hash:
                continue
            # project_history: skip if different phase_id (§9)
            if entry.type == MemoryType.PROJECT_HISTORY:
                old_phase = candidate.metadata.get("phase_id")
                new_phase = entry.metadata.get("phase_id")
                if old_phase != new_phase:
                    continue
            return candidate

        return None

    def _merge_entries(self, existing: MemoryEntry, new: MemoryEntry) -> None:
        """Merge new entry's metadata into existing (§9 merge rules).

        Fields kept from existing: content, timestamp, id.
        Fields merged: metadata (union, new overrides), version (increment).
        """
        merged_metadata = {**existing.metadata, **new.metadata}
        updated = MemoryEntry(
            id=existing.id,
            type=existing.type,
            content=existing.content,
            timestamp=existing.timestamp,
            metadata=merged_metadata,
            scope=existing.scope,
            content_hash=existing.content_hash,
            version=existing.version + 1,
        )
        try:
            self._repo.store(updated)
        except MemoryError:
            raise
        except Exception as e:
            raise MemoryError(
                f"Failed to merge entry: {e}",
                code="MEM_STORE_FAILED",
                recoverable=True,
                context={"entry_id": str(existing.id)},
                cause=e,
            ) from e

    # ------------------------------------------------------------------
    # Retention / GC (MINV-5)
    # ------------------------------------------------------------------

    def _enforce_retention(self, memory_type: str, scope: str) -> None:
        """Lazy GC: evict expired entries and enforce max-count.

        Permanent types are never GC'd (MINV-5).
        """
        policy = _RETENTION_POLICY.get(memory_type)
        if policy is None:
            return

        # Skip permanent types
        if policy["permanent"]:
            return

        # Evict expired (TTL)
        ttl_days = policy.get("ttl_days")
        if ttl_days is not None:
            cutoff = datetime.now() - timedelta(days=ttl_days)
            try:
                self._repo.delete_expired(cutoff)
            except MemoryError:
                raise
            except Exception:
                pass  # GC failure is non-fatal

        # Enforce max count: evict oldest if over limit
        max_count = policy.get("max")
        if max_count is not None:
            try:
                current_count = self._repo.count(memory_type=memory_type, scope=scope)
            except (MemoryError, Exception):
                return
            # Trigger GC when 100 over max (§8)
            if current_count > max_count + 100:
                entries = self._repo.load_all(memory_type=memory_type, scope=scope)
                # entries already sorted by timestamp desc; oldest = tail
                to_delete = entries[max_count:]
                for entry in to_delete:
                    try:
                        self._repo.delete(str(entry.id))
                    except (MemoryError, Exception):
                        pass  # GC failure is non-fatal

    # ------------------------------------------------------------------
    # Expiry check (MINV-4)
    # ------------------------------------------------------------------

    def _is_expired(self, entry: MemoryEntry, now: datetime) -> bool:
        """Check if entry is past its TTL."""
        policy = _RETENTION_POLICY.get(entry.type.value)
        if policy is None or policy["permanent"]:
            return False
        ttl_days = policy.get("ttl_days")
        if ttl_days is None:
            return False
        cutoff = now - timedelta(days=ttl_days)
        return entry.timestamp < cutoff

    # ------------------------------------------------------------------
    # Grouping / formatting helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _group_by_type(entries: list[MemoryEntry]) -> dict[str, list[MemoryEntry]]:
        """Group entries by MemoryType value."""
        grouped: dict[str, list[MemoryEntry]] = {}
        for entry in entries:
            key = entry.type.value
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(entry)
        return grouped

    def _summarize_brief(self, grouped: dict[str, list[MemoryEntry]]) -> str:
        """Brief summary: count per type, 1-2 sentences."""
        lines = ["Memory Summary (brief)\n"]
        for type_name, entries in grouped.items():
            count = len(entries)
            latest = entries[0].timestamp.strftime("%Y-%m-%d") if entries else "n/a"
            lines.append(
                f"- {type_name}: {count} entries "
                f"(latest: {latest})"
            )
        total = sum(len(e) for e in grouped.values())
        lines.append(f"\nTotal: {total} active entries")
        return "\n".join(lines)

    def _summarize_detailed(self, grouped: dict[str, list[MemoryEntry]]) -> str:
        """Detailed summary: per-type paragraph with recent entries."""
        lines = ["Memory Summary (detailed)\n"]
        for type_name, entries in grouped.items():
            count = len(entries)
            lines.append(f"## {type_name} ({count} entries)")
            # Show up to 5 most recent
            for entry in entries[:5]:
                ts = entry.timestamp.strftime("%Y-%m-%d %H:%M")
                snippet = entry.content[:120].replace("\n", " ")
                lines.append(f"  [{ts}] {snippet}")
            if count > 5:
                lines.append(f"  ... and {count - 5} more")
            lines.append("")
        return "\n".join(lines).rstrip()

    def _summarize_full(
        self,
        grouped: dict[str, list[MemoryEntry]],
        scope: str,
    ) -> str:
        """Full summary: structured markdown report."""
        total = sum(len(e) for e in grouped.values())
        lines = [
            "# Memory Report",
            f"\nScope: {scope}",
            f"Total entries: {total}",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
        ]
        for type_name, entries in grouped.items():
            lines.append(f"## {type_name}")
            lines.append(f"Count: {len(entries)}\n")
            for i, entry in enumerate(entries, 1):
                ts = entry.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                content = entry.content.replace("\n", "\n  ")
                lines.append(f"### Entry {i}")
                lines.append(f"- ID: {entry.id}")
                lines.append(f"- Timestamp: {ts}")
                lines.append(f"- Version: {entry.version}")
                if entry.metadata:
                    lines.append(f"- Metadata: {entry.metadata}")
                lines.append(f"\n  {content}\n")
        return "\n".join(lines).rstrip()
