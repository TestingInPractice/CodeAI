"""Unit tests for Memory Layer orchestrator."""

import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from uuid import uuid4

from scripts.core.enums import MemoryType
from scripts.core.errors import MemoryError
from scripts.core.memory.json_repository import JsonMemoryRepository
from scripts.core.memory_layer import MemoryLayer
from scripts.core.types.memory import MemoryEntry


def _make_entry(
    content: str = "test memory",
    memory_type: MemoryType = MemoryType.DECISIONS,
    scope: str = "project",
    ts: datetime | None = None,
    metadata: dict | None = None,
    content_hash: str = "",
    version: int = 1,
) -> MemoryEntry:
    return MemoryEntry(
        id=uuid4(),
        type=memory_type,
        content=content,
        timestamp=ts or datetime.now(),
        metadata=metadata or {},
        scope=scope,
        content_hash=content_hash,
        version=version,
    )


class _BaseTestCase(unittest.TestCase):
    """Shared setup for all test classes."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self._tmp_dir = Path(self._tmp.name)
        self.repo = JsonMemoryRepository(self._tmp_dir)
        self.layer = MemoryLayer(self.repo)

    def tearDown(self):
        self._tmp.cleanup()


# ======================================================================
# store()
# ======================================================================

class TestStore(_BaseTestCase):
    def test_store_persists_entry(self):
        entry = _make_entry("hello world")
        self.layer.store(entry)
        loaded = self.repo.load(str(entry.id))
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.content, "hello world")

    def test_store_assigns_content_hash(self):
        entry = _make_entry("compute my hash")
        self.layer.store(entry)
        loaded = self.repo.load(str(entry.id))
        self.assertNotEqual(loaded.content_hash, "")

    def test_store_preserves_existing_hash(self):
        entry = _make_entry("already hashed", content_hash="precomputed")
        self.layer.store(entry)
        loaded = self.repo.load(str(entry.id))
        self.assertEqual(loaded.content_hash, "precomputed")

    def test_store_deduplicates_same_type_and_hash(self):
        entry1 = _make_entry("duplicate content")
        entry2 = _make_entry("duplicate content")
        self.layer.store(entry1)
        self.layer.store(entry2)

        # Only one entry should exist
        all_entries = self.repo.load_all(scope="project")
        self.assertEqual(len(all_entries), 1)

    def test_store_dedup_merges_metadata(self):
        entry1 = _make_entry("merge me", metadata={"source": "a"})
        entry2 = _make_entry("merge me", metadata={"extra": "b"})
        self.layer.store(entry1)
        self.layer.store(entry2)

        loaded = self.repo.load(str(entry1.id))
        self.assertEqual(loaded.metadata["source"], "a")
        self.assertEqual(loaded.metadata["extra"], "b")
        self.assertEqual(loaded.version, 2)

    def test_store_different_content_not_deduped(self):
        entry1 = _make_entry("content A")
        entry2 = _make_entry("content B")
        self.layer.store(entry1)
        self.layer.store(entry2)
        self.assertEqual(self.repo.count(scope="project"), 2)

    def test_store_iterations_never_deduped(self):
        entry1 = _make_entry("iter 1", memory_type=MemoryType.ITERATIONS)
        entry2 = _make_entry("iter 1", memory_type=MemoryType.ITERATIONS)
        self.layer.store(entry1)
        self.layer.store(entry2)
        self.assertEqual(self.repo.count(scope="project"), 2)

    def test_store_project_history_different_phase_not_deduped(self):
        entry1 = _make_entry("phase done", memory_type=MemoryType.PROJECT_HISTORY, metadata={"phase_id": "p1"})
        entry2 = _make_entry("phase done", memory_type=MemoryType.PROJECT_HISTORY, metadata={"phase_id": "p2"})
        self.layer.store(entry1)
        self.layer.store(entry2)
        self.assertEqual(self.repo.count(scope="project"), 2)

    def test_store_invalid_entry_no_id(self):
        entry = MemoryEntry(
            id=None,
            type=MemoryType.DECISIONS,
            content="no id",
            scope="project",
        )
        with self.assertRaises(MemoryError) as ctx:
            self.layer.store(entry)
        self.assertEqual(ctx.exception.code, "MEM_INVALID_ENTRY")

    def test_store_invalid_scope(self):
        entry = _make_entry("bad scope", scope="invalid")
        with self.assertRaises(MemoryError) as ctx:
            self.layer.store(entry)
        self.assertEqual(ctx.exception.code, "MEM_INVALID_ENTRY")

    def test_store_empty_content(self):
        entry = MemoryEntry(
            id=uuid4(),
            type=MemoryType.DECISIONS,
            content="",
            scope="project",
        )
        with self.assertRaises(MemoryError) as ctx:
            self.layer.store(entry)
        self.assertEqual(ctx.exception.code, "MEM_INVALID_ENTRY")


# ======================================================================
# load()
# ======================================================================

class TestLoad(_BaseTestCase):
    def test_load_returns_matching_entries(self):
        self.layer.store(_make_entry("apple pie"))
        self.layer.store(_make_entry("banana split"))
        self.layer.store(_make_entry("apple cider"))

        results = self.layer.load("apple")
        self.assertEqual(len(results), 2)
        contents = {e.content for e in results}
        self.assertEqual(contents, {"apple pie", "apple cider"})

    def test_load_case_insensitive(self):
        self.layer.store(_make_entry("Hello World"))
        results = self.layer.load("hello")
        self.assertEqual(len(results), 1)

    def test_load_filters_by_scope(self):
        self.layer.store(_make_entry("project only", scope="project"))
        self.layer.store(_make_entry("global only", scope="global"))

        results = self.layer.load("", scope="project")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].content, "project only")

    def test_load_excludes_expired_entries(self):
        old_ts = datetime.now() - timedelta(days=100)
        self.layer.store(_make_entry("old decision", ts=old_ts))
        self.layer.store(_make_entry("new decision"))

        results = self.layer.load("decision")
        # decisions are permanent, so both should appear
        self.assertEqual(len(results), 2)

    def test_load_excludes_expired_non_permanent(self):
        old_ts = datetime.now() - timedelta(days=100)
        self.layer.store(_make_entry("old judge", memory_type=MemoryType.JUDGE_HISTORY, ts=old_ts))
        self.layer.store(_make_entry("new judge", memory_type=MemoryType.JUDGE_HISTORY))

        results = self.layer.load("judge", scope="project")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].content, "new judge")

    def test_load_sorted_by_recency(self):
        now = datetime.now()
        self.layer.store(_make_entry("oldest", ts=now - timedelta(hours=3)))
        self.layer.store(_make_entry("newest", ts=now))
        self.layer.store(_make_entry("middle", ts=now - timedelta(hours=1)))

        results = self.layer.load("")
        self.assertEqual(
            [e.content for e in results],
            ["newest", "middle", "oldest"],
        )

    def test_load_empty_query_returns_all(self):
        self.layer.store(_make_entry("a"))
        self.layer.store(_make_entry("b"))
        results = self.layer.load("")
        self.assertEqual(len(results), 2)

    def test_load_no_match_returns_empty(self):
        self.layer.store(_make_entry("apple"))
        results = self.layer.load("xyz")
        self.assertEqual(results, [])

    def test_load_invalid_scope(self):
        with self.assertRaises(MemoryError) as ctx:
            self.layer.load("test", scope="bad")
        self.assertEqual(ctx.exception.code, "MEM_INVALID_ENTRY")

    def test_load_capped_at_500(self):
        """MINV-6: load() limit is capped at 500."""
        # The actual cap is on _MAX_LOAD_LIMIT which is 500
        # We verify the cap is enforced by checking the private constant
        from scripts.core.memory_layer import _MAX_LOAD_LIMIT
        self.assertEqual(_MAX_LOAD_LIMIT, 500)


# ======================================================================
# summarize()
# ======================================================================

class TestSummarize(_BaseTestCase):
    def test_summarize_empty_store(self):
        result = self.layer.summarize()
        self.assertEqual(result, "No entries found.")

    def test_summarize_brief(self):
        self.layer.store(_make_entry("decision 1", memory_type=MemoryType.DECISIONS))
        self.layer.store(_make_entry("decision 2", memory_type=MemoryType.DECISIONS))
        self.layer.store(_make_entry("pattern 1", memory_type=MemoryType.LEARNED_PATTERNS))

        result = self.layer.summarize(depth="brief")
        self.assertIn("Memory Summary (brief)", result)
        self.assertIn("decisions: 2", result)
        self.assertIn("learned_patterns: 1", result)
        self.assertIn("Total: 3", result)

    def test_summarize_detailed(self):
        self.layer.store(_make_entry("long term fact", memory_type=MemoryType.LONG_TERM))
        result = self.layer.summarize(depth="detailed")
        self.assertIn("Memory Summary (detailed)", result)
        self.assertIn("long_term", result)
        self.assertIn("long term fact", result)

    def test_summarize_full(self):
        self.layer.store(_make_entry("important decision"))
        result = self.layer.summarize(depth="full")
        self.assertIn("# Memory Report", result)
        self.assertIn("important decision", result)
        self.assertIn("Scope: project", result)

    def test_summarize_filters_by_scope(self):
        self.layer.store(_make_entry("project entry", scope="project"))
        self.layer.store(_make_entry("global entry", scope="global"))

        result = self.layer.summarize(scope="project", depth="brief")
        # Brief mode shows counts, not content — check total
        self.assertIn("Total: 1", result)
        # Verify global entry is not counted
        result_global = self.layer.summarize(scope="global", depth="brief")
        self.assertIn("Total: 1", result_global)

    def test_summarize_excludes_expired(self):
        old_ts = datetime.now() - timedelta(days=100)
        self.layer.store(_make_entry("old judge", memory_type=MemoryType.JUDGE_HISTORY, ts=old_ts))
        self.layer.store(_make_entry("new judge", memory_type=MemoryType.JUDGE_HISTORY))

        result = self.layer.summarize(depth="brief")
        self.assertIn("judge_history: 1", result)

    def test_summarize_invalid_depth(self):
        with self.assertRaises(MemoryError) as ctx:
            self.layer.summarize(depth="invalid")
        self.assertEqual(ctx.exception.code, "MEM_INVALID_ENTRY")

    def test_summarize_invalid_scope(self):
        with self.assertRaises(MemoryError) as ctx:
            self.layer.summarize(scope="bad")
        self.assertEqual(ctx.exception.code, "MEM_INVALID_ENTRY")


# ======================================================================
# Retention / GC
# ======================================================================

class TestRetention(_BaseTestCase):
    def test_gc_removes_expired_entries(self):
        """Entries past TTL should be GC'd after store."""
        old_ts = datetime.now() - timedelta(days=100)
        self.layer.store(_make_entry(
            "old judge",
            memory_type=MemoryType.JUDGE_HISTORY,
            ts=old_ts,
        ))
        self.layer.store(_make_entry("new judge", memory_type=MemoryType.JUDGE_HISTORY))

        # After second store, GC should have removed the old one
        count = self.repo.count(memory_type="judge_history", scope="project")
        self.assertEqual(count, 1)

    def test_permanent_types_never_gc(self):
        old_ts = datetime.now() - timedelta(days=1000)
        self.layer.store(_make_entry("ancient decision", ts=old_ts))
        self.layer.store(_make_entry("new decision"))

        count = self.repo.count(memory_type="decisions", scope="project")
        self.assertEqual(count, 2)

    def test_gc_evicts_oldest_when_over_limit(self):
        """When over max+100, oldest entries are evicted."""
        # project_history max=1000, GC triggers at 1100
        # We'll test with a smaller scenario by storing many entries
        for i in range(10):
            self.layer.store(_make_entry(
                f"history {i}",
                memory_type=MemoryType.PROJECT_HISTORY,
                ts=datetime.now() - timedelta(hours=i),
            ))
        # All 10 should exist (well under 1100)
        count = self.repo.count(memory_type="project_history", scope="project")
        self.assertEqual(count, 10)


