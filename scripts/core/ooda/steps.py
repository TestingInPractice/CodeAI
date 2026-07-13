"""CodeAI Platform — OODA Pipeline Steps.

Each step is a separate class (SOLID - Single Responsibility).
Steps communicate exclusively via ProjectContext.

- ObserveStep: Gathers knowledge and memory context
- OrientStep: Analyzes context, history, requirements
- DecideStep: Builds plan, risks, rollback, tests
- ActStep: Executes (stub in v1), returns artifacts
"""

from pathlib import Path
from uuid import uuid4

from scripts.core.enums import KnowledgeType, MemoryType
from scripts.core.errors import OODAError
from scripts.core.knowledge_layer import KnowledgeLayer
from scripts.core.memory_layer import MemoryLayer
from scripts.core.types.common import Artifact, RuntimeContext
from scripts.core.types.knowledge import Knowledge
from scripts.core.types.memory import MemoryEntry
from scripts.core.types.project import ProjectContext
from scripts.core.types.workflow import Task


class ObserveStep:
    """Gathers context from Knowledge Layer and Memory Layer.

    Read-only — no generation, no decisions.
    Output: ProjectContext with knowledge and memory populated.
    """

    def __init__(
        self,
        knowledge: KnowledgeLayer,
        memory: MemoryLayer,
    ) -> None:
        self._knowledge = knowledge
        self._memory = memory

    def execute(self, ctx: ProjectContext, task: Task) -> ProjectContext:
        """Gather context for the task.

        Queries Knowledge Layer for architecture/best_practice/reference.
        Queries Memory Layer for project_history and decisions.
        """
        query = f"{task.title} {task.description}".strip()
        if not query:
            query = task.title

        # Gather knowledge
        try:
            arch_ctx = self._knowledge.retrieve(
                KnowledgeType.ARCHITECTURE, {"source": task.spec_ref or ""}
            )
            ctx.knowledge.extend(arch_ctx.items)
        except Exception:
            pass  # Non-fatal — knowledge is enrichment

        try:
            bp_ctx = self._knowledge.retrieve(KnowledgeType.BEST_PRACTICE, {})
            ctx.knowledge.extend(bp_ctx.items)
        except Exception:
            pass

        # Gather memory
        try:
            history = self._memory.load(query, scope="project")
            ctx.memory.extend(history)
        except Exception:
            pass  # Non-fatal — memory is enrichment

        try:
            decisions = self._memory.load(
                query, scope="project"
            )
            decisions = [
                e for e in decisions
                if e.type == MemoryType.DECISIONS
            ]
            ctx.memory.extend(decisions)
        except Exception:
            pass

        return ctx


class OrientStep:
    """Analyzes gathered context and produces orientation insights.

    Combines knowledge, memory, and requirements into a coherent analysis.
    """

    def execute(self, ctx: ProjectContext, task: Task) -> ProjectContext:
        """Analyze context and produce orientation.

        Builds a summary of what we know and what gaps exist.
        """
        # Analyze knowledge coverage
        knowledge_summary = self._summarize_knowledge(ctx.knowledge)

        # Analyze memory context
        memory_summary = self._summarize_memory(ctx.memory)

        # Build orientation insights in runtime context
        if ctx.runtime is None:
            ctx.runtime = RuntimeContext(project_root=Path("."))

        ctx.runtime.variables["orientation"] = {
            "task": task.title,
            "knowledge_coverage": knowledge_summary,
            "memory_context": memory_summary,
            "gaps": self._identify_gaps(ctx),
        }

        return ctx

    @staticmethod
    def _summarize_knowledge(knowledge: list[Knowledge]) -> dict:
        """Summarize available knowledge."""
        by_kind = {}
        for k in knowledge:
            by_kind.setdefault(k.kind.value, []).append(k)
        return {
            "total": len(knowledge),
            "by_kind": {k: len(v) for k, v in by_kind.items()},
        }

    @staticmethod
    def _summarize_memory(memory: list[MemoryEntry]) -> dict:
        """Summarize available memory."""
        by_type = {}
        for m in memory:
            by_type.setdefault(m.type.value, []).append(m)
        return {
            "total": len(memory),
            "by_type": {k: len(v) for k, v in by_type.items()},
        }

    @staticmethod
    def _identify_gaps(ctx: ProjectContext) -> list[str]:
        """Identify gaps in context."""
        gaps = []
        if not ctx.knowledge:
            gaps.append("No knowledge items found")
        if not ctx.memory:
            gaps.append("No memory history found")
        if not ctx.spec.requirements:
            gaps.append("No requirements in spec")
        return gaps


class DecideStep:
    """Builds execution plan, identifies risks, and defines rollback/tests.

    Produces a structured plan in runtime variables.
    """

    def execute(self, ctx: ProjectContext, task: Task) -> ProjectContext:
        """Build execution plan.

        Creates plan with: files, changes, risks, tests, rollback.
        """
        orientation = {}
        if ctx.runtime and "orientation" in ctx.runtime.variables:
            orientation = ctx.runtime.variables["orientation"]

        # Build plan
        plan = {
            "task_id": str(task.uuid),
            "task_title": task.title,
            "description": task.description,
            "files": [],
            "changes": [],
            "risks": [],
            "tests": [],
            "rollback": {
                "strategy": "git revert",
                "commits": [],
            },
        }

        # Identify files from spec_ref
        if task.spec_ref:
            plan["files"].append(task.spec_ref)

        # Identify risks from gaps
        gaps = orientation.get("gaps", [])
        for gap in gaps:
            plan["risks"].append({
                "description": gap,
                "severity": "medium",
                "mitigation": "Gather more context or proceed with caution",
            })

        # Define test strategy
        plan["tests"].append({
            "type": "unit",
            "description": f"Test coverage for {task.title}",
        })

        # Store plan in runtime
        if ctx.runtime is None:
            ctx.runtime = RuntimeContext(project_root=Path("."))
        ctx.runtime.variables["plan"] = plan

        return ctx


class ActStep:
    """Executes the plan (stub in v1).

    In v1, returns artifacts indicating what would be done.
    """

    def execute(self, ctx: ProjectContext, task: Task) -> list[Artifact]:
        """Execute the plan (v1 stub).

        Returns artifacts describing what was produced.
        """
        plan = {}
        if ctx.runtime and "plan" in ctx.runtime.variables:
            plan = ctx.runtime.variables["plan"]

        artifacts = []

        # Create summary artifact
        summary = self._build_summary(plan, task)
        artifact = Artifact(
            name=f"ooda-summary-{task.uuid}.md",
            path=Path(f".opencode/tasks/{task.uuid}/ooda-summary.md"),
            type="summary",
            checksum="",
            metadata={"task_id": str(task.uuid)},
        )
        artifacts.append(artifact)

        return artifacts

    @staticmethod
    def _build_summary(plan: dict, task: Task) -> str:
        """Build execution summary."""
        lines = [
            f"# OODA Execution Summary",
            f"",
            f"## Task: {task.title}",
            f"**ID:** {task.uuid}",
            f"**Status:** Completed (v1 stub)",
            f"",
            f"## Plan",
            f"- Files: {len(plan.get('files', []))}",
            f"- Risks: {len(plan.get('risks', []))}",
            f"- Tests: {len(plan.get('tests', []))}",
            f"",
            f"## Notes",
            f"This is a v1 stub execution.",
        ]
        return "\n".join(lines)
