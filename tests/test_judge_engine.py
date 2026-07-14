"""Unit tests for JudgeEngine.

Tests use ONLY public API from CORE_RUNTIME.md:
- evaluate(response, context, spec)
- score(response, rubric)
- route(verdict)
"""

import unittest

from scripts.core.enums import RouteTarget, VerdictStatus
from scripts.core.errors import JudgeError
from scripts.core.judge_engine import JudgeEngine
from scripts.core.types import Rubric, RubricCriterion, Verdict


def make_engine(threshold: float = 0.5) -> JudgeEngine:
    return JudgeEngine(pass_threshold=threshold)


def make_rubric(name: str = "test", n: int = 3) -> Rubric:
    criteria = [
        RubricCriterion(id=f"c{i}", label=f"criteria {i}", weight=1, scale=5)
        for i in range(n)
    ]
    return Rubric(name=name, criteria=criteria)


# ── evaluate() ──────────────────────────────────────────────────


class TestEvaluate(unittest.TestCase):
    def test_empty_response_raises(self):
        engine = make_engine()
        with self.assertRaises(JudgeError) as ctx:
            engine.evaluate("", context="ctx", spec="q")
        self.assertIn("empty", str(ctx.exception))

    def test_pass_with_good_response(self):
        engine = make_engine()
        response = "The answer is 42 based on the analysis of the question"
        spec = "What is the answer to the question about analysis?"
        context = "The analysis shows the answer is 42 based on thorough review"

        verdict = engine.evaluate(response, context, spec)
        self.assertEqual(verdict.overall, VerdictStatus.PASS)
        self.assertGreater(verdict.confidence, 0.5)
        self.assertIn("ac_check", verdict.scores)
        self.assertIn("relevance", verdict.scores)
        self.assertIn("faithfulness", verdict.scores)
        self.assertIn("context_precision", verdict.scores)

    def test_fail_with_poor_response(self):
        engine = make_engine()
        response = "xyz"
        spec = "How does the authentication system work in detail?"
        context = ""

        verdict = engine.evaluate(response, context, spec)
        self.assertEqual(verdict.overall, VerdictStatus.FAIL)
        self.assertLess(verdict.confidence, 0.5)

    def test_pass_with_concerns(self):
        engine = make_engine()
        response = (
            "The authentication system works by validating user credentials "
            "against the database and issuing a JWT token for subsequent requests"
        )
        spec = "How does authentication work?"
        context = (
            "## Authentication\n"
            "- The authentication system validates credentials against the database\n"
            "- JWT tokens are issued for subsequent API requests\n"
            "- Token expiration is configurable per deployment"
        )

        verdict = engine.evaluate(response, context, spec)
        self.assertIn(verdict.overall, [VerdictStatus.PASS, VerdictStatus.PASS_WITH_CONCERNS])

    def test_scores_are_dict(self):
        engine = make_engine()
        verdict = engine.evaluate("some response", "some context", "some question")
        self.assertIsInstance(verdict.scores, dict)
        self.assertEqual(len(verdict.scores), 4)

    def test_failures_are_list(self):
        engine = make_engine()
        verdict = engine.evaluate("x", "", "how does system work in detail?")
        self.assertIsInstance(verdict.failures, list)


# ── score() ─────────────────────────────────────────────────────


class TestScore(unittest.TestCase):
    def test_empty_rubric(self):
        engine = make_engine()
        rubric = Rubric(name="empty", criteria=[])
        score = engine.score("response", rubric)
        self.assertEqual(score.value, 0.0)
        self.assertEqual(score.breakdown, {})
        self.assertEqual(score.judge, "empty")

    def test_score_with_matching_criteria(self):
        engine = make_engine()
        rubric = Rubric(
            name="auth",
            criteria=[
                RubricCriterion(id="c1", label="authentication", weight=1, scale=5),
                RubricCriterion(id="c2", label="security", weight=1, scale=5),
            ],
        )
        score = engine.score("authentication and security measures", rubric)
        self.assertGreater(score.value, 0.0)
        self.assertIn("c1", score.breakdown)
        self.assertIn("c2", score.breakdown)

    def test_score_with_no_match(self):
        engine = make_engine()
        rubric = Rubric(
            name="specific",
            criteria=[
                RubricCriterion(id="c1", label="quantum entanglement", weight=1, scale=5),
            ],
        )
        score = engine.score("simple text response", rubric)
        self.assertEqual(score.value, 0.0)

    def test_weighted_criteria(self):
        engine = make_engine()
        rubric = Rubric(
            name="weighted",
            criteria=[
                RubricCriterion(id="c1", label="critical", weight=10, scale=5),
                RubricCriterion(id="c2", label="minor", weight=1, scale=5),
            ],
        )
        score = engine.score("critical minor", rubric)
        self.assertGreater(score.value, 0.0)

    def test_score_judge_name(self):
        engine = make_engine()
        rubric = make_rubric("my-judge")
        score = engine.score("test", rubric)
        self.assertEqual(score.judge, "my-judge")


# ── route() ─────────────────────────────────────────────────────


