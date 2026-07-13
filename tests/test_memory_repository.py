"""Unit tests for Memory Layer repository layer."""

import json
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from uuid import UUID, uuid4

from scripts.core.enums import MemoryType
from scripts.core.errors import MemoryError
from scripts.core.memory.json_repository import JsonMemoryRepository
from scripts.core.memory.models import MemoryEntry


def _make_entry(
    content: str = "test memory",
    memory_type: MemoryType = MemoryType.DECISIONS,
    scope: str = "project",
    ts: datetime | None = None,
) -> MemoryEntry:
    """Create a MemoryEntry with sensible defaults."""
    return MemoryEntry(
        id=uuid4(),
        type=memory_type,
        content=content,
        timestamp=ts or datetime.now(),
        scope=scope,
        content_hash="abc123",
        version=1,
    )


class TestStoreAndLoad(unittest.TestCase):
    """Test store and load roundtrip."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self._tmp_dir = Path(self._tmp.name)
        self.repo = JsonMemoryRepository(self._tmp_dir)

    def tearDown(self):
        self._tmp.cleanup()

    def test_store_and_load_roundtrip(self):
        entry = _make_entry("first decision")
        self.repo.store(entry)

        loaded = self.repo.load(str(entry.id))
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.id, entry.id)
        self.assertEqual(loaded.content, "first decision")
        self.assertEqual(loaded.type, MemoryType.DECISIONS)
        self.assertEqual(loaded.scope, "project")

    def test_load_nonexistent_returns_none(self):
        self.assertIsNone(self.repo.load(str(uuid4())))

    def test_store_overwrites_existing(self):
        entry = _make_entry("v1")
        self.repo.store(entry)

        updated = MemoryEntry(
            id=entry.id,
            type=entry.type,
            content="v2",
            timestamp=entry.timestamp,
            scope=entry.scope,
            content_hash="def456",
            version=2,
        )
        self.repo.store(updated)

        loaded = self.repo.load(str(entry.id))
        self.assertEqual(loaded.content, "v2")
        self.assertEqual(loaded.version, 2)

    def test_store_global_scope(self):
        entry = _make_entry("global memory", scope="global")
        self.repo.store(entry)

        loaded = self.repo.load(str(entry.id))
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.scope, "global")

    def test_store_multiple_scopes_same_id(self):
        """Same ID stored in different scopes — both persisted."""
        project_entry = _make_entry("project scope", scope="project")
        global_entry = MemoryEntry(
            id=project_entry.id,
            type=project_entry.type,
            content="global scope",
            timestamp=project_entry.timestamp,
            scope="global",
        )
        self.repo.store(project_entry)
        self.repo.store(global_entry)

        # load scans project first, so project version is returned
        loaded = self.repo.load(str(project_entry.id))
        self.assertEqual(loaded.scope, "project")


class TestLoadAll(unittest.TestCase):
    """Test load_all filtering and sorting."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self._tmp_dir = Path(self._tmp.name)
        self.repo = JsonMemoryRepository(self._tmp_dir)

    def tearDown(self):
        self._tmp.cleanup()

    def test_load_all_returns_all_in_scope(self):
        for i in range(5):
            self.repo.store(_make_entry(f"entry {i}"))
        entries = self.repo.load_all(scope="project")
        self.assertEqual(len(entries), 5)

    def test_load_all_sorted_by_timestamp_desc(self):
        now = datetime.now()
        self.repo.store(_make_entry("oldest", ts=now - timedelta(hours=3)))
        self.repo.store(_make_entry("middle", ts=now - timedelta(hours=1)))
        self.repo.store(_make_entry("newest", ts=now))

        entries = self.repo.load_all(scope="project")
        self.assertEqual(
            [e.content for e in entries],
            ["newest", "middle", "oldest"],
        )

    def test_load_all_filters_by_type(self):
        self.repo.store(_make_entry("decision", memory_type=MemoryType.DECISIONS))
        self.repo.store(_make_entry("pattern", memory_type=MemoryType.LEARNED_PATTERNS))
        self.repo.store(_make_entry("another decision", memory_type=MemoryType.DECISIONS))

        decisions = self.repo.load_all(memory_type="decisions", scope="project")
        self.assertEqual(len(decisions), 2)
        self.assertTrue(all(e.type == MemoryType.DECISIONS for e in decisions))

    def test_load_all_empty_scope(self):
        self.assertEqual(self.repo.load_all(scope="empty_scope"), [])

    def test_load_all_does_not_cross_scopes(self):
        self.repo.store(_make_entry("project entry", scope="project"))
        self.repo.store(_make_entry("global entry", scope="global"))

        project_entries = self.repo.load_all(scope="project")
        self.assertEqual(len(project_entries), 1)
        self.assertEqual(project_entries[0].content, "project entry")

        global_entries = self.repo.load_all(scope="global")
        self.assertEqual(len(global_entries), 1)
        self.assertEqual(global_entries[0].content, "global entry")


