"""CodeAI Platform — Judge Engine.

Evaluates OODA outputs against spec using 4 pillars:
1. AC Check — acceptance criteria coverage
2. Relevance — response answers the question
3. Faithfulness — response is grounded in context
4. Context Precision — context quality

Routes to next step: repeat (OODA), revise (Spec), retask (Workflow), or continue.
"""

import re
from scripts.core.enums import RouteTarget, VerdictStatus
from scripts.core.errors import JudgeError
from scripts.core.types import RouteAction, Rubric, Score, Verdict


def _tokenize(text: str) -> set[str]:
    """Extract lowercase word tokens."""
    return set(re.findall(r"\w+", text.lower()))


def _score_relevance(question: str, response: str) -> tuple[float, list[str]]:
    """Score how well response answers question."""
    qw = _tokenize(question)
    rw = _tokenize(response)

    issues: list[str] = []
    if not qw:
        return 0.5, ["empty_question"]

    overlap = len(qw & rw) / len(qw)

    if len(response.split()) < 3:
        issues.append("response_too_short")
    if "?" in question and "?" not in response and len(response.split()) < 10:
        issues.append("question_unanswered")

    if overlap >= 0.6:
        return 1.0, issues
    elif overlap >= 0.4:
        return 0.75, issues
    elif overlap >= 0.2:
        return 0.5, issues
    return 0.25, issues


def _score_faithfulness(response: str, context: str) -> tuple[float, list[str]]:
    """Score how grounded response is in context."""
    if not context:
        return 0.5, ["no_context_provided"]

    rw = _tokenize(response)
    cw = _tokenize(context)

    overlap = len(rw & cw) / len(rw) if rw else 0
    hallucinated = rw - cw
    hallucination_ratio = len(hallucinated) / len(rw) if rw else 0

    issues: list[str] = []
    if hallucination_ratio > 0.5:
        issues.append("high_hallucination_risk")
    if overlap < 0.3:
        issues.append("response_not_grounded_in_context")

    if overlap >= 0.7 and hallucination_ratio <= 0.2:
        return 1.0, issues
    elif overlap >= 0.5 and hallucination_ratio <= 0.3:
        return 0.75, issues
    elif overlap >= 0.3:
        return 0.5, issues
    return 0.25, issues


def _score_context_precision(context: str) -> tuple[float, list[str]]:
    """Score quality of the context itself."""
    if not context:
        return 0.0, ["empty_context"]

    issues: list[str] = []
    words = context.split()

    if len(words) < 10:
        issues.append("context_too_short")
    if len(words) > 4000:
        issues.append("context_too_long")

    has_structure = any(m in context for m in ["\n- ", "\n1.", "\n* ", "::", "##", "**"])
    if not has_structure:
        issues.append("context_unstructured")

    if 10 <= len(words) <= 2000:
        return 0.75, issues
    return 0.5, issues


def _score_ac(response: str, acceptance_criteria: list[str]) -> tuple[float, list[str]]:
    """Score acceptance criteria coverage."""
    if not acceptance_criteria:
        return 0.5, ["no_criteria_provided"]

    response_lower = response.lower()
    covered = 0

    for ac in acceptance_criteria:
        terms = _tokenize(ac)
        if terms and len(terms & _tokenize(response_lower)) / len(terms) >= 0.3:
            covered += 1

    ratio = covered / len(acceptance_criteria)
    issues: list[str] = []

    if ratio < 0.5:
        issues.append(f"ac_low_coverage: {covered}/{len(acceptance_criteria)}")

    if ratio < 0.3:
        return 0.25, issues
    elif ratio < 0.7:
        return 0.5, issues
    elif ratio < 1.0:
        return 0.75, issues
    return 1.0, issues


def _overall_status(scores: dict[str, float]) -> VerdictStatus:
    """Determine overall verdict from pillar scores."""
    if not scores:
        return VerdictStatus.FAIL

    avg = sum(scores.values()) / len(scores)

    if avg >= 0.7:
        return VerdictStatus.PASS
    elif avg >= 0.5:
        return VerdictStatus.PASS_WITH_CONCERNS
    return VerdictStatus.FAIL