class TestRoute(unittest.TestCase):
    def test_pass_routes_to_workflow(self):
        engine = make_engine()
        verdict = Verdict(
            overall=VerdictStatus.PASS,
            scores={"ac_check": 0.8, "relevance": 0.9},
        )
        action = engine.route(verdict)
        self.assertEqual(action.target, RouteTarget.WORKFLOW)

    def test_pass_with_concerns_routes_to_workflow(self):
        engine = make_engine()
        verdict = Verdict(
            overall=VerdictStatus.PASS_WITH_CONCERNS,
            scores={"ac_check": 0.6, "relevance": 0.7},
        )
        action = engine.route(verdict)
        self.assertEqual(action.target, RouteTarget.WORKFLOW)

    def test_fail_low_ac_routes_to_spec(self):
        engine = make_engine()
        verdict = Verdict(
            overall=VerdictStatus.FAIL,
            scores={"ac_check": 0.2, "relevance": 0.8, "faithfulness": 0.8, "context_precision": 0.8},
        )
        action = engine.route(verdict)
        self.assertEqual(action.target, RouteTarget.SPEC)

    def test_fail_low_faithfulness_routes_to_ooda(self):
        engine = make_engine()
        verdict = Verdict(
            overall=VerdictStatus.FAIL,
            scores={"ac_check": 0.8, "relevance": 0.8, "faithfulness": 0.2, "context_precision": 0.8},
        )
        action = engine.route(verdict)
        self.assertEqual(action.target, RouteTarget.OODA)

    def test_fail_hallucination_routes_to_ooda(self):
        engine = make_engine()
        verdict = Verdict(
            overall=VerdictStatus.FAIL,
            scores={"ac_check": 0.8, "relevance": 0.8, "faithfulness": 0.6, "context_precision": 0.8},
            failures=["high_hallucination_risk"],
        )
        action = engine.route(verdict)
        self.assertEqual(action.target, RouteTarget.OODA)

    def test_fail_low_relevance_routes_to_workflow(self):
        engine = make_engine()
        verdict = Verdict(
            overall=VerdictStatus.FAIL,
            scores={"ac_check": 0.8, "relevance": 0.2, "faithfulness": 0.8, "context_precision": 0.8},
        )
        action = engine.route(verdict)
        self.assertEqual(action.target, RouteTarget.WORKFLOW)

    def test_fail_low_context_routes_to_ooda(self):
        engine = make_engine()
        verdict = Verdict(
            overall=VerdictStatus.FAIL,
            scores={"ac_check": 0.8, "relevance": 0.8, "faithfulness": 0.8, "context_precision": 0.2},
        )
        action = engine.route(verdict)
        self.assertEqual(action.target, RouteTarget.OODA)

    def test_fail_default_routes_to_spec(self):
        engine = make_engine()
        verdict = Verdict(
            overall=VerdictStatus.FAIL,
            scores={"ac_check": 0.6, "relevance": 0.6, "faithfulness": 0.6, "context_precision": 0.6},
        )
        action = engine.route(verdict)
        self.assertEqual(action.target, RouteTarget.SPEC)

    def test_route_has_reason(self):
        engine = make_engine()
        verdict = Verdict(overall=VerdictStatus.PASS, scores={})
        action = engine.route(verdict)
        self.assertIsInstance(action.reason, str)
        self.assertGreater(len(action.reason), 0)


# ── evaluate() AC coverage ──────────────────────────────────────


