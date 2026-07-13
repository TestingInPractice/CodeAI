"""CodeAI Platform — Cache Policy.

In-memory TTL-based cache for Knowledge Layer results.
Matches DESIGN §13 exactly.

This is an *internal adapter* — not part of the public API.
"""

import hashlib
import time
from dataclasses import dataclass, field
from typing import Any


# TTL constants (seconds) from DESIGN §13
_QUERY_TTL = 300       # 5 minutes
_DOC_TTL = 1800        # 30 minutes
_INDEX_TTL = 3600      # 1 hour
_MAX_QUERY_ENTRIES = 1000
_MAX_DOC_ENTRIES = 500


@dataclass
class _CacheEntry:
    """Single cache entry with TTL."""
    value: Any
    expires_at: float


class CachePolicy:
    """TTL-based in-memory cache.

    Three layers per DESIGN §13:
    - query_cache: per query string, 5 min TTL
    - doc_cache: per document path, 30 min TTL
    - index_cache: full index, 1 hour TTL

    Cache is lost on restart — acceptable for v1 single-process.
    """

    def __init__(self) -> None:
        self._query_cache: dict[str, _CacheEntry] = {}
        self._doc_cache: dict[str, _CacheEntry] = {}
        self._index_cache: dict[str, _CacheEntry] = {}

    # ------------------------------------------------------------------
    # Query cache (search / retrieve results)
    # ------------------------------------------------------------------

    def get_query(self, key: str) -> Any | None:
        """Get cached query result. Returns None on miss or expiry."""
        entry = self._query_cache.get(key)
        if entry is None:
            return None
        if time.time() > entry.expires_at:
            del self._query_cache[key]
            return None
        return entry.value

    def put_query(self, key: str, value: Any) -> None:
        """Store query result with TTL."""
        if len(self._query_cache) >= _MAX_QUERY_ENTRIES:
            self._evict_oldest(self._query_cache)
        self._query_cache[key] = _CacheEntry(
            value=value,
            expires_at=time.time() + _QUERY_TTL,
        )

    # ------------------------------------------------------------------
    # Document cache
    # ------------------------------------------------------------------

    def get_doc(self, key: str) -> Any | None:
        """Get cached document. Returns None on miss or expiry."""
        entry = self._doc_cache.get(key)
        if entry is None:
            return None
        if time.time() > entry.expires_at:
            del self._doc_cache[key]
            return None
        return entry.value

    def put_doc(self, key: str, value: Any) -> None:
        """Store document with TTL."""
        if len(self._doc_cache) >= _MAX_DOC_ENTRIES:
            self._evict_oldest(self._doc_cache)
        self._doc_cache[key] = _CacheEntry(
            value=value,
            expires_at=time.time() + _DOC_TTL,
        )

    # ------------------------------------------------------------------
    # Index cache
    # ------------------------------------------------------------------

    def get_index(self, key: str) -> Any | None:
        """Get cached index. Returns None on miss or expiry."""
        entry = self._index_cache.get(key)
        if entry is None:
            return None
        if time.time() > entry.expires_at:
            del self._index_cache[key]
            return None
        return entry.value

    def put_index(self, key: str, value: Any) -> None:
        """Store index with TTL. Only one entry allowed."""
        self._index_cache.clear()
        self._index_cache[key] = _CacheEntry(
            value=value,
            expires_at=time.time() + _INDEX_TTL,
        )

    # ------------------------------------------------------------------
    # Invalidation (DESIGN §13.3)
    # ------------------------------------------------------------------

    def invalidate_query(self, pattern: str = "") -> None:
        """Invalidate query cache entries matching pattern."""
        if not pattern:
            self._query_cache.clear()
            return
        keys_to_remove = [k for k in self._query_cache if pattern in k]
        for k in keys_to_remove:
            del self._query_cache[k]

    def invalidate_doc(self, pattern: str = "") -> None:
        """Invalidate doc cache entries matching pattern."""
        if not pattern:
            self._doc_cache.clear()
            return
        keys_to_remove = [k for k in self._doc_cache if pattern in k]
        for k in keys_to_remove:
            del self._doc_cache[k]

    def invalidate_all(self) -> None:
        """Invalidate all caches."""
        self._query_cache.clear()
        self._doc_cache.clear()
        self._index_cache.clear()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def make_search_key(query: str, scope: str) -> str:
        """Build deterministic cache key for search."""
        raw = f"search:{scope}:{query}"
        return hashlib.sha256(raw.encode()).hexdigest()[:32]

    @staticmethod
    def make_retrieve_key(context_type: str, params: dict[str, Any]) -> str:
        """Build deterministic cache key for retrieve."""
        params_str = str(sorted(params.items()))
        raw = f"retrieve:{context_type}:{params_str}"
        return hashlib.sha256(raw.encode()).hexdigest()[:32]

    @staticmethod
    def _evict_oldest(cache: dict[str, _CacheEntry]) -> None:
        """Remove the entry with earliest expiry (LRU-like)."""
        if not cache:
            return
        oldest_key = min(cache, key=lambda k: cache[k].expires_at)
        del cache[oldest_key]
