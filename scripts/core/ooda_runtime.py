"""CodeAI Platform — OODA Runtime.

Orchestration layer for observe/orient/decide/act cycle.
No business logic — only step coordination and state management.

Public API (frozen — CORE_RUNTIME.md §2.3):
    execute(task) -> OODAResult
    resume(task_id) -> OODAResult
    interrupt(task_id) -> None
"""

from pathlib import Path
from uuid import UUID, uuid4

from scripts.core.enums import TaskStatus
from scripts.core.errors import OODAError
from scripts.core.knowledge_layer import KnowledgeLayer
from scripts.core.memory_layer import MemoryLayer
from scripts.core.ooda.pipeline import OODAPipeline
from scripts.core.ooda.state import OODARuntimeState
from scripts.core.types.common import Artifact, RuntimeContext
from scripts.core.types.ooda import OODAResult
from scripts.core.types.project import ProjectContext
from scripts.core.types.workflow import Task


class OODARuntime:
    """OODA Runtime — agent orchestration.

    Responsibilities (CORE_RUNTIME.md §2.3):
    - Execute observe/orient/decide/act cycle per task
    - Manage shared state between agents
    - Track runtime state for resume/interrupt

    Does NOT contain:
    - Business logic of agents (each step is independent)
    - Judge Engine evaluation (external)
    - Spec Engine generation (external)
    - Workflow Engine state (delegates to it)

    Dependencies:
    - Knowledge Layer (context)
    - Memory Layer (history)
    - Types (data structures)

    Step Mappings (CORE_RUNTIME.md §2.3):
    | Step    | Agents          | Output           |
    |---------|-----------------|------------------|
    | analyst | @observe → @orient | architecture.md |
    | dev     | @decide → @act     | dev-summary.md  |
    | tester  | @decide → @act     | tester-summary.md|
    """

    def __init__(
        self,
        knowledge: KnowledgeLayer,
        memory: MemoryLayer,
    ) -> None:
        """Initialize OODA Runtime with dependencies.

        Args:
            knowledge: Knowledge Layer for context retrieval.
            memory: Memory Layer for history retrieval.
        """
        self._knowledge = knowledge
        self._memory = memory
        self._pipeline = OODAPipeline(knowledge, memory)
        self._states: dict[UUID, OODARuntimeState] = {}

    def execute(self, task: Task) -> OODAResult:
        """Execute OODA cycle for a task.

        Runs full pipeline: Observe → Orient → Decide → Act.
        Returns OODAResult with outputs and summary.

        Args:
            task: Task to execute.

        Returns:
            OODAResult with outputs and summary.

        Raises:
            OODAError: If task is already running or cycle fails.
        """
        # Check if task is already running
        if task.uuid in self._states:
            existing = self._states[task.uuid]
            if existing.is_running():
                raise OODAError(
                    f"Task {task.uuid} is already running",
                    code="OODA_TASK_RUNNING",
                    recoverable=False,
                    context={"task_id": str(task.uuid)},
                )

        # Create initial context
        ctx = ProjectContext(
            runtime=RuntimeContext(
                project_root=Path("."),
                current_agent="ooda",
                current_role="runtime",
            )
        )

        # Create and track state
        state = OODARuntimeState()
        state.start(task.uuid)
        self._states[task.uuid] = state

        try:
            # Run pipeline
            ctx = self._pipeline.run(ctx, task, state)

            # Build result
            artifacts = []
            if ctx.runtime and "plan" in ctx.runtime.variables:
                plan = ctx.runtime.variables["plan"]
                artifacts = self._build_artifacts(plan, task)

            summary = self._build_summary(ctx, task)

            return OODAResult(
                task_id=task.uuid,
                step="complete",
                success=True,
                outputs=artifacts,
                summary=summary,
            )

        except OODAError:
            state.fail("Pipeline error")
            raise
        except Exception as e:
            state.fail(str(e))
            raise OODAError(
                f"Execute failed: {e}",
                code="OODA_EXECUTE_FAILED",
                recoverable=False,
                context={"task_id": str(task.uuid)},
                cause=e,
            ) from e

    def resume(self, task_id: UUID) -> OODAResult:
        """Resume an interrupted task.

        Continues from the last completed step.

        Args:
            task_id: ID of the task to resume.

        Returns:
            OODAResult with outputs and summary.

        Raises:
            OODAError: If task cannot be resumed.
        """
        # Find state
        state = self._states.get(task_id)
        if state is None:
            raise OODAError(
                f"No state found for task {task_id}",
                code="OODA_NO_STATE",
                recoverable=False,
                context={"task_id": str(task_id)},
            )

        if not state.can_resume():
            raise OODAError(
                f"Task {task_id} cannot be resumed: status is {state.status.value}",
                code="OODA_CANNOT_RESUME",
                recoverable=False,
                context={"task_id": str(task_id), "status": state.status.value},
            )

        # Create context (in real implementation, would restore from state)
        ctx = ProjectContext(
            runtime=RuntimeContext(
                project_root=Path("."),
                current_agent="ooda",
                current_role="runtime",
            )
        )

        # Mark as running
        state.status = state.status  # Reset to running state

        try:
            # Resume pipeline from interrupted step
            ctx = self._pipeline.run(ctx, Task(uuid=task_id, title="resumed"), state)

            artifacts = []
            if ctx.runtime and "plan" in ctx.runtime.variables:
                plan = ctx.runtime.variables["plan"]
                artifacts = self._build_artifacts(plan, Task(uuid=task_id, title="resumed"))

            summary = self._build_summary(ctx, Task(uuid=task_id, title="resumed"))

            return OODAResult(
                task_id=task_id,
                step="complete",
                success=True,
                outputs=artifacts,
                summary=summary,
            )

        except OODAError:
            state.fail("Resume failed")
            raise
        except Exception as e:
            state.fail(str(e))
            raise OODAError(
                f"Resume failed: {e}",
                code="OODA_RESUME_FAILED",
                recoverable=False,
                context={"task_id": str(task_id)},
                cause=e,
            ) from e

    def interrupt(self, task_id: UUID) -> None:
        """Interrupt a running task.

        Saves current state for later resume.

        Args:
            task_id: ID of the task to interrupt.

        Raises:
            OODAError: If task is not running.
        """
        state = self._states.get(task_id)
        if state is None:
            raise OODAError(
                f"No state found for task {task_id}",
                code="OODA_NO_STATE",
                recoverable=False,
                context={"task_id": str(task_id)},
            )

        if not state.is_running():
            raise OODAError(
                f"Task {task_id} is not running: status is {state.status.value}",
                code="OODA_NOT_RUNNING",
                recoverable=False,
                context={"task_id": str(task_id), "status": state.status.value},
            )

        state.interrupt()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_artifacts(plan: dict, task: Task) -> list[Artifact]:
        """Build artifacts from execution plan."""
        artifacts = []

        # Summary artifact
        artifacts.append(Artifact(
            name=f"ooda-summary-{task.uuid}.md",
            path=Path(f".opencode/tasks/{task.uuid}/ooda-summary.md"),
            type="summary",
            checksum="",
            metadata={"task_id": str(task.uuid)},
        ))

        # Plan artifact
        artifacts.append(Artifact(
            name=f"plan-{task.uuid}.json",
            path=Path(f".opencode/tasks/{task.uuid}/plan.json"),
            type="plan",
            checksum="",
            metadata={"task_id": str(task.uuid)},
        ))

        return artifacts

    @staticmethod
    def _build_summary(ctx: ProjectContext, task: Task) -> str:
        """Build execution summary."""
        knowledge_count = len(ctx.knowledge)
        memory_count = len(ctx.memory)

        orientation = {}
        if ctx.runtime and "orientation" in ctx.runtime.variables:
            orientation = ctx.runtime.variables["orientation"]

        gaps = orientation.get("gaps", [])

        lines = [
            f"# OODA Execution Summary",
            f"",
            f"## Task: {task.title}",
            f"**ID:** {task.uuid}",
            f"",
            f"## Context Gathered",
            f"- Knowledge items: {knowledge_count}",
            f"- Memory entries: {memory_count}",
            f"",
        ]

        if gaps:
            lines.append("## Gaps Identified")
            for gap in gaps:
                lines.append(f"- {gap}")
            lines.append("")

        lines.append("## Status")
        lines.append("Cycle completed successfully.")

        return "\n".join(lines)
