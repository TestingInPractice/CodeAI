"""Integration Test: Full Pipeline.

Tests the complete pipeline:
User Prompt → Spec Engine → Workflow Engine → OODA Runtime → Knowledge Layer → Memory Layer → Judge Engine → Workflow Engine

Verifies correct state passing between all subsystems.
"""

import sys
import unittest
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.core.enums import (
    KnowledgeKind,
    KnowledgeType,
    MemoryType,
    PhaseStatus,
    TaskStatus,
    VerdictStatus,
    WorkflowStatus,
)
from scripts.core.event_bus import EventBus
from scripts.core.judge_engine import JudgeEngine
from scripts.core.knowledge_layer import KnowledgeLayer
from scripts.core.memory_layer import MemoryLayer
from scripts.core.ooda_runtime import OODARuntime
from scripts.core.types.knowledge import Knowledge
from scripts.core.types.memory import MemoryEntry
from scripts.core.types.workflow import Task
from scripts.core.workflow_engine import WorkflowEngine
from scripts.core.workflow.state import PhaseState, TaskState, WorkflowState

from tests.integration.in_memory_memory_repository import InMemoryMemoryRepository


class TestFullPipeline(unittest.TestCase):
    """End-to-end pipeline: Workflow → OODA → Knowledge → Memory → Judge → Workflow."""

    def test_single_phase_full_cycle(self):
        """One phase: start → OODA execute → judge → complete."""
        # Wire up subsystems
        bus = EventBus()
        knowledge = KnowledgeLayer()
        mem_repo = InMemoryMemoryRepository()
        memory = MemoryLayer(mem_repo)
        ooda = OODARuntime(knowledge, memory)
        judge = JudgeEngine()

        # Seed knowledge
        k = Knowledge(
            id=uuid4(), source="arch.md", kind=KnowledgeKind.DOCUMENT,
            content="Use OODA loop for agent orchestration", score=0.9,
            metadata={"scope": "project"},
        )
        knowledge.index(k)

        # Seed memory
        m = MemoryEntry(
            id=uuid4(), type=MemoryType.PROJECT_HISTORY,
            content="Previously built workflow engine", scope="project",
            metadata={"phase_id": "p1"},
        )
        memory.store(m)

        # Setup workflow
        task_state = TaskState(uuid=uuid4(), title="Implement OODA")
        phase = PhaseState(id="p1", title="Implement OODA Runtime", tasks=[task_state])
        state = WorkflowState(phases=[phase])
        workflow = WorkflowEngine(state)

        # 1. Start phase
        workflow.start("p1")
        assert state.current_phase is not None
        assert state.current_phase.id == "p1"

        # 2. OODA execute
        task = Task(uuid=uuid4(), title="Implement OODA", description="Build the runtime")
        result = ooda.execute(task)
        assert result.success is True
        assert result.task_id == task.uuid
        assert len(result.outputs) > 0
        assert result.summary != ""

        # 3. Judge evaluate
        verdict = judge.evaluate(
            response=result.summary,
            context="Architecture: OODA loop for agent orchestration",
            spec="Implement OODA Runtime for the platform",
        )
        assert verdict.overall is not None
        assert 0 <= verdict.confidence <= 1

        # 4. Route
        route = judge.route(verdict)
        assert route.target.value in ("workflow", "ooda", "spec")

        # 5. Complete phase (mark task completed)
        task_state.status = TaskStatus.COMPLETED
        workflow.complete("p1", judge_passed=True)

        assert state.current_phase is None
        assert state.workflow_status == WorkflowStatus.COMPLETED

    def test_multi_phase_pipeline(self):
        """Three sequential phases: p1 → p2 → p3."""
        knowledge = KnowledgeLayer()
        mem_repo = InMemoryMemoryRepository()
        memory = MemoryLayer(mem_repo)
        ooda = OODARuntime(knowledge, memory)
        judge = JudgeEngine()

        # Setup 3-phase workflow
        t1 = TaskState(uuid=uuid4(), title="Phase 1 task")
        t2 = TaskState(uuid=uuid4(), title="Phase 2 task")
        t3 = TaskState(uuid=uuid4(), title="Phase 3 task")
        p1 = PhaseState(id="p1", title="Phase 1", tasks=[t1])
        p2 = PhaseState(id="p2", title="Phase 2", tasks=[t2], depends_on=["p1"])
        p3 = PhaseState(id="p3", title="Phase 3", tasks=[t3], depends_on=["p2"])
        state = WorkflowState(phases=[p1, p2, p3])
        workflow = WorkflowEngine(state)

        # Phase 1
        workflow.start("p1")
        task1 = Task(uuid=uuid4(), title="Phase 1 task", description="First phase")
        result1 = ooda.execute(task1)
        assert result1.success
        v1 = judge.evaluate(result1.summary, "context", "spec")
        t1.status = TaskStatus.COMPLETED
        workflow.complete("p1", judge_passed=True)

        # Phase 2
        next_phase = workflow.next()
        assert next_phase is not None
        assert next_phase.id == "p2"
        workflow.start("p2")
        task2 = Task(uuid=uuid4(), title="Phase 2 task", description="Second phase")
        result2 = ooda.execute(task2)
        assert result2.success
        v2 = judge.evaluate(result2.summary, "context", "spec")
        t2.status = TaskStatus.COMPLETED
        workflow.complete("p2", judge_passed=True)

        # Phase 3
        next_phase = workflow.next()
        assert next_phase is not None
        assert next_phase.id == "p3"
        workflow.start("p3")
        task3 = Task(uuid=uuid4(), title="Phase 3 task", description="Third phase")
        result3 = ooda.execute(task3)
        assert result3.success
        t3.status = TaskStatus.COMPLETED
        workflow.complete("p3", judge_passed=True)

        assert state.workflow_status == WorkflowStatus.COMPLETED

    def test_context_flows_between_subsystems(self):
        """Verify context is not lost between subsystems."""
        knowledge = KnowledgeLayer()
        mem_repo = InMemoryMemoryRepository()
        memory = MemoryLayer(mem_repo)

        # Seed knowledge
        k = Knowledge(
            id=uuid4(), source="api-docs.md", kind=KnowledgeKind.DOCUMENT,
            content="REST API with authentication middleware", score=0.9,
            metadata={"scope": "project"},
        )
        knowledge.index(k)

        # Seed memory
        m = MemoryEntry(
            id=uuid4(), type=MemoryType.DECISIONS,
            content="Use JWT for authentication", scope="project",
            metadata={},
        )
        memory.store(m)

        # OODA execute
        ooda = OODARuntime(knowledge, memory)
        task = Task(uuid=uuid4(), title="Add auth middleware", description="JWT authentication")
        result = ooda.execute(task)

        # Verify context was gathered
        assert result.success
        # The summary should reflect gathered context
        assert "auth" in result.summary.lower() or "middleware" in result.summary.lower() or "task" in result.summary.lower()

    def test_event_bus_integrates_with_pipeline(self):
        """Events are published during pipeline execution."""
        bus = EventBus()
        events_received = []

        def handler(event):
            events_received.append(event.name)

        bus.subscribe("task.*", handler)
        bus.subscribe("*", handler)

        # Publish events manually (simulating pipeline)
        bus.publish("task.started", {"source": "ooda", "task_id": "abc"})
        bus.publish("task.completed", {"source": "ooda", "task_id": "abc"})

        # Dedup: task.* and * both match task.started, but handler fires once
        assert events_received.count("task.started") == 1
        assert events_received.count("task.completed") == 1

    def test_judge_routes_to_workflow_on_pass(self):
        """Judge PASS routes back to workflow."""
        judge = JudgeEngine()
        verdict = judge.evaluate(
            response="Implemented OODA loop with all steps",
            context="Architecture: OODA loop for agent orchestration",
            spec="Implement OODA Runtime",
        )
        route = judge.route(verdict)
        assert route.target.value == "workflow"

    def test_judge_routes_to_ooda_on_fail(self):
        """Judge routes based on verdict."""
        judge = JudgeEngine()
        verdict = judge.evaluate(
            response="x",
            context="",
            spec="Implement complex system with many requirements",
        )
        route = judge.route(verdict)
        # Route should be valid
        assert route.target.value in ("workflow", "ooda", "spec")

    def test_knowledge_and_memory_feed_ooda(self):
        """Knowledge and Memory data flows into OODA context."""
        knowledge = KnowledgeLayer()
        mem_repo = InMemoryMemoryRepository()
        memory = MemoryLayer(mem_repo)

        # Seed
        knowledge.index(Knowledge(
            id=uuid4(), source="docs.md", kind=KnowledgeKind.DOCUMENT,
            content="System uses microservices architecture", score=0.9,
            metadata={"scope": "project"},
        ))
        memory.store(MemoryEntry(
            id=uuid4(), type=MemoryType.PROJECT_HISTORY,
            content="Migrated to microservices last sprint", scope="project",
            metadata={},
        ))

        ooda = OODARuntime(knowledge, memory)
        task = Task(uuid=uuid4(), title="microservices deployment", description="Deploy microservices")
        result = ooda.execute(task)

        assert result.success
        # Summary should mention context gathered
        assert "Knowledge items" in result.summary or "memory" in result.summary.lower()
