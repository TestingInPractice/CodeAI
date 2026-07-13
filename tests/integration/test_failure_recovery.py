"""Integration Test: Failure Recovery.

Tests failure scenarios:
- Knowledge unavailable → OODA continues
- Memory unavailable → OODA continues
- Judge FAIL → Workflow rollback
- Resume after interrupt
- Error propagation and recovery
"""

import sys
import unittest
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.core.enums import (
    KnowledgeKind,
    MemoryType,
    PhaseStatus,
    TaskStatus,
    WorkflowStatus,
)
from scripts.core.errors import (
    CodeAIError,
    KnowledgeError,
    MemoryError,
    OODAError,
    WorkflowError,
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


class _FailingMemoryRepository:
    """Memory repository that raises on all operations."""

    def store(self, entry):
        raise MemoryError("Storage unavailable", code="MEM_STORE_FAILED", recoverable=True)

    def load(self, entry_id):
        raise MemoryError("Load unavailable", code="MEM_LOAD_FAILED", recoverable=True)

    def load_all(self, memory_type=None, scope="project"):
        raise MemoryError("Load unavailable", code="MEM_LOAD_FAILED", recoverable=True)

    def delete(self, entry_id):
        raise MemoryError("Delete unavailable", code="MEM_DELETE_FAILED", recoverable=True)

    def exists(self, entry_id):
        raise MemoryError("Check unavailable", code="MEM_LOAD_FAILED", recoverable=True)

    def count(self, memory_type=None, scope="project"):
        raise MemoryError("Count unavailable", code="MEM_LOAD_FAILED", recoverable=True)

    def delete_expired(self, before):
        raise MemoryError("Delete unavailable", code="MEM_DELETE_FAILED", recoverable=True)


class TestFailureRecovery(unittest.TestCase):
    """Failure and recovery scenarios."""

    def test_ooda_continues_when_memory_fails(self):
        """OODA continues even if Memory Layer fails."""
        knowledge = KnowledgeLayer()
        failing_memory = MemoryLayer(_FailingMemoryRepository())
        ooda = OODARuntime(knowledge, failing_memory)

        task = Task(uuid=uuid4(), title="Task with memory failure", description="Test")
        result = ooda.execute(task)
        # OODA should complete despite memory failure
        assert result.success

    def test_ooda_continues_when_knowledge_empty(self):
        """OODA continues with empty knowledge."""
        knowledge = KnowledgeLayer()
        mem_repo = InMemoryMemoryRepository()
        memory = MemoryLayer(mem_repo)
        ooda = OODARuntime(knowledge, memory)

        task = Task(uuid=uuid4(), title="Task with no knowledge", description="Test")
        result = ooda.execute(task)
        assert result.success

    def test_workflow_rollback_on_judge_fail(self):
        """Workflow rolls back when judge fails."""
        t = TaskState(uuid=str(uuid4()), title="task")
        state = WorkflowState(phases=[PhaseState(id="p1", title="Phase 1", tasks=[t])])
        workflow = WorkflowEngine(state)

        workflow.start("p1")
        t.status = TaskStatus.COMPLETED

        # Simulate judge fail
        workflow.rollback("p1", "Judge failed")

        assert state.current_phase is None
        assert state.workflow_status == WorkflowStatus.ROLLING_BACK
        assert len(state.rollback_stack) == 1

    def test_resume_after_rollback(self):
        """Resume workflow after rollback."""
        t = TaskState(uuid=str(uuid4()), title="task")
        state = WorkflowState(phases=[PhaseState(id="p1", title="Phase 1", tasks=[t])])
        workflow = WorkflowEngine(state)

        workflow.start("p1")
        t.status = TaskStatus.COMPLETED
        workflow.rollback("p1", "Need to redo")

        # Phase should be pending again
        phase = next(p for p in state.phases if p.id == "p1")
        assert phase.status == PhaseStatus.PENDING
        assert phase.judge_passed is False

        # Can start again
        workflow.start("p1")
        assert state.current_phase.id == "p1"

    def test_error_hierarchy(self):
        """All errors inherit from CodeAIError."""
        assert issubclass(KnowledgeError, CodeAIError)
        assert issubclass(MemoryError, CodeAIError)
        assert issubclass(OODAError, CodeAIError)
        assert issubclass(WorkflowError, CodeAIError)

    def test_error_has_code(self):
        """Errors carry stable error codes."""
        err = KnowledgeError("test", code="KLG_TEST")
        assert err.code == "KLG_TEST"
        assert err.recoverable is False

    def test_error_has_context(self):
        """Errors carry context dict."""
        err = OODAError("test", code="OODA_TEST", context={"key": "value"})
        assert err.context["key"] == "value"

    def test_workflow_error_on_invalid_transition(self):
        """Workflow raises on invalid state transitions."""
        state = WorkflowState(phases=[PhaseState(id="p1", title="Phase 1", tasks=[])])
        workflow = WorkflowEngine(state)

        # Complete without starting
        with self.assertRaises(WorkflowError):
            workflow.complete("p1", judge_passed=True)

    def test_judge_empty_response_raises(self):
        """Judge raises on empty response."""
        judge = JudgeEngine()
        with self.assertRaises(Exception):
            judge.evaluate("", "", "")

    def test_multiple_rollbacks(self):
        """Multiple rollbacks accumulate in stack."""
        t = TaskState(uuid=str(uuid4()), title="task")
        state = WorkflowState(phases=[PhaseState(id="p1", title="Phase 1", tasks=[t])])
        workflow = WorkflowEngine(state)

        workflow.start("p1")
        t.status = TaskStatus.COMPLETED
        workflow.rollback("p1", "First rollback")

        workflow.start("p1")
        t.status = TaskStatus.COMPLETED
        workflow.rollback("p1", "Second rollback")

        assert len(state.rollback_stack) == 2
        assert state.rollback_stack[0]["reason"] == "First rollback"
        assert state.rollback_stack[1]["reason"] == "Second rollback"

    def test_knowledge_error_code(self):
        """KnowledgeError has correct error code."""
        try:
            raise KnowledgeError("fail", code="KLG_SEARCH_FAILED", recoverable=True)
        except KnowledgeError as e:
            assert e.code == "KLG_SEARCH_FAILED"
            assert e.recoverable is True

    def test_memory_error_code(self):
        """MemoryError has correct error code."""
        try:
            raise MemoryError("fail", code="MEM_STORE_FAILED", recoverable=True)
        except MemoryError as e:
            assert e.code == "MEM_STORE_FAILED"
            assert e.recoverable is True

    def test_ooda_error_code(self):
        """OODAError has correct error code."""
        try:
            raise OODAError("fail", code="OODA_EXECUTE_FAILED")
        except OODAError as e:
            assert e.code == "OODA_EXECUTE_FAILED"

    def test_workflow_error_code(self):
        """WorkflowError has correct error code."""
        try:
            raise WorkflowError("fail", code="WF_PHASE_NOT_FOUND")
        except WorkflowError as e:
            assert e.code == "WF_PHASE_NOT_FOUND"
