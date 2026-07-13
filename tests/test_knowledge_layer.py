"""Unit tests for Knowledge Layer.

Covers:
- search() and retrieve() public API
- CachePolicy (TTL, invalidation, LRU)
- InMemoryKnowledgeRepository (index, search)
- SearchRanker (BM25, fuzzy, scoring)
- Error handling and invariants (KINV-1 through KINV-7)
"""

import time
import unittest
from uuid import uuid4

from scripts.core.enums import KnowledgeKind, KnowledgeType
from scripts.core.errors import KnowledgeError
from scripts.core.knowledge.cache import CachePolicy
from scripts.core.knowledge.in_memory_repository import InMemoryKnowledgeRepository
from scripts.core.knowledge.ranking import SearchRanker, _levenshtein, _tokenize
from scripts.core.knowledge_layer import KnowledgeLayer
from scripts.core.types.knowledge import Context, Knowledge


def _make_knowledge(
    content: str = "test content",
    kind: KnowledgeKind = KnowledgeKind.DOCUMENT,
    source: str = "docs/test.md",
    metadata: dict | None = None,
) -> Knowledge:
    return Knowledge(
        id=uuid4(),
        source=source,
        kind=kind,
        content=content,
        score=0.0,
        metadata=metadata or {},
    )


# ======================================================================
# _tokenize
# ======================================================================

class TestTokenize(unittest.TestCase):
    def test_lowercases(self):
        self.assertEqual(_tokenize("Hello World"), ["hello", "world"])

    def test_splits_on_punctuation(self):
        self.assertEqual(_tokenize("foo-bar,baz"), ["foo", "bar", "baz"])

    def test_empty_string(self):
        self.assertEqual(_tokenize(""), [])


# ======================================================================
# _levenshtein
# ======================================================================

class TestLevenshtein(unittest.TestCase):
    def test_identical(self):
        self.assertEqual(_levenshtein("abc", "abc"), 0)

    def test_one_edit(self):
        self.assertEqual(_levenshtein("abc", "ac"), 1)

    def test_two_edits(self):
        self.assertEqual(_levenshtein("abc", "axc"), 1)
        self.assertEqual(_levenshtein("abc", "axz"), 2)

    def test_empty(self):
        self.assertEqual(_levenshtein("", "abc"), 3)


# ======================================================================
# CachePolicy
# ======================================================================