class JudgeEngine:
    """Judge Engine — evaluation and routing.

    Evaluates OODA outputs against spec using 4 pillars:
    1. AC Check — acceptance criteria coverage
    2. Relevance — response answers the question
    3. Faithfulness — response is grounded in context
    4. Context Precision — context quality

    Routes to next step based on verdict.
    """

    def __init__(self, pass_threshold: float = 0.5):
        """Initialize Judge Engine.

        Args:
            pass_threshold: Minimum average score to PASS (default 0.5).
        """
        self._pass_threshold = pass_threshold

    def evaluate(
        self,
        response: str,
        context: str = "",
        spec: str = "",
    ) -> Verdict:
        """Full evaluation: AC + relevance + faithfulness + context precision.

        Args:
            response: Response to evaluate.
            context: Context for evaluation (knowledge base, docs).
            spec: Spec text (question/prompt that generated the response).

        Returns:
            Verdict with overall status, scores, and failures.
        """
        if not response:
            raise JudgeError("Cannot evaluate empty response", code="JUDGE_EMPTY_RESPONSE")

        ac_scores = _score_ac(response, [])
        rel_scores = _score_relevance(spec or "", response)
        faith_scores = _score_faithfulness(response, context)
        ctx_scores = _score_context_precision(context)

        scores = {
            "ac_check": ac_scores[0],
            "relevance": rel_scores[0],
            "faithfulness": faith_scores[0],
            "context_precision": ctx_scores[0],
        }

        all_issues = ac_scores[1] + rel_scores[1] + faith_scores[1] + ctx_scores[1]
        avg = sum(scores.values()) / len(scores)

        return Verdict(
            overall=_overall_status(scores),
            scores=scores,
            failures=all_issues,
            confidence=avg,
        )

    def score(self, response: str, rubric: Rubric) -> Score:
        """Score response against a specific rubric.

        Args:
            response: Response to score.
            rubric: Rubric with criteria to score against.

        Returns:
            Score with value and breakdown per criterion.
        """
        if not rubric.criteria:
            return Score(value=0.0, breakdown={}, judge=rubric.name)

        breakdown: dict[str, float] = {}
        total_weight = 0
        weighted_sum = 0.0

        response_tokens = _tokenize(response)

        for criterion in rubric.criteria:
            criterion_tokens = _tokenize(criterion.label)
            if criterion_tokens:
                overlap = len(response_tokens & criterion_tokens) / len(criterion_tokens)
            else:
                overlap = 0.0

            normalized = min(overlap * criterion.scale, criterion.scale)
            breakdown[criterion.id] = normalized

            weighted_sum += normalized * criterion.weight
            total_weight += criterion.scale * criterion.weight

        value = weighted_sum / total_weight if total_weight > 0 else 0.0

        return Score(value=round(value, 3), breakdown=breakdown, judge=rubric.name)

    def route(self, verdict: Verdict) -> RouteAction:
        """Determine next step based on verdict.

        Routing logic:
        - PASS → continue (workflow proceeds)
        - PASS_WITH_CONCERNS → continue with warnings
        - FAIL + ac_check low → revise spec (AC not met)
        - FAIL + faithfulness low → repeat OODA (hallucination)
        - FAIL + relevance low → retask workflow (wrong direction)
        - FAIL + context low → repeat OODA (need better context)
        - FAIL default → revise spec

        Args:
            verdict: Verdict from evaluate().

        Returns:
            RouteAction with target and reason.
        """
        if verdict.overall in (VerdictStatus.PASS, VerdictStatus.PASS_WITH_CONCERNS):
            return RouteAction(
                target=RouteTarget.WORKFLOW,
                reason=f"Verdict: {verdict.overall.value}",
            )

        scores = verdict.scores
        failures = verdict.failures

        ac_score = scores.get("ac_check", 1.0)
        faith_score = scores.get("faithfulness", 1.0)
        rel_score = scores.get("relevance", 1.0)
        ctx_score = scores.get("context_precision", 1.0)

        if ac_score < 0.5:
            return RouteAction(
                target=RouteTarget.SPEC,
                reason="AC coverage too low — revise spec",
            )

        if faith_score < 0.5 or any("hallucination" in f for f in failures):
            return RouteAction(
                target=RouteTarget.OODA,
                reason="Faithfulness too low — repeat with grounding",
            )

        if rel_score < 0.5:
            return RouteAction(
                target=RouteTarget.WORKFLOW,
                reason="Relevance too low — retask workflow",
            )

        if ctx_score < 0.5:
            return RouteAction(
                target=RouteTarget.OODA,
                reason="Context quality poor — repeat with better context",
            )

        return RouteAction(
            target=RouteTarget.SPEC,
            reason="Multiple failures — revise spec",
        )
