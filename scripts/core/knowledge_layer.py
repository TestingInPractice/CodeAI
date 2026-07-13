"""CodeAI Platform — Knowledge Layer.

Orchestrator for knowledge retrieval. Sits on top of KnowledgeRepository,
CachePolicy, and SearchRanker. No file I/O, no MCP, no Obsidian — all
delegated to injected adapters.

Public API matches CORE_RUNTIME.md §2.4 exactly:
    search(query: str, scope: str = "all") -> list[Knowledge]
    retrieve(context_type: KnowledgeType, params: dict[str, Any]) -> Context
"""

from typing import Any

from scripts.core.enums import KnowledgeType
from scripts.core.errors import KnowledgeError
from scripts.core.knowledge.cache import CachePolicy
from scripts.core.knowledge.in_memory_repository import InMemoryKnowledgeRepository
from scripts.core.knowledge.ranking import SearchRanker
from scripts.core.types.knowledge import Context, Knowledge

# Valid scopes (DESIGN §5)
_VALID_SCOPES = ("all", "project", "global")

# Context summary templates (DESIGN §10.3)
_MAX_CONTEXT_ITEMS = 10


class KnowledgeLayer:
    """Knowledge Layer — passive knowledge provider.

    Responsibilities (DESIGN §3):
    - Search across knowledge base
    - Retrieve context for OODA agents
    - Index documents
    - Cache results

    Does NOT:
    - Make decisions (Judge Engine)
    - Manage state (Workflow Engine)
    - Access filesystem directly (Repository Pattern)
    - Access MCP directly (Transport Layer)
    - Access Obsidian directly (Transport Layer)
    - Know about Memory Layer (independent subsystem)
    - Execute LLM generation (caller's job)
    """

    def __init__(
        self,
        repository: InMemoryKnowledgeRepository | None = None,
        cache: CachePolicy | None = None,
    ) -> None:
        """Initialize with injected adapters.

        Args:
            repository: Knowledge persistence (default: InMemoryKnowledgeRepository).
            cache: Cache policy (default: CachePolicy).
        """
        self._repo = repository or InMemoryKnowledgeRepository()
        self._cache = cache or CachePolicy()
        self._ranker = SearchRanker()

    # ------------------------------------------------------------------
    # Public API (frozen — CORE_RUNTIME.md §2.4)
    # ------------------------------------------------------------------

    def search(self, query: str, scope: str = "all") -> list[Knowledge]:
        """Search knowledge base by text query.

        Performs hybrid search: BM25 + fuzzy matching.
        Returns results sorted by relevance score.

        Args:
            query: Text to search for.
            scope: Filter by scope ("all", "project", "global").

        Returns:
            List of matching Knowledge items, sorted by score desc.

        Raises:
            KnowledgeError: On invalid input or repository failure.
        """
        # KINV-7: validate scope
        self._validate_scope(scope)

        # KINV-1: never return None
        if not query or not query.strip():
            return []

        # Check cache (DESIGN §13)
        cache_key = CachePolicy.make_search_key(query, scope)
        cached = self._cache.get_query(cache_key)
        if cached is not None:
            return cached

        try:
            # Delegate to repository → ranker
            results = self._repo.search(query)
        except KnowledgeError:
            raise
        except Exception as e:
            raise KnowledgeError(
                f"Search failed: {e}",
                code="KLG_SEARCH_FAILED",
                recoverable=True,
                context={"query": query, "scope": scope, "cause": str(e)},
                cause=e,
            ) from e

        # Apply scope filter
        if scope != "all":
            results = self._filter_by_scope(results, scope)

        # Cache results (DESIGN §13)
        self._cache.put_query(cache_key, results)

        return results

    def retrieve(
        self,
        context_type: KnowledgeType,
        params: dict[str, Any],
    ) -> Context:
        """Retrieve structured context for a specific knowledge type.

        Returns all knowledge of the given type, filtered by params.

        Args:
            context_type: Type of knowledge to retrieve.
            params: Filters (kind, source, after, before). Pass {} for no filters.

        Returns:
            Context with items and summary.

        Raises:
            KnowledgeError: On invalid input or repository failure.
        """
        # Check cache
        cache_key = CachePolicy.make_retrieve_key(context_type.value, params)
        cached = self._cache.get_query(cache_key)
        if cached is not None:
            return cached

        try:
            # Extract kind filter from params
            kind_filter = params.get("kind")
            source_filter = params.get("source")

            # Search repository for items matching context type
            if kind_filter:
                all_items = self._repo.search(context_type.value, kind=kind_filter)
            else:
                all_items = self._repo.search(context_type.value)

            # Apply additional filters
            items = self._apply_retrieve_filters(all_items, params)

            # Build Context (KINV-2: never return None)
            context = Context(
                context_type=context_type,
                items=items[:_MAX_CONTEXT_ITEMS],
                summary=self._build_summary(items, context_type),
            )

            # Cache
            self._cache.put_query(cache_key, context)

            return context

        except KnowledgeError:
            raise
        except Exception as e:
            raise KnowledgeError(
                f"Retrieve failed: {e}",
                code="KLG_RETRIEVE_FAILED",
                recoverable=True,
                context={
                    "context_type": context_type.value,
                    "params": params,
                    "cause": str(e),
                },
                cause=e,
            ) from e

    # ------------------------------------------------------------------
    # Indexing (called by transport adapters, not public API)
    # ------------------------------------------------------------------

    def index(self, item: Knowledge) -> None:
        """Index a knowledge item (internal, not public API).

        Args:
            item: Knowledge item to index.

        Raises:
            KnowledgeError: If indexing fails.
        """
        try:
            self._repo.index(item)
        except KnowledgeError:
            raise
        except Exception as e:
            raise KnowledgeError(
                f"Index failed: {e}",
                code="KLG_INDEX_FAILED",
                recoverable=True,
                context={"item_id": str(item.id)},
                cause=e,
            ) from e
        # Invalidate caches on mutation
        self._cache.invalidate_all()

    def index_all(self, items: list[Knowledge]) -> None:
        """Index multiple knowledge items (internal).

        Args:
            items: List of Knowledge items to index.
        """
        try:
            self._repo.index_all(items)
        except KnowledgeError:
            raise
        except Exception as e:
            raise KnowledgeError(
                f"Index failed: {e}",
                code="KLG_INDEX_FAILED",
                recoverable=True,
                context={"count": len(items)},
                cause=e,
            ) from e
        self._cache.invalidate_all()

    # ------------------------------------------------------------------
    # Validation (KINV-7)
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_scope(scope: str) -> None:
        """Validate scope parameter (KINV-7)."""
        if scope not in _VALID_SCOPES:
            raise KnowledgeError(
                f"Invalid scope: {scope!r} (must be 'all', 'project', or 'global')",
                code="KLG_INVALID_QUERY",
                recoverable=False,
                context={"field": "scope", "value": scope},
            )

    # ------------------------------------------------------------------
    # Filtering
    # ------------------------------------------------------------------

    @staticmethod
    def _filter_by_scope(items: list[Knowledge], scope: str) -> list[Knowledge]:
        """Filter items by scope field in metadata."""
        filtered = []
        for item in items:
            item_scope = item.metadata.get("scope", "all")
            if item_scope == scope or item_scope == "all":
                filtered.append(item)
        return filtered

    @staticmethod
    def _apply_retrieve_filters(
        items: list[Knowledge], params: dict[str, Any]
    ) -> list[Knowledge]:
        """Apply retrieve-specific filters from params dict."""
        result = list(items)

        source = params.get("source")
        if source:
            result = [i for i in result if source in i.source]

        after = params.get("after")
        if after is not None:
            # Filter by date in metadata
            result = [
                i for i in result
                if i.metadata.get("date", "") >= str(after)
            ]

        before = params.get("before")
        if before is not None:
            result = [
                i for i in result
                if i.metadata.get("date", "") <= str(before)
            ]

        return result

    # ------------------------------------------------------------------
    # Summary (DESIGN §10.3)
    # ------------------------------------------------------------------

    @staticmethod
    def _build_summary(items: list[Knowledge], context_type: KnowledgeType) -> str:
        """Build a brief summary for a Context."""
        if not items:
            return f"No {context_type.value} knowledge found."

        # Collect unique kinds
        kinds = sorted(set(i.kind.value for i in items))
        # Collect unique sources
        sources = sorted(set(i.source for i in items))

        lines = [
            f"Found {len(items)} {context_type.value} items.",
            f"Kinds: {', '.join(kinds)}.",
            f"Sources: {len(sources)} unique.",
        ]
        return " ".join(lines)