class TestDelete(unittest.TestCase):
    """Test delete operations."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self._tmp_dir = Path(self._tmp.name)
        self.repo = JsonMemoryRepository(self._tmp_dir)

    def tearDown(self):
        self._tmp.cleanup()

    def test_delete_existing_returns_true(self):
        entry = _make_entry("to delete")
        self.repo.store(entry)
        self.assertTrue(self.repo.delete(str(entry.id)))
        self.assertIsNone(self.repo.load(str(entry.id)))

    def test_delete_nonexistent_returns_false(self):
        self.assertFalse(self.repo.delete(str(uuid4())))

    def test_delete_from_global_scope(self):
        entry = _make_entry("global entry", scope="global")
        self.repo.store(entry)
        self.assertTrue(self.repo.delete(str(entry.id)))
        self.assertIsNone(self.repo.load(str(entry.id)))

    def test_delete_removes_from_all_scopes(self):
        """delete(entry_id) removes from both project and global scopes."""
        entry_id = uuid4()
        self.repo.store(MemoryEntry(
            id=entry_id, type=MemoryType.DECISIONS,
            content="project", timestamp=datetime.now(), scope="project",
        ))
        self.repo.store(MemoryEntry(
            id=entry_id, type=MemoryType.DECISIONS,
            content="global", timestamp=datetime.now(), scope="global",
        ))

        deleted = self.repo.delete(str(entry_id))
        self.assertTrue(deleted)
        # Entry removed from both scopes
        self.assertIsNone(self.repo.load(str(entry_id)))


class TestExistsAndCount(unittest.TestCase):
    """Test exists and count operations."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self._tmp_dir = Path(self._tmp.name)
        self.repo = JsonMemoryRepository(self._tmp_dir)

    def tearDown(self):
        self._tmp.cleanup()

    def test_exists_returns_true_for_stored_entry(self):
        entry = _make_entry()
        self.repo.store(entry)
        self.assertTrue(self.repo.exists(str(entry.id)))

    def test_exists_returns_false_for_missing(self):
        self.assertFalse(self.repo.exists(str(uuid4())))

    def test_count_all_in_scope(self):
        for _ in range(3):
            self.repo.store(_make_entry())
        self.assertEqual(self.repo.count(scope="project"), 3)

    def test_count_filters_by_type(self):
        self.repo.store(_make_entry(memory_type=MemoryType.DECISIONS))
        self.repo.store(_make_entry(memory_type=MemoryType.LEARNED_PATTERNS))
        self.repo.store(_make_entry(memory_type=MemoryType.DECISIONS))

        self.assertEqual(self.repo.count(memory_type="decisions", scope="project"), 2)

    def test_count_empty_scope(self):
        self.assertEqual(self.repo.count(scope="empty"), 0)


