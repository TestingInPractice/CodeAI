"""CodeAI Platform — End-to-End Pipeline.

Connects all 6 subsystems + Event Bus into one executable flow:

    User Prompt
        → SpecEngine.generate()
        → SpecEngine.validate()
        → SpecEngine.approve()
        → SpecEngine.parse()
        → WorkflowEngine.start()
        → WorkflowEngine.next()
        → OODARuntime.execute()
        → KnowledgeLayer.search()/retrieve()
        → MemoryLayer.load()
        → JudgeEngine.evaluate()
        → WorkflowEngine.complete() or rollback()

No new abstractions. No new layers. Just wiring.
"""

from dataclasses import dataclass, field
from pathlib import Path
from uuid import uuid4

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
from scripts.core.ooda_runtime import OODARuntime
from scripts.core.spec_engine import SpecEngine
from scripts.core.types.common import Artifact
from scripts.core.types.knowledge import Knowledge
from scripts.core.types.memory import MemoryEntry
from scripts.core.types.ooda import OODAResult
from scripts.core.types.spec import StructuredSpec, ValidationResult
from scripts.core.types.workflow import Phase, Task
from scripts.core.workflow_engine import WorkflowEngine
from scripts.core.workflow.state import PhaseState, TaskState, WorkflowState

from scripts.core.memory.in_memory_repository import InMemoryMemoryRepository


@dataclass
class PipelineResult:
    """Result of a full pipeline execution."""
    prompt: str
    spec: StructuredSpec = field(default_factory=StructuredSpec)
    validation: ValidationResult = field(default_factory=lambda: ValidationResult(valid=True))
    phases_completed: list[str] = field(default_factory=list)
    phases_failed: list[str] = field(default_factory=list)
    ooda_results: list[OODAResult] = field(default_factory=list)
    judge_verdicts: list[dict] = field(default_factory=list)
    workflow_status: str = ""
    artifacts: list[Artifact] = field(default_factory=list)
    events: list[str] = field(default_factory=list)


