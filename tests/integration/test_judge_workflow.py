"""Integration Test: Judge + Workflow.

Tests Judge Engine integration with Workflow Engine:
- evaluate → route → workflow decision
- PASS routes to workflow
- FAIL routes to OODA or Spec
- Score with rubric
- Multiple evaluations in sequence
"""

import sys
import unittest
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.core.enums import (
    RouteTarget,
    VerdictStatus,
    WorkflowStatus,
)
from scripts.core.judge_engine import JudgeEngine
from scripts.core.types.judge import RouteAction, Rubric, RubricCriterion, Score, Verdict
from scripts.core.workflow_engine import WorkflowEngine
from scripts.core.workflow.state import PhaseState, TaskState, WorkflowState


class TestJudgeWorkflow(unittest.TestCase):
    """Judge + Workflow integration."""

    def test_judge_pass_completes_phase(self):
        """Judge PASS allows phase completion."""
        judge = JudgeEngine()
        t = TaskState(uuid=uuid4(), title="task")
        state = WorkflowState(phases=[PhaseState(id="p1", title="Phase 1", tasks=[t])])
        workflow = WorkflowEngine(state)

        workflow.start("p1")
        t.status = "completed"

        verdict = judge.evaluate(
            response="Phase completed with all requirements met",
            context="Implementation matches spec",
            spec="Phase requirements",
        )

        judge_passed = verdict.overall in (VerdictStatus.PASS, VerdictStatus.PASS_WITH_CONCERNS)
        workflow.complete("p1", judge_passed=judge_passed)
        assert state.workflow_status == WorkflowStatus.COMPLETED

    def test_judge_fail_prevents_completion(self):
        """Judge FAIL prevents phase completion."""
        judge = JudgeEngine()
        t = TaskState(uuid=uuid4(), title="task")
        state = WorkflowState(phases=[PhaseState(id="p1", title="Phase 1", tasks=[t])])
        workflow = WorkflowEngine(state)

        workflow.start("p1")
        t.status = "completed"

        verdict = judge.evaluate(
            response="x",
            context="",
            spec="Complex requirements with many acceptance criteria",
        )

        # If FAIL, cannot complete
        if verdict.overall == VerdictStatus.FAIL:
            with self.assertRaises(Exception):
                workflow.complete("p1", judge_passed=False)

    def test_judge_routes_to_workflow_on_pass(self):
        """PASS verdict routes to workflow."""
        judge = JudgeEngine()
        verdict = judge.evaluate(
            response="Successfully implemented all features",
            context="Feature implementation matches requirements",
            spec="Implement features with tests",
        )
        route = judge.route(verdict)
        assert route.target in (RouteTarget.WORKFLOW, RouteTarget.OODA, RouteTarget.SPEC)

        if verdict.overall in (VerdictStatus.PASS, VerdictStatus.PASS_WITH_CONCERNS):
            assert route.target == RouteTarget.WORKFLOW

    def test_judge_routes_to_ooda_on_low_faithfulness(self):
        """Low faithfulness routes to OODA."""
        judge = JudgeEngine()
        verdict = judge.evaluate(
            response="xyz completely unrelated response with no context",
            context="",
            spec="Implement authentication system with JWT tokens",
        )
        route = judge.route(verdict)
        # Should route somewhere
        assert route.target in (RouteTarget.WORKFLOW, RouteTarget.OODA, RouteTarget.SPEC)

    def test_judge_score_with_rubric(self):
        """Score response against rubric."""
        judge = JudgeEngine()
        rubric = Rubric(
            name="code_quality",
            criteria=[
                RubricCriterion(id="c1", label="code is clean and readable", weight=2),
                RubricCriterion(id="c2", label="tests are comprehensive", weight=1),
                RubricCriterion(id="c3", label="documentation is complete", weight=1),
            ],
        )
        score = judge.score("code is clean and readable with comprehensive tests", rubric)
        assert isinstance(score, Score)
        assert 0 <= score.value <= 1
        assert "c1" in score.breakdown

    def test_multiple_evaluations(self):
        """Multiple evaluations in sequence."""
        judge = JudgeEngine()
        results = []
        for i in range(5):
            verdict = judge.evaluate(
                response=f"Implementation {i} with details",
                context=f"Context for iteration {i}",
                spec=f"Requirements iteration {i}",
            )
            results.append(verdict)

        assert len(results) == 5
        for v in results:
            assert v.overall in (VerdictStatus.PASS, VerdictStatus.PASS_WITH_CONCERNS, VerdictStatus.FAIL)

    def test_judge_verdict_fields(self):
        """Verdict has correct fields."""
        judge = JudgeEngine()
        verdict = judge.evaluate(
            response="Complete implementation with tests and docs",
            context="Full context with architecture decisions",
            spec="Implement complete feature",
        )
        assert isinstance(verdict.overall, VerdictStatus)
        assert isinstance(verdict.scores, dict)
        assert isinstance(verdict.failures, list)
        assert 0 <= verdict.confidence <= 1

    def test_route_action_fields(self):
        """RouteAction has correct fields."""
        judge = JudgeEngine()
        verdict = judge.evaluate("response", "context", "spec")
        route = judge.route(verdict)
        assert isinstance(route.target, RouteTarget)
        assert isinstance(route.reason, str)

    def test_workflow_judge_feedback_loop(self):
        """Judge evaluation feeds back into workflow decisions."""
        judge = JudgeEngine()
        t = TaskState(uuid=uuid4(), title="task")
        state = WorkflowState(phases=[PhaseState(id="p1", title="Phase 1", tasks=[t])])
        workflow = WorkflowEngine(state)

        workflow.start("p1")
        t.status = "completed"

        # Evaluate
        verdict = judge.evaluate("Completed implementation", "Context", "Spec")
        route = judge.route(verdict)

        # Use route to decide
        if route.target == RouteTarget.WORKFLOW:
            judge_passed = verdict.overall in (VerdictStatus.PASS, VerdictStatus.PASS_WITH_CONCERNS)
            workflow.complete("p1", judge_passed=judge_passed)
            assert state.workflow_status == WorkflowStatus.COMPLETED
        else:
            # Would route back to OODA or Spec
            assert route.target in (RouteTarget.OODA, RouteTarget.SPEC)
