"""CodeAI Platform — OODA Pipeline.

Orchestrates the four OODA steps: Observe → Orient → Decide → Act.
Steps are injected, pipeline has no knowledge of step implementations.
"""

from scripts.core.errors import OODAError
from scripts.core.knowledge_layer import KnowledgeLayer
from scripts.core.memory_layer import MemoryLayer
from scripts.core.ooda.steps import (
    ActStep,
    DecideStep,
    ObserveStep,
    OrientStep,
)
from scripts.core.ooda.state import OODARuntimeState
from scripts.core.types.project import ProjectContext
from scripts.core.types.workflow import Task


class OODAPipeline:
    """Orchestrates the OODA cycle.

    Pipeline order:
        1. Observe — gather knowledge and memory
        2. Orient — analyze context
        3. Decide — build plan
        4. Act — execute (stub in v1)

    Each step receives ProjectContext, returns ProjectContext.
    Pipeline is interruptible — state tracks current step.
    """

    def __init__(
        self,
        knowledge: KnowledgeLayer,
        memory: MemoryLayer,
    ) -> None:
        self._observe = ObserveStep(knowledge, memory)
        self._orient = OrientStep()
        self._decide = DecideStep()
        self._act = ActStep()

    def run(
        self,
        ctx: ProjectContext,
        task: Task,
        state: OODARuntimeState,
    ) -> ProjectContext:
        """Run full OODA cycle.

        Checks state for interruption points and resumes from there.

        Args:
            ctx: Project context to populate.
            task: Task being executed.
            state: Runtime state for tracking.

        Returns:
            Populated ProjectContext.
        """
        try:
            # Step 1: Observe
            if state.current_step in ("", "observe"):
                state.advance("observe")
                ctx = self._observe.execute(ctx, task)

            # Step 2: Orient
            if state.current_step in ("observe", "orient"):
                state.advance("orient")
                ctx = self._orient.execute(ctx, task)

            # Step 3: Decide
            if state.current_step in ("orient", "decide"):
                state.advance("decide")
                ctx = self._decide.execute(ctx, task)

            # Step 4: Act
            if state.current_step in ("decide", "act"):
                state.advance("act")
                artifacts = self._act.execute(ctx, task)

            state.complete()
            return ctx

        except OODAError:
            raise
        except Exception as e:
            state.fail(str(e))
            raise OODAError(
                f"Pipeline failed: {e}",
                code="OODA_PIPELINE_FAILED",
                recoverable=False,
                context={"task_id": str(task.uuid), "step": state.current_step},
                cause=e,
            ) from e

    def run_step(
        self,
        ctx: ProjectContext,
        task: Task,
        step_name: str,
    ) -> ProjectContext:
        """Run a single step (for resume).

        Args:
            ctx: Project context.
            task: Task being executed.
            step_name: Name of the step to run ("observe", "orient", "decide", "act").

        Returns:
            Updated ProjectContext.
        """
        steps = {
            "observe": self._observe,
            "orient": self._orient,
            "decide": self._decide,
            "act": self._act,
        }

        step = steps.get(step_name)
        if step is None:
            raise OODAError(
                f"Unknown step: {step_name}",
                code="OODA_UNKNOWN_STEP",
                recoverable=False,
                context={"step": step_name},
            )

        try:
            if step_name == "act":
                step.execute(ctx, task)
            else:
                ctx = step.execute(ctx, task)
            return ctx
        except OODAError:
            raise
        except Exception as e:
            raise OODAError(
                f"Step '{step_name}' failed: {e}",
                code="OODA_STEP_FAILED",
                recoverable=False,
                context={"task_id": str(task.uuid), "step": step_name},
                cause=e,
            ) from e
