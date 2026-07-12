"""CodeAI Platform — Knowledge Layer (stub)."""

from typing import Any

from scripts.core.types import Context, Knowledge, KnowledgeType


class KnowledgeLayer:
    """Knowledge Layer — passive knowledge provider.

    Responsibilities:
        - Search across knowledge base
        - Retrieve context for OODA agents
        - Does NOT make decisions or manage state

    Internal components:
        - MCP (protocol)
        - Obsidian (document storage)
        - OHS (hybrid search: BM25 + fuzzy + vectors)
        - RAG (retrieval augmented generation)
        - GraphRAG (document relationships)
        - Vector DB (embeddings)
        - Docs (articles, theses)

    API:
        search(query, scope) -> list[Knowledge]
        retrieve(context_type, params) -> Context
    """

    def search(self, query: str, scope: str = "all") -> list[Knowledge]:
        """Search knowledge base.

        Args:
            query: Search query.
            scope: Search scope (all, docs, code, references).

        Returns:
            List of Knowledge items sorted by relevance.
        """
        raise NotImplementedError

    def retrieve(self, context_type: KnowledgeType, params: dict[str, Any]) -> Context:
        """Retrieve context of a specific type.

        Args:
            context_type: Type of context (architecture, best_practice, reference).
            params: Additional parameters for retrieval.

        Returns:
            Context with items and summary.
        """
        raise NotImplementedError
