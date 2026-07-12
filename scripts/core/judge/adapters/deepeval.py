"""CodeAI Platform — DeepEval Adapter (stub)."""

from scripts.core.types import Score, Verdict


class DeepEvalAdapter:
    """DeepEval Adapter — optional integration with DeepEval.

    Status: Stub. This is one adapter among possible judge implementations.

    Responsibilities:
        - Bridge to DeepEval's 50+ metrics
        - Use G-Eval for custom rubrics
        - Use DAG metric for structural checks

    Note: DeepEval is one tool in the Judge Engine, not the foundation.
    This adapter can be replaced without affecting the rest of the system.
    """

    def __init__(self):
        raise NotImplementedError("DeepEval adapter not yet implemented")

    def evaluate(self, response: str, context: str, spec: str) -> Verdict:
        """Evaluate using DeepEval metrics."""
        raise NotImplementedError

    def score(self, response: str, metric: str) -> Score:
        """Score using a specific DeepEval metric."""
        raise NotImplementedError
