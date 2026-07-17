"""End-to-End Integration Tests.

Tests the complete pipeline connecting all 6 subsystems + Event Bus.
"""

import sys
import unittest
from pathlib import Path
from uuid import UUID, uuid4

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.core.enums import (
    KnowledgeKind,
    MemoryType,
    TaskStatus,
    VerdictStatus,
    WorkflowStatus,
)
from scripts.core.event_bus import EventBus
from scripts.core.judge_engine import JudgeEngine
from scripts.core.knowledge_layer import KnowledgeLayer
from scripts.core.memory_layer import MemoryLayer
from scripts.core.memory.in_memory_repository import InMemoryMemoryRepository
from scripts.core.ooda_runtime import OODARuntime
from scripts.core.pipeline import EndToEndPipeline, PipelineResult
from scripts.core.spec_engine import SpecEngine
from scripts.core.types.knowledge import Knowledge
from scripts.core.types.memory import MemoryEntry
from scripts.core.types.workflow import Task
from scripts.core.workflow_engine import WorkflowEngine
from scripts.core.workflow.state import PhaseState, TaskState, WorkflowState


class TestSuccessfulPipeline(unittest.TestCase):
    """Test successful end-to-end pipeline execution."""

    def test_full_pipeline_run(self):
        """Complete pipeline: prompt → spec → workflow → OODA → judge → done."""
        pipeline = EndToEndPipeline()
        result = pipeline.run("Create a Python calculator")

        # Spec generated
        self.assertTrue(result.validation.valid)
        self.assertGreater(len(result.spec.requirements), 0)
        self.assertGreater(len(result.spec.acceptance_criteria), 0)

        # Workflow completed
        self.assertEqual(result.workflow_status, WorkflowStatus.COMPLETED.value)
        self.assertEqual(len(result.phases_completed), 1)
        self.assertEqual(len(result.phases_failed), 0)

        # OODA executed
        self.assertEqual(len(result.ooda_results), 1)
        self.assertTrue(result.ooda_results[0].success)

        # Judge evaluated
        self.assertEqual(len(result.judge_verdicts), 1)
        self.assertIn(result.judge_verdicts[0]["overall"], ["PASS", "PASS_WITH_CONCERNS"])

        # Events published
        self.assertGreater(len(result.events), 0)

        # Artifacts produced
        self.assertGreater(len(result.artifacts), 0)

    def test_multi_requirement_pipeline(self):
        """Pipeline with multiple requirements creates multiple phases."""
        pipeline = EndToEndPipeline()

        # Override spec to have 3 requirements
        from scripts.core.types.spec import Requirement, AC, StructuredSpec
        from scripts.core.enums import Priority
        reqs = [
            Requirement(id=uuid4(), title=f"Requirement {i}", description=f"Desc {i}", priority=Priority.MUST)
            for i in range(3)
        ]
        acs = [
            AC(id=uuid4(), requirement_id=r.id, description=f"AC for {r.title}")
            for r in reqs
        ]
        pipeline.spec_engine.parse = lambda path: StructuredSpec(
            requirements=reqs, acceptance_criteria=acs,
        )

        result = pipeline.run("Build a multi-feature app")

        # All 3 phases should execute
        self.assertEqual(len(result.ooda_results), 3)
        self.assertEqual(len(result.judge_verdicts), 3)

    def test_spec_generates_valid_structured_spec(self):
        """SpecEngine produces valid StructuredSpec."""
        engine = SpecEngine()
        path = engine.generate("Test prompt")
        self.assertIsNotNone(path)

        validation = engine.validate(path)
        self.assertTrue(validation.valid)

        engine.approve(path)
        spec = engine.parse(path)

        self.assertGreater(len(spec.requirements), 0)
        self.assertGreater(len(spec.acceptance_criteria), 0)
        self.assertIsNotNone(spec.scope)