class TestDeleteExpired(unittest.TestCase):
    """Test delete_expired operations."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self._tmp_dir = Path(self._tmp.name)
        self.repo = JsonMemoryRepository(self._tmp_dir)

    def tearDown(self):
        self._tmp.cleanup()

    def test_delete_expired_removes_old_entries(self):
        now = datetime.now()
        self.repo.store(_make_entry("old", ts=now - timedelta(days=10)))
        self.repo.store(_make_entry("recent", ts=now - timedelta(hours=1)))

        deleted = self.repo.delete_expired(before=now - timedelta(days=1))
        self.assertEqual(deleted, 1)
        self.assertEqual(self.repo.count(scope="project"), 1)

    def test_delete_expired_no_matches(self):
        now = datetime.now()
        self.repo.store(_make_entry("recent", ts=now))
        deleted = self.repo.delete_expired(before=now - timedelta(days=365))
        self.assertEqual(deleted, 0)

    def test_delete_expired_across_scopes(self):
        now = datetime.now()
        self.repo.store(_make_entry("old project", ts=now - timedelta(days=10), scope="project"))
        self.repo.store(_make_entry("old global", ts=now - timedelta(days=10), scope="global"))

        deleted = self.repo.delete_expired(before=now - timedelta(days=1))
        self.assertEqual(deleted, 2)

    def test_delete_expired_future_timestamp(self):
        future = datetime.now() + timedelta(days=365)
        self.repo.store(_make_entry("future", ts=future))

        deleted = self.repo.delete_expired(before=future + timedelta(days=1))
        self.assertEqual(deleted, 1)


class TestErrorHandling(unittest.TestCase):
    """Test error handling edge cases."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self._tmp_dir = Path(self._tmp.name)
        self.repo = JsonMemoryRepository(self._tmp_dir)

    def tearDown(self):
        self._tmp.cleanup()

    def test_load_nonexistent_id(self):
        result = self.repo.load("nonexistent-id-123")
        self.assertIsNone(result)

    def test_delete_nonexistent_id(self):
        result = self.repo.delete("nonexistent-id-456")
        self.assertFalse(result)


class TestSerialization(unittest.TestCase):
    """Test serialization / deserialization roundtrip."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self._tmp_dir = Path(self._tmp.name)
        self.repo = JsonMemoryRepository(self._tmp_dir)

    def tearDown(self):
        self._tmp.cleanup()

    def test_store_and_load_preserves_all_fields(self):
        entry = MemoryEntry(
            id=uuid4(),
            type=MemoryType.USER_PREFERENCES,
            content="prefer tabs over spaces",
            timestamp=datetime(2025, 6, 15, 10, 30, 0),
            metadata={"source": "user_input"},
            scope="global",
            content_hash="hash123",
            version=3,
        )
        self.repo.store(entry)

        loaded = self.repo.load(str(entry.id))
        self.assertEqual(loaded.id, entry.id)
        self.assertEqual(loaded.type, MemoryType.USER_PREFERENCES)
        self.assertEqual(loaded.content, "prefer tabs over spaces")
        self.assertEqual(loaded.metadata, {"source": "user_input"})
        self.assertEqual(loaded.scope, "global")
        self.assertEqual(loaded.content_hash, "hash123")
        self.assertEqual(loaded.version, 3)

    def test_json_file_structure(self):
        entry = _make_entry("test")
        self.repo.store(entry)

        json_path = self._tmp_dir / "project" / "memory.json"
        self.assertTrue(json_path.exists())

        with open(json_path) as f:
            data = json.load(f)
        self.assertIn(str(entry.id), data)
        self.assertEqual(data[str(entry.id)]["content"], "test")


class TestCorruptFiles(unittest.TestCase):
    """Test handling of corrupt JSON files."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self._tmp_dir = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_load_all_with_corrupt_json(self):
        """Corrupt memory.json should return empty list, not crash."""
        scope_dir = self._tmp_dir / "project"
        scope_dir.mkdir(parents=True)
        (scope_dir / "memory.json").write_text("NOT VALID JSON {{{")

        repo = JsonMemoryRepository(self._tmp_dir)
        entries = repo.load_all(scope="project")
        self.assertEqual(entries, [])

    def test_exists_with_corrupt_json(self):
        scope_dir = self._tmp_dir / "project"
        scope_dir.mkdir(parents=True)
        (scope_dir / "memory.json").write_text("bad json")

        repo = JsonMemoryRepository(self._tmp_dir)
        self.assertFalse(repo.exists(str(uuid4())))

    def test_count_with_corrupt_json(self):
        scope_dir = self._tmp_dir / "project"
        scope_dir.mkdir(parents=True)
        (scope_dir / "memory.json").write_text("[")

        repo = JsonMemoryRepository(self._tmp_dir)
        self.assertEqual(repo.count(scope="project"), 0)


if __name__ == "__main__":
    unittest.main()