class EndToEndPipeline:
    """End-to-end pipeline connecting all subsystems.

    Usage:
        pipeline = EndToEndPipeline()
        result = pipeline.run("Create a Python calculator")
    """

    def __init__(self):
        # Wire up all subsystems
        self.spec_engine = SpecEngine()
        self.event_bus = EventBus()
        self.knowledge = KnowledgeLayer()
        mem_repo = InMemoryMemoryRepository()
        self.memory = MemoryLayer(mem_repo)
        self.ooda = OODARuntime(self.knowledge, self.memory)
        self.judge = JudgeEngine()
        self.workflow = None

        # Track events
        self._events: list[str] = []
        self.event_bus.subscribe("*", lambda e: self._events.append(e.name))

    def run(self, prompt: str) -> PipelineResult:
        """Execute the full pipeline.

        Args:
            prompt: User's project description.

        Returns:
            PipelineResult with all artifacts and state.
        """
        result = PipelineResult(prompt=prompt, spec=StructuredSpec())

        # ── Phase 1: Spec Engine ──────────────────────────────
        self.event_bus.publish("spec.created", {"source": "spec_engine", "prompt": prompt[:100]})

        goals_path = self.spec_engine.generate(prompt)
        result.validation = self.spec_engine.validate(goals_path)

        if not result.validation.valid:
            result.workflow_status = "spec_invalid"
            return result

        self.spec_engine.approve(goals_path)
        result.spec = self.spec_engine.parse(goals_path)

        self.event_bus.publish("spec.validated", {"source": "spec_engine"})

        # ── Phase 2: Workflow Engine setup ────────────────────
        phases = self._create_phases(result.spec)
        state = WorkflowState(phases=phases)
        self.workflow = WorkflowEngine(state)

        # ── Phase 3: Execute each phase ───────────────────────
        processed: set[str] = set()
        while True:
            next_phase = self.workflow.next()
            if next_phase is None:
                break
            if next_phase.id in processed:
                break

            processed.add(next_phase.id)
            phase_result = self._execute_phase(next_phase, result)
            if phase_result == "completed":
                result.phases_completed.append(next_phase.id)
            else:
                result.phases_failed.append(next_phase.id)

        result.workflow_status = state.workflow_status.value
        result.artifacts = self._collect_artifacts(result)
        result.events = list(self._events)

        return result

    def _create_phases(self, spec: StructuredSpec) -> list[PhaseState]:
        """Create workflow phases from spec."""
        phases = []
        for i, req in enumerate(spec.requirements):
            phase_id = f"phase-{i+1}"
            task = TaskState(
                uuid=str(uuid4()),
                title=req.title,
                spec_ref=str(req.id),
            )
            phases.append(PhaseState(
                id=phase_id,
                title=req.title,
                tasks=[task],
                depends_on=[f"phase-{i}"] if i > 0 else [],
            ))
        return phases

    def _execute_phase(self, phase: PhaseState, result: PipelineResult) -> str:
        """Execute a single phase through OODA → Judge → Workflow."""
        # Start phase
        self.workflow.start(phase.id)
        self.event_bus.publish("phase.started", {"source": "workflow", "phase_id": phase.id})

        # Build task from phase
        task_state = phase.tasks[0]
        task = Task(
            uuid=uuid4(),
            title=task_state.title,
            description=f"Implement: {task_state.title}",
            spec_ref=task_state.spec_ref,
        )

        # Seed knowledge for this phase
        self._seed_knowledge(task.title)

        # Seed memory
        self._seed_memory(task.title)

        # ── OODA execute ──────────────────────────────────────
        ooda_result = self.ooda.execute(task)
        result.ooda_results.append(ooda_result)

        self.event_bus.publish("task.completed", {
            "source": "ooda",
            "task_id": str(task.uuid),
            "success": ooda_result.success,
        })

        # ── Judge evaluate ────────────────────────────────────
        # Extract acceptance criteria linked to this phase's requirement
        ac_descriptions: list[str] = []
        if task_state.spec_ref and result.spec:
            for ac in result.spec.acceptance_criteria:
                if str(ac.requirement_id) == task_state.spec_ref:
                    ac_descriptions.append(ac.description)

        verdict = self.judge.evaluate(
            response=ooda_result.summary,
            context=self._build_context(task.title),
            spec=task.title,
            acceptance_criteria=ac_descriptions,
        )

        route = self.judge.route(verdict)

        result.judge_verdicts.append({
            "phase": phase.id,
            "overall": verdict.overall.value,
            "confidence": verdict.confidence,
            "route": route.target.value,
        })

        self.event_bus.publish("judge.evaluated", {
            "source": "judge",
            "phase_id": phase.id,
            "overall": verdict.overall.value,
        })

        # ── Workflow complete or rollback ─────────────────────
        judge_passed = verdict.overall in (
            VerdictStatus.PASS,
            VerdictStatus.PASS_WITH_CONCERNS,
        )

        if judge_passed:
            task_state.status = TaskStatus.COMPLETED
            self.workflow.complete(phase.id, judge_passed=True)
            self.event_bus.publish("phase.completed", {"source": "workflow", "phase_id": phase.id})
            return "completed"
        else:
            self.workflow.rollback(phase.id, f"Judge {verdict.overall.value}")
            self.event_bus.publish("phase.rollback", {"source": "workflow", "phase_id": phase.id})
            return "failed"

    def _seed_knowledge(self, task_title: str):
        """Seed knowledge relevant to the task."""
        items = [
            Knowledge(
                id=uuid4(),
                source="architecture.md",
                kind=KnowledgeKind.DOCUMENT,
                content=f"Architecture pattern for {task_title}",
                score=0.9,
                metadata={"scope": "project"},
            ),
            Knowledge(
                id=uuid4(),
                source="best-practices.md",
                kind=KnowledgeKind.ARTICLE,
                content=f"Best practices for {task_title}",
                score=0.8,
                metadata={"scope": "project"},
            ),
        ]
        self.knowledge.index_all(items)

    def _seed_memory(self, task_title: str):
        """Seed memory relevant to the task."""
        entry = MemoryEntry(
            id=uuid4(),
            type=MemoryType.PROJECT_HISTORY,
            content=f"Previously worked on {task_title}",
            scope="project",
            metadata={"phase_id": task_title},
        )
        self.memory.store(entry)

    def _build_context(self, task_title: str) -> str:
        """Build context string for Judge evaluation."""
        knowledge_ctx = self.knowledge.search(task_title)
        items = [k.content for k in knowledge_ctx[:3]]
        return f"Task: {task_title}. Knowledge: {'; '.join(items)}"

    def _collect_artifacts(self, result: PipelineResult) -> list[Artifact]:
        """Collect all artifacts from execution."""
        artifacts = []
        for ooda_result in result.ooda_results:
            artifacts.extend(ooda_result.outputs)
        return artifacts