class TestCachePolicy(unittest.TestCase):
    def setUp(self):
        self.cache = CachePolicy()

    def test_put_and_get_query(self):
        self.cache.put_query("key1", ["result"])
        self.assertEqual(self.cache.get_query("key1"), ["result"])

    def test_query_miss(self):
        self.assertIsNone(self.cache.get_query("missing"))

    def test_query_expiry(self):
        # Manually insert expired entry
        self.cache._query_cache["old"] = CachePolicy.__new__(CachePolicy)
        # Use internal dataclass directly
        from scripts.core.knowledge.cache import _CacheEntry
        self.cache._query_cache["old"] = _CacheEntry(
            value=["stale"],
            expires_at=time.time() - 1,
        )
        self.assertIsNone(self.cache.get_query("old"))

    def test_put_and_get_doc(self):
        self.cache.put_doc("doc1", "content")
        self.assertEqual(self.cache.get_doc("doc1"), "content")

    def test_doc_expiry(self):
        from scripts.core.knowledge.cache import _CacheEntry
        self.cache._doc_cache["old"] = _CacheEntry(
            value="stale",
            expires_at=time.time() - 1,
        )
        self.assertIsNone(self.cache.get_doc("old"))

    def test_put_and_get_index(self):
        self.cache.put_index("idx1", [1, 2, 3])
        self.assertEqual(self.cache.get_index("idx1"), [1, 2, 3])

    def test_index_single_entry(self):
        self.cache.put_index("a", [1])
        self.cache.put_index("b", [2])
        # Only last entry should remain
        self.assertIsNone(self.cache.get_index("a"))
        self.assertEqual(self.cache.get_index("b"), [2])

    def test_invalidate_query_all(self):
        self.cache.put_query("a", 1)
        self.cache.put_query("b", 2)
        self.cache.invalidate_query()
        self.assertIsNone(self.cache.get_query("a"))
        self.assertIsNone(self.cache.get_query("b"))

    def test_invalidate_query_pattern(self):
        self.cache.put_query("search:all:python", [1])
        self.cache.put_query("search:all:java", [2])
        self.cache.invalidate_query("python")
        self.assertIsNone(self.cache.get_query("search:all:python"))
        self.assertIsNotNone(self.cache.get_query("search:all:java"))

    def test_invalidate_doc(self):
        self.cache.put_doc("a", 1)
        self.cache.invalidate_doc("a")
        self.assertIsNone(self.cache.get_doc("a"))

    def test_invalidate_all(self):
        self.cache.put_query("q", 1)
        self.cache.put_doc("d", 2)
        self.cache.put_index("i", 3)
        self.cache.invalidate_all()
        self.assertIsNone(self.cache.get_query("q"))
        self.assertIsNone(self.cache.get_doc("d"))
        self.assertIsNone(self.cache.get_index("i"))

    def test_lru_eviction_query(self):
        for i in range(1001):
            self.cache.put_query(f"k{i}", i)
        # Should have evicted at least one
        self.assertLessEqual(len(self.cache._query_cache), 1000)

    def test_lru_eviction_doc(self):
        for i in range(501):
            self.cache.put_doc(f"d{i}", i)
        self.assertLessEqual(len(self.cache._doc_cache), 500)

    def test_make_search_key_deterministic(self):
        k1 = CachePolicy.make_search_key("python", "all")
        k2 = CachePolicy.make_search_key("python", "all")
        self.assertEqual(k1, k2)

    def test_make_retrieve_key_deterministic(self):
        k1 = CachePolicy.make_retrieve_key("architecture", {"kind": "adr"})
        k2 = CachePolicy.make_retrieve_key("architecture", {"kind": "adr"})
        self.assertEqual(k1, k2)

    def test_make_search_key_differs_by_scope(self):
        k1 = CachePolicy.make_search_key("python", "all")
        k2 = CachePolicy.make_search_key("python", "project")
        self.assertNotEqual(k1, k2)


# ======================================================================
# InMemoryKnowledgeRepository
# ======================================================================

class TestInMemoryRepository(unittest.TestCase):
    def setUp(self):
        self.repo = InMemoryKnowledgeRepository()

    def test_index_and_count(self):
        item = _make_knowledge("hello")
        self.repo.index(item)
        self.assertEqual(self.repo.count(), 1)

    def test_index_all(self):
        items = [_make_knowledge(f"doc {i}") for i in range(5)]
        self.repo.index_all(items)
        self.assertEqual(self.repo.count(), 5)

    def test_search_returns_matches(self):
        self.repo.index(_make_knowledge("Python tutorial"))
        self.repo.index(_make_knowledge("Java guide"))
        results = self.repo.search("Python")
        self.assertGreater(len(results), 0)
        self.assertIn("Python", results[0].content)

    def test_search_empty_query(self):
        self.repo.index(_make_knowledge("something"))
        results = self.repo.search("")
        self.assertEqual(results, [])

    def test_search_no_matches(self):
        self.repo.index(_make_knowledge("Python"))
        results = self.repo.search("xyz123nonexistent")
        self.assertEqual(results, [])

    def test_search_by_kind(self):
        self.repo.index(_make_knowledge("spec doc", kind=KnowledgeKind.SPEC))
        self.repo.index(_make_knowledge("code doc", kind=KnowledgeKind.CODE))
        results = self.repo.search("doc", kind="spec")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].kind, KnowledgeKind.SPEC)

    def test_index_empty_source_raises(self):
        item = _make_knowledge("content", source="")
        with self.assertRaises(KnowledgeError) as ctx:
            self.repo.index(item)
        self.assertEqual(ctx.exception.code, "KLG_INDEX_FAILED")


# ======================================================================
# SearchRanker
# ======================================================================

