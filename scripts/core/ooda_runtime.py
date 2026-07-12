"""CodeAI Platform — OODA Runtime (stub)."""

from uuid import UUID

from scripts.core.types import OODAResult, Task


class OODARuntime:
    """OODA Runtime — agent orchestration.

    Responsibilities:
        - Execute observe/orient/decide/act cycle per task
        - Manage shared state between agents
        - Validate plans (Files/Changes/Risks/Tests/Rollback)
        - Generate summaries for Judge Engine

    API:
        execute(task) -> OODAResult
        resume(task_id) -> OODAResult
        interrupt(task_id) -> None
    """

    def execute(self, task: Task) -> OODAResult:
        """Execute OODA cycle for a task.

        Args:
            task: Task to execute.

        Returns:
            OODAResult with outputs and summary.
        """
        raise NotImplementedError

    def resume(self, task_id: UUID) -> OODAResult:
        """Resume an interrupted task.

        Args:
            task_id: ID of the task to resume.

        Returns:
            OODAResult with outputs and summary.
        """
        raise NotImplementedError

    def interrupt(self, task_id: UUID) -> None:
        """Interrupt a running task.

        Args:
            task_id: ID of the task to interrupt.
        """
        raise NotImplementedError
