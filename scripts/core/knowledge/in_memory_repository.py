"""CodeAI Platform — In-Memory Knowledge Repository.

v1 implementation: stores Knowledge items in a list, performs
BM25 + fuzzy search in-memory. No external dependencies.

This is an *internal adapter* — not part of the public API.
"""

from scripts.core.enums import KnowledgeKind
from scripts.core.errors import KnowledgeError
from scripts.core.knowledge.ranking import SearchRanker
from scripts.core.types.knowledge import Knowledge


class InMemoryKnowledgeRepository:
    """In-memory knowledge repository for v1.

    Stores items in a list. Search delegates to SearchRanker.
    """

    def __init__(self) -> None:
        self._items: list[Knowledge] = []
        self._ranker = SearchRanker()

    # ------------------------------------------------------------------
    # KnowledgeRepository interface (CORE_RUNTIME.md §4)
    # ------------------------------------------------------------------

    def search(self, query: str, kind: str | None = None) -> list[Knowledge]:
        """Search knowledge base by text query.

        Uses BM25 + fuzzy matching via SearchRanker.
        """
        if not query:
            return []

        # Filter by kind if specified
        candidates = self._items
        if kind is not None:
            candidates = [i for i in candidates if i.kind.value == kind]

        return self._ranker.rank(query, candidates)

    def index(self, item: Knowledge) -> None:
        """Index a single knowledge item."""
        if not item.source:
            raise KnowledgeError(
                "Cannot index item with empty source",
                code="KLG_INDEX_FAILED",
                recoverable=False,
                context={"item_id": str(item.id)},
            )
        self._items.append(item)

    def index_all(self, items: list[Knowledge]) -> None:
        """Index multiple knowledge items."""
        for item in items:
            self.index(item)

    def count(self) -> int:
        """Return total number of indexed items."""
        return len(self._items)
