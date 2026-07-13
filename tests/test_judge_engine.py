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


if __name__ == "__main__":
    unittest.main()