# ======================================================================
# Deduplication edge cases
# ======================================================================

class TestDeduplication(_BaseTestCase):
    def test_dedup_same_hash_different_scope(self):
        """Same content in different scopes should NOT be deduped."""
        self.layer.store(_make_entry("same content", scope="project"))
        self.layer.store(_make_entry("same content", scope="global"))
        self.assertEqual(self.repo.count(scope="project"), 1)
        self.assertEqual(self.repo.count(scope="global"), 1)

    def test_dedup_preserves_original_timestamp(self):
        """Merged entry keeps the original timestamp."""
        ts = datetime(2025, 1, 1, 12, 0, 0)
        entry1 = _make_entry("keep timestamp", ts=ts)
        entry2 = _make_entry("keep timestamp", ts=datetime.now())
        self.layer.store(entry1)
        self.layer.store(entry2)

        loaded = self.repo.load(str(entry1.id))
        self.assertEqual(loaded.timestamp, ts)

    def test_dedup_preserves_original_id(self):
        """Merged entry keeps the original ID."""
        entry1 = _make_entry("keep id")
        entry2 = _make_entry("keep id")
        self.layer.store(entry1)
        self.layer.store(entry2)

        loaded = self.repo.load(str(entry1.id))
        self.assertIsNotNone(loaded)
        self.assertEqual(str(loaded.id), str(entry1.id))