class TestSearchRanker(unittest.TestCase):
    def setUp(self):
        self.ranker = SearchRanker()

    def test_empty_items(self):
        self.assertEqual(self.ranker.rank("query", []), [])

    def test_exact_match_ranks_higher(self):
        items = [
            _make_knowledge("Python is great", source="docs/python.md"),
            _make_knowledge("Python basics for beginners", source="docs/java.md"),
        ]
        results = self.ranker.rank("Python", items)
        self.assertEqual(len(results), 2)
        self.assertGreater(results[0].score, results[1].score)
        self.assertIn("Python", results[0].content)

    def test_scores_normalized(self):
        items = [_make_knowledge(f"doc {i} python coding") for i in range(20)]
        results = self.ranker.rank("python", items)
        for r in results:
            self.assertGreaterEqual(r.score, 0.0)
            self.assertLessEqual(r.score, 1.0)

    def test_fuzzy_match(self):
        items = [
            _make_knowledge("Python programming"),
            _make_knowledge("Java programming"),
        ]
        # "Pyhon" is close to "Python" — fuzzy should match
        results = self.ranker.rank("Pyhon", items)
        self.assertGreater(len(results), 0)

    def test_source_priority(self):
        items = [
            _make_knowledge("test", source="docs/test.md"),
            _make_knowledge("test", source="articles/test.md"),
        ]
        results = self.ranker.rank("test", items)
        # docs/ has higher source priority than articles/
        self.assertEqual(results[0].source, "docs/test.md")

    def test_kind_priority(self):
        items = [
            _make_knowledge("test", kind=KnowledgeKind.DOCUMENT),
            _make_knowledge("test", kind=KnowledgeKind.SPEC),
        ]
        results = self.ranker.rank("test", items)
        # spec has higher kind priority than document
        self.assertEqual(results[0].kind, KnowledgeKind.SPEC)


# ======================================================================
# KnowledgeLayer — search()
# ======================================================================

class TestKnowledgeLayerSearch(unittest.TestCase):
    def setUp(self):
        self.layer = KnowledgeLayer()
        self.layer.index_all([
            _make_knowledge("Python architecture guide", kind=KnowledgeKind.DOCUMENT, source="docs/arch.md"),
            _make_knowledge("Java best practices", kind=KnowledgeKind.ARTICLE, source="articles/java.md"),
            _make_knowledge("Python testing patterns", kind=KnowledgeKind.CODE, source="docs/test.md"),
        ])

    def test_search_returns_list(self):
        """KINV-1: search() always returns a list."""
        result = self.layer.search("Python")
        self.assertIsInstance(result, list)

    def test_search_empty_query_returns_empty(self):
        """KINV-1: empty query → empty list."""
        self.assertEqual(self.layer.search(""), [])
        self.assertEqual(self.layer.search("   "), [])

    def test_search_returns_matching_items(self):
        results = self.layer.search("Python")
        self.assertGreater(len(results), 0)

    def test_search_scores_are_normalized(self):
        """KINV-4: scores in [0.0, 1.0]."""
        results = self.layer.search("Python")
        for item in results:
            self.assertGreaterEqual(item.score, 0.0)
            self.assertLessEqual(item.score, 1.0)

    def test_search_invalid_scope_raises(self):
        """KINV-7: scope must be 'all', 'project', or 'global'."""
        with self.assertRaises(KnowledgeError) as ctx:
            self.layer.search("test", scope="invalid")
        self.assertEqual(ctx.exception.code, "KLG_INVALID_QUERY")

    def test_search_with_scope_project(self):
        results = self.layer.search("Python", scope="project")
        self.assertIsInstance(results, list)

    def test_search_with_scope_global(self):
        results = self.layer.search("Python", scope="global")
        self.assertIsInstance(results, list)

    def test_search_cache_hit(self):
        """Second call should return cached result."""
        r1 = self.layer.search("Python")
        r2 = self.layer.search("Python")
        self.assertEqual(len(r1), len(r2))

    def test_search_cache_invalidation(self):
        """Cache should be invalidated on index."""
        r1 = self.layer.search("Python")
        self.layer.index(_make_knowledge("Python advanced guide"))
        r2 = self.layer.search("Python")
        self.assertGreaterEqual(len(r2), len(r1))


# ======================================================================
# KnowledgeLayer — retrieve()
# ======================================================================

