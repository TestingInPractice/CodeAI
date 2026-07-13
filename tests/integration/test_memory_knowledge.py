"""Integration Test: Memory + Knowledge.

Tests:
- Knowledge.search() → Memory.store() → Memory.load() → Knowledge.retrieve() → OODA
- Context not lost between subsystems
"""

import sys
import unittest
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.core.enums import KnowledgeKind, KnowledgeType, MemoryType
from scripts.core.knowledge_layer import KnowledgeLayer
from scripts.core.memory_layer import MemoryLayer
from scripts.core.ooda_runtime import OODARuntime
from scripts.core.types.knowledge import Knowledge
from scripts.core.types.memory import MemoryEntry
from scripts.core.types.workflow import Task

from tests.integration.in_memory_memory_repository import InMemoryMemoryRepository


class TestMemoryKnowledge(unittest.TestCase):
    """Memory and Knowledge integration."""

    def test_knowledge_search_feeds_memory_store(self):
        """Search knowledge, store results in memory."""
        knowledge = KnowledgeLayer()
        mem_repo = InMemoryMemoryRepository()
        memory = MemoryLayer(mem_repo)

        # Index knowledge
        knowledge.index(Knowledge(
            id=uuid4(), source="docs.md", kind=KnowledgeKind.DOCUMENT,
            content="Architecture pattern: event-driven microservices", score=0.9,
            metadata={"scope": "project"},
        ))

        # Search
        results = knowledge.search("architecture")
        assert len(results) > 0

        # Store search result in memory
        entry = MemoryEntry(
            id=uuid4(),
            type=MemoryType.PROJECT_HISTORY,
            content=f"Found architecture pattern: {results[0].content}",
            scope="project",
            metadata={"source": "knowledge_search"},
        )
        memory.store(entry)

        # Load from memory
        loaded = memory.load("architecture")
        assert len(loaded) > 0
        assert "architecture" in loaded[0].content.lower()

    def test_memory_load_feeds_knowledge_index(self):
        """Load memory, index into knowledge."""
        knowledge = KnowledgeLayer()
        mem_repo = InMemoryMemoryRepository()
        memory = MemoryLayer(mem_repo)

        # Store in memory
        memory.store(MemoryEntry(
            id=uuid4(),
            type=MemoryType.DECISIONS,
            content="Use Repository Pattern for data access",
            scope="project",
            metadata={},
        ))

        # Load from memory
        decisions = memory.load("Repository Pattern")
        assert len(decisions) > 0

        # Index into knowledge
        knowledge.index(Knowledge(
            id=uuid4(),
            source="memory:decisions",
            kind=KnowledgeKind.DOCUMENT,
            content=decisions[0].content,
            score=0.8,
            metadata={"scope": "project"},
        ))

        # Search knowledge
        results = knowledge.search("Repository Pattern")
        assert len(results) > 0

    def test_ooda_uses_both_knowledge_and_memory(self):
        """OODA gathers from both Knowledge and Memory."""
        knowledge = KnowledgeLayer()
        mem_repo = InMemoryMemoryRepository()
        memory = MemoryLayer(mem_repo)

        # Seed both
        knowledge.index(Knowledge(
            id=uuid4(), source="arch.md", kind=KnowledgeKind.DOCUMENT,
            content="System uses hexagonal architecture", score=0.9,
            metadata={"scope": "project"},
        ))
        memory.store(MemoryEntry(
            id=uuid4(), type=MemoryType.PROJECT_HISTORY,
            content="Migrated to hexagonal architecture in sprint 5", scope="project",
            metadata={},
        ))

        ooda = OODARuntime(knowledge, memory)
        task = Task(uuid=uuid4(), title="hexagonal architecture refactoring", description="Apply hexagonal pattern")
        result = ooda.execute(task)

        assert result.success
        # Summary should reflect gathered context
        assert "Knowledge items" in result.summary or "hexagonal" in result.summary.lower()

    def test_context_preserved_through_pipeline(self):
        """Context flows: Knowledge → OODA → Judge without loss."""
        knowledge = KnowledgeLayer()
        mem_repo = InMemoryMemoryRepository()
        memory = MemoryLayer(mem_repo)

        knowledge.index(Knowledge(
            id=uuid4(), source="api.md", kind=KnowledgeKind.DOCUMENT,
            content="REST API with pagination and filtering", score=0.9,
            metadata={"scope": "project"},
        ))
        memory.store(MemoryEntry(
            id=uuid4(), type=MemoryType.DECISIONS,
            content="Use cursor-based pagination for API", scope="project",
            metadata={},
        ))

        ooda = OODARuntime(knowledge, memory)
        task = Task(uuid=uuid4(), title="API pagination", description="Implement cursor pagination")
        result = ooda.execute(task)

        # Feed into Judge
        from scripts.core.judge_engine import JudgeEngine
        judge = JudgeEngine()
        verdict = judge.evaluate(
            response=result.summary,
            context="REST API with pagination and filtering",
            spec="Implement cursor-based pagination",
        )
        assert verdict.overall is not None
        assert verdict.confidence > 0

    def test_knowledge_search_empty_query(self):
        """Empty query returns empty list."""
        knowledge = KnowledgeLayer()
        results = knowledge.search("")
        assert results == []

    def test_memory_load_empty_query(self):
        """Empty query returns empty list."""
        mem_repo = InMemoryMemoryRepository()
        memory = MemoryLayer(mem_repo)
        results = memory.load("")
        assert results == []

    def test_knowledge_retrieve_by_type(self):
        """Retrieve context by knowledge type."""
        knowledge = KnowledgeLayer()

        knowledge.index(Knowledge(
            id=uuid4(), source="arch.md", kind=KnowledgeKind.DOCUMENT,
            content="Architecture decision: use event sourcing", score=0.9,
            metadata={"scope": "project"},
        ))
        knowledge.index(Knowledge(
            id=uuid4(), source="pattern.md", kind=KnowledgeKind.ARTICLE,
            content="Best practice: CQRS pattern", score=0.8,
            metadata={"scope": "project"},
        ))

        ctx = knowledge.retrieve(KnowledgeType.ARCHITECTURE, {})
        assert ctx.context_type == KnowledgeType.ARCHITECTURE
        assert isinstance(ctx.items, list)

    def test_memory_summarize(self):
        """Memory summarize returns non-empty for non-empty store."""
        mem_repo = InMemoryMemoryRepository()
        memory = MemoryLayer(mem_repo)

        memory.store(MemoryEntry(
            id=uuid4(), type=MemoryType.PROJECT_HISTORY,
            content="Built workflow engine", scope="project",
            metadata={},
        ))
        memory.store(MemoryEntry(
            id=uuid4(), type=MemoryType.DECISIONS,
            content="Use async processing", scope="project",
            metadata={},
        ))

        summary = memory.summarize(scope="project", depth="brief")
        assert summary != ""
        assert "entries" in summary.lower() or "memory" in summary.lower()