class TestACCoverage(unittest.TestCase):
    """Test that AC coverage actually works when ACs are passed."""

    def test_no_ac_returns_0_5(self):
        """Without ACs, ac_check score is 0.5 (default)."""
        engine = make_engine()
        verdict = engine.evaluate("some response", "context", "spec")
        self.assertEqual(verdict.scores["ac_check"], 0.5)
        self.assertIn("no_criteria_provided", verdict.failures)

    def test_empty_ac_list_returns_0_5(self):
        """Empty AC list behaves same as no ACs."""
        engine = make_engine()
        verdict = engine.evaluate("response", "context", "spec", acceptance_criteria=[])
        self.assertEqual(verdict.scores["ac_check"], 0.5)

    def test_no_ac_coverage_leads_to_fail(self):
        """When ACs exist but response covers none, ac_check is low → FAIL."""
        engine = make_engine()
        verdict = engine.evaluate(
            response="The system uses quantum computing for blockchain",
            context="quantum blockchain analysis",
            spec="quantum blockchain analysis",
            acceptance_criteria=[
                "User can register with email",
                "User receives confirmation email",
                "User can reset password",
            ],
        )
        # AC score should be low (0.25) because response doesn't cover any ACs
        self.assertLess(verdict.scores["ac_check"], 0.5)
        self.assertIn("ac_low_coverage", verdict.failures[0])

    def test_full_ac_coverage_leads_to_high_score(self):
        """When response covers all ACs, ac_check is 1.0."""
        engine = make_engine()
        verdict = engine.evaluate(
            response=(
                "The user can register with email and password. "
                "After registration the user receives a confirmation email. "
                "The user can reset password via the forgot password flow."
            ),
            context="User registration system with email confirmation and password reset",
            spec="Build user registration system",
            acceptance_criteria=[
                "User can register with email",
                "User receives confirmation email",
                "User can reset password",
            ],
        )
        self.assertEqual(verdict.scores["ac_check"], 1.0)

    def test_partial_ac_coverage(self):
        """When response covers some ACs, score is proportional."""
        engine = make_engine()
        # Only first AC is covered; other two are about completely different features
        verdict = engine.evaluate(
            response=(
                "The calculator performs arithmetic addition of two numbers"
            ),
            context="Calculator arithmetic module with addition support",
            spec="Build calculator",
            acceptance_criteria=[
                "Calculator performs addition correctly",
                "User can export results to PDF format",
                "System supports multi-language localization",
            ],
        )
        # "Calculator performs addition correctly" covered (high overlap).
        # "export results to PDF" NOT covered (no overlap).
        # "multi-language localization" NOT covered (no overlap).
        # ratio 1/3 = 0.33 → ac_low_coverage issue
        ac_issues = [f for f in verdict.failures if "ac_low_coverage" in f]
        self.assertEqual(len(ac_issues), 1)

    def test_ac_none_treated_as_empty(self):
        """None acceptance_criteria is same as empty list."""
        engine = make_engine()
        verdict = engine.evaluate("response", "context", "spec", acceptance_criteria=None)
        self.assertEqual(verdict.scores["ac_check"], 0.5)

    def test_ac_check_in_verdict(self):
        """ac_check always appears in verdict.scores."""
        engine = make_engine()
        verdict = engine.evaluate("x", "", "", acceptance_criteria=["ac1"])
        self.assertIn("ac_check", verdict.scores)

    def test_full_coverage_all_acs_score_1(self):
        """All ACs covered → ac_check score is exactly 1.0."""
        engine = make_engine()
        response = (
            "User registers with email address. "
            "Confirmation email is sent. "
            "Password reset flow works."
        )
        verdict = engine.evaluate(
            response=response,
            context="registration system",
            spec="build registration",
            acceptance_criteria=[
                "User registers with email",
                "Confirmation email is sent",
                "Password reset works",
            ],
        )
        self.assertEqual(verdict.scores["ac_check"], 1.0)


# ── Pipeline AC threading ────────────────────────────────────────


class TestPipelineACThreading(unittest.TestCase):
    """Test that Pipeline passes ACs from spec to Judge."""

    def test_pipeline_passes_acs_to_judge(self):
        """Pipeline extracts ACs linked to requirement and passes to Judge."""
        from uuid import uuid4
        from scripts.core.pipeline import EndToEndPipeline
        from scripts.core.types.spec import Requirement, AC, StructuredSpec
        from scripts.core.enums import Priority

        pipeline = EndToEndPipeline()

        # Create spec with known ACs
        req_id = uuid4()
        ac1_id = uuid4()
        ac2_id = uuid4()
        pipeline.spec_engine.parse = lambda path: StructuredSpec(
            requirements=[
                Requirement(id=req_id, title="Build login", description="Login system", priority=Priority.MUST),
            ],
            acceptance_criteria=[
                AC(id=ac1_id, requirement_id=req_id, description="User enters credentials"),
                AC(id=ac2_id, requirement_id=req_id, description="System validates password"),
            ],
        )

        # Capture what judge.evaluate receives
        captured_kwargs = {}
        original_evaluate = pipeline.judge.evaluate

        def capture_evaluate(**kwargs):
            captured_kwargs.update(kwargs)
            return original_evaluate(**kwargs)

        pipeline.judge.evaluate = capture_evaluate

        result = pipeline.run("Build login system")

        # Judge should have received ACs
        self.assertIn("acceptance_criteria", captured_kwargs)
        acs = captured_kwargs["acceptance_criteria"]
        self.assertEqual(len(acs), 2)
        self.assertIn("User enters credentials", acs)
        self.assertIn("System validates password", acs)

    def test_pipeline_no_acs_when_spec_has_none(self):
        """Pipeline passes empty list when spec has no ACs for a requirement."""
        from uuid import uuid4
        from scripts.core.pipeline import EndToEndPipeline
        from scripts.core.types.spec import Requirement, StructuredSpec
        from scripts.core.enums import Priority

        pipeline = EndToEndPipeline()

        req_id = uuid4()
        pipeline.spec_engine.parse = lambda path: StructuredSpec(
            requirements=[
                Requirement(id=req_id, title="Task", description="Do something", priority=Priority.MUST),
            ],
            acceptance_criteria=[],  # No ACs
        )

        captured = {}
        original_evaluate = pipeline.judge.evaluate

        def capture(**kwargs):
            captured.update(kwargs)
            return original_evaluate(**kwargs)

        pipeline.judge.evaluate = capture
        pipeline.run("Do something")

        self.assertIn("acceptance_criteria", captured)
        self.assertEqual(len(captured["acceptance_criteria"]), 0)


if __name__ == "__main__":
    unittest.main()