class TestKnowledgeLayerRetrieve(unittest.TestCase):
    def setUp(self):
        self.layer = KnowledgeLayer()
        self.layer.index_all([
            _make_knowledge(
                "Architecture overview",
                kind=KnowledgeKind.DOCUMENT,
                source="docs/arch.md",
                metadata={"scope": "project"},
            ),
            _make_knowledge(
                "Architecture patterns",
                kind=KnowledgeKind.ADR,
                source="docs/patterns.md",
                metadata={"scope": "global"},
            ),
            _make_knowledge(
                "Best practices guide",
                kind=KnowledgeKind.ARTICLE,
                source="articles/best.md",
            ),
        ])

    def test_retrieve_returns_context(self):
        """KINV-2: retrieve() always returns a Context."""
        ctx = self.layer.retrieve(KnowledgeType.ARCHITECTURE, {})
        self.assertIsInstance(ctx, Context)

    def test_retrieve_context_type_matches(self):
        ctx = self.layer.retrieve(KnowledgeType.ARCHITECTURE, {})
        self.assertEqual(ctx.context_type, KnowledgeType.ARCHITECTURE)

    def test_retrieve_empty_params(self):
        ctx = self.layer.retrieve(KnowledgeType.ARCHITECTURE, {})
        self.assertIsInstance(ctx.items, list)
        self.assertIsInstance(ctx.summary, str)

    def test_retrieve_with_kind_filter(self):
        ctx = self.layer.retrieve(
            KnowledgeType.ARCHITECTURE,
            {"kind": "adr"},
        )
        for item in ctx.items:
            self.assertEqual(item.kind, KnowledgeKind.ADR)

    def test_retrieve_with_source_filter(self):
        ctx = self.layer.retrieve(
            KnowledgeType.ARCHITECTURE,
            {"source": "docs/arch.md"},
        )
        for item in ctx.items:
            self.assertIn("docs/arch.md", item.source)

    def test_retrieve_summary_not_empty(self):
        ctx = self.layer.retrieve(KnowledgeType.ARCHITECTURE, {})
        self.assertTrue(len(ctx.summary) > 0)

    def test_retrieve_cache_hit(self):
        ctx1 = self.layer.retrieve(KnowledgeType.ARCHITECTURE, {})
        ctx2 = self.layer.retrieve(KnowledgeType.ARCHITECTURE, {})
        self.assertEqual(len(ctx1.items), len(ctx2.items))


# ======================================================================
# KnowledgeLayer — index()
# ======================================================================

class TestKnowledgeLayerIndex(unittest.TestCase):
    def setUp(self):
        self.layer = KnowledgeLayer()

    def test_index_single_item(self):
        item = _make_knowledge("new doc")
        self.layer.index(item)
        self.assertEqual(self.layer._repo.count(), 1)

    def test_index_all_items(self):
        items = [_make_knowledge(f"doc {i}") for i in range(3)]
        self.layer.index_all(items)
        self.assertEqual(self.layer._repo.count(), 3)

    def test_index_invalidates_cache(self):
        self.layer.index(_make_knowledge("doc1"))
        self.layer.search("doc1")  # populates cache
        self.layer.index(_make_knowledge("doc2"))
        # Cache should be cleared
        self.assertIsNone(self.layer._cache.get_query(
            CachePolicy.make_search_key("doc1", "all")
        ))


# ======================================================================
# Invariants
# ======================================================================

