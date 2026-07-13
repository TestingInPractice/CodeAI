"""Shared fixtures for integration tests."""

import sys
from pathlib import Path
from uuid import uuid4

import unittest

# Add project root to path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from scripts.core.enums import (
    KnowledgeKind,
    KnowledgeType,
    MemoryType,
    PhaseStatus,
    TaskStatus,
)
from scripts.core.event_bus import EventBus
from scripts.core.knowledge_layer import KnowledgeLayer
from scripts.core.memory_layer import MemoryLayer
from scripts.core.ooda_runtime import OODARuntime
from scripts.core.types.knowledge import Knowledge
from scripts.core.types.memory import MemoryEntry
from scripts.core.types.workflow import Task

from tests.integration.in_memory_memory_repository import InMemoryMemoryRepository


def event_bus():
    return EventBus()


def knowledge_layer():
    return KnowledgeLayer()


def memory_repo():
    return InMemoryMemoryRepository()


def memory_layer(memory_repo):
    return MemoryLayer(memory_repo)


def ooda_runtime(knowledge_layer, memory_layer):
    return OODARuntime(knowledge_layer, memory_layer)


def judge_engine():
    from scripts.core.judge_engine import JudgeEngine
    return JudgeEngine()


def sample_knowledge():
    items = [
        Knowledge(
            id=uuid4(),
            source="docs/architecture.md",
            kind=KnowledgeKind.DOCUMENT,
            content="Architecture uses OODA loop for agent orchestration",
            score=0.9,
            metadata={"scope": "project"},
        ),
        Knowledge(
            id=uuid4(),
            source="docs/patterns.md",
            kind=KnowledgeKind.ARTICLE,
            content="Best practice: separate concerns in agent systems",
            score=0.8,
            metadata={"scope": "project"},
        ),
    ]
    return items


def sample_memory_entries():
    return [
        MemoryEntry(
            id=uuid4(),
            type=MemoryType.PROJECT_HISTORY,
            content="Implemented workflow engine in phase 1",
            scope="project",
            metadata={"phase_id": "p1"},
        ),
        MemoryEntry(
            id=uuid4(),
            type=MemoryType.DECISIONS,
            content="Decided to use Repository Pattern for persistence",
            scope="project",
            metadata={},
        ),
    ]


def sample_task():
    return Task(
        uuid=uuid4(),
        title="Implement integration tests",
        description="Write comprehensive integration tests for the platform",
        spec_ref="docs/specs/goals.md",
    )


def make_task(title="test task", description="test desc", spec_ref=""):
    return Task(uuid=uuid4(), title=title, description=description, spec_ref=spec_ref)


def make_knowledge(content="test knowledge", kind=KnowledgeKind.DOCUMENT, source="test"):
    return Knowledge(
        id=uuid4(),
        source=source,
        kind=kind,
        content=content,
        score=0.8,
        metadata={"scope": "project"},
    )


def make_memory(content="test memory", mem_type=MemoryType.PROJECT_HISTORY, scope="project"):
    return MemoryEntry(
        id=uuid4(),
        type=mem_type,
        content=content,
        scope=scope,
        metadata={},
    )