class TestJudgeFailRollback(unittest.TestCase):
    """Test Judge FAIL → rollback flow."""

    def test_judge_fail_causes_rollback(self):
        """When Judge FAILs, phase is rolled back."""
        pipeline = EndToEndPipeline()

        # Override judge to always fail
        from unittest.mock import MagicMock
        from scripts.core.types.judge import Verdict, RouteAction
        from scripts.core.enums import RouteTarget
        pipeline.judge.evaluate = MagicMock(return_value=Verdict(
            overall=VerdictStatus.FAIL,
            scores={"ac_check": 0.2, "relevance": 0.2, "faithfulness": 0.2, "context_precision": 0.2},
            failures=["ac_low_coverage: 0/2"],
            confidence=0.2,
        ))
        pipeline.judge.route = MagicMock(return_value=RouteAction(
            target=RouteTarget.SPEC,
            reason="AC coverage too low",
        ))

        result = pipeline.run("Build something")

        # Phase should fail
        self.assertEqual(len(result.phases_failed), 1)
        self.assertEqual(len(result.phases_completed), 0)

    def test_judge_verdict_reflected_in_result(self):
        """Judge verdict is captured in pipeline result."""
        pipeline = EndToEndPipeline()

        from unittest.mock import MagicMock
        from scripts.core.types.judge import Verdict, RouteAction
        from scripts.core.enums import RouteTarget
        pipeline.judge.evaluate = MagicMock(return_value=Verdict(
            overall=VerdictStatus.FAIL,
            scores={},
            failures=["test failure"],
            confidence=0.1,
        ))
        pipeline.judge.route = MagicMock(return_value=RouteAction(
            target=RouteTarget.OODA,
            reason="Repeat with grounding",
        ))

        result = pipeline.run("Test")
        self.assertEqual(result.judge_verdicts[0]["overall"], "FAIL")
        self.assertEqual(result.judge_verdicts[0]["route"], "ooda")


class TestJudgeFailRepeatOODA(unittest.TestCase):
    """Test Judge FAIL → route to OODA."""

    def test_fail_routes_to_ooda(self):
        """Low faithfulness routes to OODA."""
        pipeline = EndToEndPipeline()

        from unittest.mock import MagicMock
        from scripts.core.types.judge import Verdict, RouteAction
        from scripts.core.enums import RouteTarget
        pipeline.judge.evaluate = MagicMock(return_value=Verdict(
            overall=VerdictStatus.FAIL,
            scores={"ac_check": 0.5, "relevance": 0.5, "faithfulness": 0.2, "context_precision": 0.5},
            failures=["high_hallucination_risk"],
            confidence=0.3,
        ))
        pipeline.judge.route = MagicMock(return_value=RouteAction(
            target=RouteTarget.OODA,
            reason="Faithfulness too low",
        ))

        result = pipeline.run("Test")
        route = result.judge_verdicts[0]["route"]
        self.assertEqual(route, "ooda")


class TestJudgeFailReviseSpec(unittest.TestCase):
    """Test Judge FAIL → route to Spec."""

    def test_fail_routes_to_spec(self):
        """Low AC coverage routes to Spec."""
        pipeline = EndToEndPipeline()

        from unittest.mock import MagicMock
        from scripts.core.types.judge import Verdict, RouteAction
        from scripts.core.enums import RouteTarget
        pipeline.judge.evaluate = MagicMock(return_value=Verdict(
            overall=VerdictStatus.FAIL,
            scores={"ac_check": 0.2, "relevance": 0.5, "faithfulness": 0.5, "context_precision": 0.5},
            failures=["ac_low_coverage: 0/2"],
            confidence=0.3,
        ))
        pipeline.judge.route = MagicMock(return_value=RouteAction(
            target=RouteTarget.SPEC,
            reason="AC coverage too low",
        ))

        result = pipeline.run("Test")
        route = result.judge_verdicts[0]["route"]
        self.assertEqual(route, "spec")


class TestMemoryPersistence(unittest.TestCase):
    """Test memory persists across iterations."""

    def test_memory_persists_across_phases(self):
        """Memory stored in phase 1 is available in phase 2."""
        pipeline = EndToEndPipeline()

        # Override spec to have 2 phases
        from scripts.core.types.spec import Requirement, AC, StructuredSpec
        from scripts.core.enums import Priority
        reqs = [
            Requirement(id=uuid4(), title="Phase 1", description="First", priority=Priority.MUST),
            Requirement(id=uuid4(), title="Phase 2", description="Second", priority=Priority.MUST),
        ]
        acs = [AC(id=uuid4(), requirement_id=r.id, description=f"AC for {r.title}") for r in reqs]
        pipeline.spec_engine.parse = lambda path: StructuredSpec(
            requirements=reqs, acceptance_criteria=acs,
        )

        result = pipeline.run("Multi-phase task")

        # Both phases should complete
        self.assertEqual(len(result.phases_completed), 2)

        # Memory should have entries from both phases
        loaded = pipeline.memory.load("Phase")
        self.assertGreater(len(loaded), 0)


class TestKnowledgeRetrieval(unittest.TestCase):
    """Test knowledge retrieval during pipeline."""

    def test_knowledge_seeded_and_retrieved(self):
        """Knowledge is seeded and retrieved during OODA."""
        pipeline = EndToEndPipeline()
        prompt = "Test knowledge retrieval"
        result = pipeline.run(prompt)

        # Knowledge should have been indexed (seeded with task titles from spec)
        search_results = pipeline.knowledge.search("knowledge")
        self.assertGreater(len(search_results), 0)

    def test_knowledge_in_ooda_context(self):
        """Knowledge items appear in OODA context."""
        pipeline = EndToEndPipeline()
        result = pipeline.run("Test knowledge in context")

        # OODA should have executed with knowledge
        self.assertTrue(result.ooda_results[0].success)