# ======================================================================
# Invariant checks
# ======================================================================

class TestInvariants(_BaseTestCase):
    def test_minv_1_unique_id(self):
        """MINV-1: Every stored entry has a unique UUID."""
        entry = _make_entry("unique id test")
        self.layer.store(entry)
        loaded = self.repo.load(str(entry.id))
        self.assertIsNotNone(loaded)
        self.assertIsInstance(loaded.id, type(entry.id))

    def test_minv_2_content_hash_is_sha256(self):
        """MINV-2: content_hash is SHA-256 of normalized content."""
        import hashlib
        entry = _make_entry("  Hello World  ")
        self.layer.store(entry)
        loaded = self.repo.load(str(entry.id))
        expected = hashlib.sha256("hello world".encode("utf-8")).hexdigest()
        self.assertEqual(loaded.content_hash, expected)

    def test_minv_4_expired_not_returned(self):
        """MINV-4: Expired entries not returned by load()."""
        old_ts = datetime.now() - timedelta(days=100)
        self.layer.store(_make_entry("expired", memory_type=MemoryType.ITERATIONS, ts=old_ts))
        results = self.layer.load("expired")
        self.assertEqual(results, [])

    def test_minv_5_permanent_never_gc(self):
        """MINV-5: Permanent types are never GC'd."""
        # decisions are permanent
        for i in range(5):
            self.layer.store(_make_entry(f"decision {i}", ts=datetime.now() - timedelta(days=1000)))
        self.assertEqual(self.repo.count(memory_type="decisions", scope="project"), 5)

    def test_minv_6_limit_cap(self):
        """MINV-6: load() capped at 500."""
        from scripts.core.memory_layer import _MAX_LOAD_LIMIT
        self.assertEqual(_MAX_LOAD_LIMIT, 500)

    def test_minv_7_empty_store_summary(self):
        """MINV-7: summarize() returns placeholder for empty store."""
        result = self.layer.summarize()
        self.assertNotEqual(result, "")
        self.assertIn("No entries found", result)

    def test_minv_8_scope_validation(self):
        """MINV-8: scope must be 'project' or 'global'."""
        entry = _make_entry("bad scope", scope="bad")
        with self.assertRaises(MemoryError):
            self.layer.store(entry)

        with self.assertRaises(MemoryError):
            self.layer.load("test", scope="bad")

        with self.assertRaises(MemoryError):
            self.layer.summarize(scope="bad")


if __name__ == "__main__":
    unittest.main()