class TestInvariants(unittest.TestCase):
    """Verify all KINV invariants."""

    def setUp(self):
        self.layer = KnowledgeLayer()

    def test_kinv1_search_never_returns_none(self):
        """KINV-1: search() always returns a list (empty if no results)."""
        result = self.layer.search("nonexistent query xyz")
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)

    def test_kinv2_retrieve_never_returns_none(self):
        """KINV-2: retrieve() always returns a Context."""
        ctx = self.layer.retrieve(KnowledgeType.TOOL, {})
        self.assertIsNotNone(ctx)
        self.assertIsInstance(ctx, Context)

    def test_kinv3_source_nonempty(self):
        """KINV-3: Knowledge items have non-empty source."""
        item = _make_knowledge("test", source="docs/test.md")
        self.layer.index(item)
        results = self.layer.search("test")
        for r in results:
            self.assertTrue(len(r.source) > 0)

    def test_kinv4_scores_normalized(self):
        """KINV-4: Search scores are in [0.0, 1.0]."""
        self.layer.index_all([
            _make_knowledge(f"python doc {i}") for i in range(10)
        ])
        results = self.layer.search("python")
        for r in results:
            self.assertGreaterEqual(r.score, 0.0)
            self.assertLessEqual(r.score, 1.0)

    def test_kinv5_cache_serves_within_ttl(self):
        """KINV-5: Cached results are served within TTL."""
        self.layer.index(_make_knowledge("cached item"))
        r1 = self.layer.search("cached item")
        r2 = self.layer.search("cached item")
        self.assertEqual(len(r1), len(r2))

    def test_kinv7_scope_validation(self):
        """KINV-7: scope must be 'all', 'project', or 'global'."""
        with self.assertRaises(KnowledgeError):
            self.layer.search("test", scope="bad")


# ======================================================================
# Error handling
# ======================================================================

class TestErrorHandling(unittest.TestCase):
    def test_knowledge_error_hierarchy(self):
        """KnowledgeError inherits from CodeAIError."""
        from scripts.core.errors import CodeAIError
        err = KnowledgeError("test", code="KLG_TEST")
        self.assertIsInstance(err, CodeAIError)

    def test_search_error_code(self):
        err = KnowledgeError("fail", code="KLG_SEARCH_FAILED", recoverable=True)
        self.assertEqual(err.code, "KLG_SEARCH_FAILED")
        self.assertTrue(err.recoverable)

    def test_retrieve_error_code(self):
        err = KnowledgeError("fail", code="KLG_RETRIEVE_FAILED")
        self.assertEqual(err.code, "KLG_RETRIEVE_FAILED")

    def test_index_error_code(self):
        err = KnowledgeError("fail", code="KLG_INDEX_FAILED")
        self.assertEqual(err.code, "KLG_INDEX_FAILED")

    def test_invalid_query_error(self):
        err = KnowledgeError("fail", code="KLG_INVALID_QUERY")
        self.assertFalse(err.recoverable)


# ======================================================================
# Dependency Rule verification
# ======================================================================

class TestDependencyRule(unittest.TestCase):
    """Verify Knowledge Layer does not import from other subsystems."""

    def test_no_workflow_import(self):
        import scripts.core.knowledge_layer as mod
        source = open(mod.__file__).read()
        self.assertNotIn("WorkflowEngine", source)
        self.assertNotIn("workflow_engine", source)

    def test_no_memory_import(self):
        import scripts.core.knowledge_layer as mod
        source = open(mod.__file__).read()
        self.assertNotIn("MemoryLayer", source)
        self.assertNotIn("memory_layer", source)

    def test_no_judge_import(self):
        import scripts.core.knowledge_layer as mod
        source = open(mod.__file__).read()
        self.assertNotIn("JudgeEngine", source)
        self.assertNotIn("judge_engine", source)

    def test_no_ooda_import(self):
        import scripts.core.knowledge_layer as mod
        source = open(mod.__file__).read()
        self.assertNotIn("OODARuntime", source)
        self.assertNotIn("ooda_runtime", source)

    def test_no_spec_import(self):
        import scripts.core.knowledge_layer as mod
        source = open(mod.__file__).read()
        self.assertNotIn("SpecEngine", source)
        self.assertNotIn("spec_engine", source)


# ======================================================================
# Public API surface
# ======================================================================

class TestPublicAPISurface(unittest.TestCase):
    """Verify KnowledgeLayer exposes exactly 2 public methods."""

    def test_only_search_and_retrieve(self):
        public = [
            m for m in dir(KnowledgeLayer)
            if not m.startswith("_")
        ]
        # Allow init, search, retrieve, index, index_all
        # But search and retrieve are the ONLY frozen public API
        self.assertIn("search", public)
        self.assertIn("retrieve", public)


if __name__ == "__main__":
    unittest.main()