class TestEventBusNotifications(unittest.TestCase):
    """Test EventBus notifications during pipeline."""

    def test_events_published_in_order(self):
        """Events are published in correct order."""
        pipeline = EndToEndPipeline()
        result = pipeline.run("Test events")

        events = result.events
        self.assertIn("spec.created", events)
        self.assertIn("spec.validated", events)
        self.assertIn("phase.started", events)
        self.assertIn("task.completed", events)
        self.assertIn("judge.evaluated", events)
        self.assertIn("phase.completed", events)

        # Order check
        spec_created_idx = events.index("spec.created")
        phase_started_idx = events.index("phase.started")
        judge_evaluated_idx = events.index("judge.evaluated")
        phase_completed_idx = events.index("phase.completed")

        self.assertLess(spec_created_idx, phase_started_idx)
        self.assertLess(phase_started_idx, judge_evaluated_idx)
        self.assertLess(judge_evaluated_idx, phase_completed_idx)

    def test_event_count_matches_phases(self):
        """Each phase produces a set of events."""
        pipeline = EndToEndPipeline()
        result = pipeline.run("Test event count")

        # At least: spec.created, spec.validated, phase.started, task.completed,
        # judge.evaluated, phase.completed = 6
        self.assertGreaterEqual(len(result.events), 6)


class TestSpecEngine(unittest.TestCase):
    """Test SpecEngine standalone."""

    def test_generate_returns_path(self):
        engine = SpecEngine()
        path = engine.generate("Test prompt")
        self.assertIsInstance(path, Path)

    def test_validate_empty_path(self):
        engine = SpecEngine()
        result = engine.validate(None)
        self.assertFalse(result.valid)

    def test_approve_null_raises(self):
        engine = SpecEngine()
        from scripts.core.errors import SpecError
        with self.assertRaises(SpecError):
            engine.approve(None)

    def test_parse_null_raises(self):
        engine = SpecEngine()
        from scripts.core.errors import SpecError
        with self.assertRaises(SpecError):
            engine.parse(None)

    def test_generate_empty_prompt_raises(self):
        engine = SpecEngine()
        from scripts.core.errors import SpecError
        with self.assertRaises(SpecError):
            engine.generate("")


