"""CodeAI Platform — Memory Layer (stub)."""

from scripts.core.types import MemoryEntry


class MemoryLayer:
    """Memory Layer — history and learned patterns.

    Responsibilities:
        - Store project history, judge decisions, iterations
        - Store ADR decisions, long-term memory
        - Store user preferences, learned patterns
        - Provide summarization of memory

    Note: Separated from Knowledge Layer because memory is not only
    knowledge — it's also history, context, and patterns.

    API:
        store(entry) -> None
        load(query, scope) -> list[MemoryEntry]
        summarize(scope, depth) -> str
    """

    def store(self, entry: MemoryEntry) -> None:
        """Store an entry in memory.

        Args:
            entry: MemoryEntry to store.
        """
        raise NotImplementedError

    def load(self, query: str, scope: str = "project") -> list[MemoryEntry]:
        """Load memory entries matching query.

        Args:
            query: Search query.
            scope: Memory scope (project, session, global).

        Returns:
            List of MemoryEntry matching the query.
        """
        raise NotImplementedError

    def summarize(self, scope: str, depth: str = "brief") -> str:
        """Get memory summary.

        Args:
            scope: Scope to summarize (project, phase, task).
            depth: Summary depth (brief, detailed, full).

        Returns:
            Summarized text.
        """
        raise NotImplementedError