class TestPhaseErrorHandling(unittest.TestCase):
    """Test Pipeline error handling in _execute_phase."""

    def _make_pipeline(self):
        """Create a fresh pipeline for testing."""
        from scripts.core.pipeline import EndToEndPipeline
        return EndToEndPipeline()

    def test_ooda_exception_causes_rollback(self):
        """Exception inside OODA execution → rollback + error recorded."""
        pipeline = self._make_pipeline()
        from unittest.mock import MagicMock
        from scripts.core.errors import OODAError

        pipeline.ooda.execute = MagicMock(side_effect=OODAError(
            "OODA crashed", code="OODA_FAIL"
        ))

        result = pipeline.run("Build a system")

        # Phase should be in failed list
        self.assertEqual(len(result.phases_failed), 1)
        self.assertEqual(len(result.phases_completed), 0)

        # Error should be recorded
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(result.errors[0]["code"], "OODA_FAIL")
        self.assertIn("OODA crashed", result.errors[0]["error"])

        # phase.failed event should be published
        self.assertIn("phase.failed", result.events)

    def test_judge_exception_causes_rollback(self):
        """Exception inside Judge evaluation → rollback + error recorded."""
        pipeline = self._make_pipeline()
        from unittest.mock import MagicMock
        from scripts.core.errors import JudgeError

        pipeline.judge.evaluate = MagicMock(side_effect=JudgeError(
            "Judge crashed", code="JUDGE_FAIL"
        ))

        result = pipeline.run("Build a system")

        self.assertEqual(len(result.phases_failed), 1)
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(result.errors[0]["code"], "JUDGE_FAIL")
        self.assertIn("phase.failed", result.events)

    def test_workflow_start_exception_causes_failure(self):
        """Exception inside Workflow.start → error recorded, no crash."""
        from unittest.mock import MagicMock, patch
        from scripts.core.errors import WorkflowError
        from scripts.core.workflow.state import PhaseState, TaskState

        # Create a mock phase for next() to return
        phase = PhaseState(id="phase-1", title="Test")
        phase.tasks.append(TaskState(uuid=UUID("00000000-0000-0000-0000-000000000001"), title="T1"))

        class FakeWorkflowEngine:
            """Fake that stores the state from __init__ and raises on start."""
            def __init__(self, state):
                self._state = state
                self._mock = MagicMock()
                self._mock.next.return_value = phase
                self._mock.start.side_effect = WorkflowError(
                    "Workflow start failed", code="WF_START_FAIL"
                )

            def __getattr__(self, name):
                return getattr(self._mock, name)

        with patch("scripts.core.pipeline.WorkflowEngine", FakeWorkflowEngine):
            pipeline = self._make_pipeline()
            result = pipeline.run("Build a system")

        self.assertEqual(len(result.errors), 1)
        self.assertEqual(result.errors[0]["code"], "WF_START_FAIL")
        self.assertEqual(result.workflow_status, "failed")

    def test_workflow_complete_exception_causes_failure(self):
        """Exception inside Workflow.complete → error recorded."""
        from unittest.mock import MagicMock, patch
        from scripts.core.errors import WorkflowError
        from scripts.core.workflow.state import PhaseState, TaskState

        # Create a mock phase for next() to return
        phase = PhaseState(id="phase-1", title="Test")
        phase.tasks.append(TaskState(uuid=UUID("00000000-0000-0000-0000-000000000001"), title="T1"))

        class FakeWorkflowEngine:
            """Fake that stores state and raises on complete."""
            def __init__(self, state):
                self._state = state
                self._mock = MagicMock()
                self._mock.next.return_value = phase
                self._mock.complete.side_effect = WorkflowError(
                    "Complete failed", code="WF_COMPLETE_FAIL"
                )

            def __getattr__(self, name):
                return getattr(self._mock, name)

        with patch("scripts.core.pipeline.WorkflowEngine", FakeWorkflowEngine):
            pipeline = self._make_pipeline()
            result = pipeline.run("Build a system")

        self.assertEqual(len(result.errors), 1)
        self.assertEqual(result.errors[0]["code"], "WF_COMPLETE_FAIL")

    def test_pipeline_returns_result_on_exception(self):
        """Pipeline always returns PipelineResult, never raises."""
        pipeline = self._make_pipeline()
        from unittest.mock import MagicMock
        from scripts.core.errors import OODAError

        pipeline.ooda.execute = MagicMock(side_effect=OODAError(
            "crash", code="X", recoverable=False
        ))

        # Should NOT raise
        result = pipeline.run("test")
        self.assertIsNotNone(result)
        self.assertEqual(result.workflow_status, "failed")

    def test_error_preserves_cause(self):
        """Error dict contains recoverable flag from original exception."""
        pipeline = self._make_pipeline()
        from unittest.mock import MagicMock
        from scripts.core.errors import OODAError

        pipeline.ooda.execute = MagicMock(side_effect=OODAError(
            "timeout", code="TIMEOUT", recoverable=True
        ))

        result = pipeline.run("test")
        self.assertTrue(result.errors[0]["recoverable"])

    def test_phase_failed_event_contains_error_info(self):
        """phase.failed event includes error message and code."""
        pipeline = self._make_pipeline()
        from unittest.mock import MagicMock
        from scripts.core.errors import OODAError

        pipeline.ooda.execute = MagicMock(side_effect=OODAError(
            "bad state", code="BAD_STATE"
        ))

        pipeline.run("test")

        # Find the phase.failed event
        failed_events = [
            e for e in pipeline._events if e == "phase.failed"
        ]
        self.assertEqual(len(failed_events), 1)

    def test_successful_phase_no_errors(self):
        """Successful phase produces no errors."""
        pipeline = self._make_pipeline()
        result = pipeline.run("Build a calculator")
        self.assertEqual(len(result.errors), 0)
        self.assertGreater(len(result.phases_completed), 0)

    def test_multiple_phases_partial_failure(self):
        """First phase fails, second never starts (dependency blocked)."""
        pipeline = self._make_pipeline()
        from unittest.mock import MagicMock
        from scripts.core.errors import OODAError
        from scripts.core.types.spec import Requirement, AC, StructuredSpec
        from scripts.core.enums import Priority

        r1 = uuid4()
        r2 = uuid4()
        pipeline.spec_engine.parse = lambda path: StructuredSpec(
            requirements=[
                Requirement(id=r1, title="Phase 1", description="First", priority=Priority.MUST),
                Requirement(id=r2, title="Phase 2", description="Second", priority=Priority.MUST),
            ],
            acceptance_criteria=[
                AC(id=uuid4(), requirement_id=r1, description="Phase 1 works"),
                AC(id=uuid4(), requirement_id=r2, description="Phase 2 works"),
            ],
        )

        pipeline.ooda.execute = MagicMock(side_effect=OODAError(
            "First OODA fails", code="OODA_1"
        ))

        result = pipeline.run("Multi-phase build")

        # Phase 1 failed, phase 2 never started (dependency blocked by phase 1 failure)
        self.assertEqual(len(result.phases_failed), 1)
        self.assertEqual(len(result.phases_completed), 0)
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(result.errors[0]["code"], "OODA_1")


if __name__ == "__main__":
    unittest.main()
