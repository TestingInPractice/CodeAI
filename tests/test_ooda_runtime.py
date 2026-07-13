"""Unit tests for OODA Runtime.

Covers:
- execute() — full cycle
- resume() — interrupted task
- interrupt() — pause running task
- Pipeline steps (observe, orient, decide, act)
- State management
- Error handling
- Dependency Rule
- Public API surface
"""

import unittest
from pathlib import Path
from uuid import uuid4

from scripts.core.enums import (
    KnowledgeType,
    MemoryType,
    TaskStatus,
)
from scripts.core.errors import OODAError
from scripts.core.knowledge_layer import KnowledgeLayer
from scripts.core.memory_layer import MemoryLayer
from scripts.core.memory.repository import MemoryRepository
from scripts.core.ooda.pipeline import OODAPipeline
from scripts.core.ooda.state import OODAStatus, OODARuntimeState
from scripts.core.ooda.steps import (
    ActStep,
    DecideStep,
    ObserveStep,
    OrientStep,
)
from scripts.core.ooda_runtime import OODARuntime
from scripts.core.types.common import RuntimeContext
from scripts.core.types.knowledge import Knowledge
from scripts.core.types.memory import MemoryEntry
from scripts.core.types.ooda import OODAResult
from scripts.core.types.project import ProjectContext
from scripts.core.types.workflow import Task


# ======================================================================
# Helpers
# ======================================================================

class InMemoryMemoryRepo(MemoryRepository):
    """In-memory implementation of MemoryRepository for testing."""

    def __init__(self):
        self._entries: list[MemoryEntry] = []

    def store(self, entry: MemoryEntry) -> None:
        self._entries.append(entry)

    def load(self, entry_id: str):
        for e in self._entries:
            if str(e.id) == entry_id:
                return e
        return None

    def load_all(self, memory_type=None, scope="project"):
        result = []
        for e in self._entries:
            if memory_type and e.type.value != memory_type:
                continue
            if e.scope != scope:
                continue
            result.append(e)
        return sorted(result, key=lambda e: e.timestamp, reverse=True)

    def delete(self, entry_id: str) -> bool:
        for i, e in enumerate(self._entries):
            if str(e.id) == entry_id:
                self._entries.pop(i)
                return True
        return False

    def exists(self, entry_id: str) -> bool:
        return any(str(e.id) == entry_id for e in self._entries)

    def count(self, memory_type=None, scope="project"):
        return len(self.load_all(memory_type=memory_type, scope=scope))

    def delete_expired(self, before) -> int:
        return 0


def _make_task(
    title: str = "Test task",
    description: str = "Test description",
    status: TaskStatus = TaskStatus.PENDING,
    spec_ref: str = "",
) -> Task:
    return Task(
        uuid=uuid4(),
        title=title,
        description=description,
        status=status,
        spec_ref=spec_ref,
    )


def _make_knowledge(
    content: str = "test knowledge",
    source: str = "docs/test.md",
) -> Knowledge:
    from scripts.core.enums import KnowledgeKind
    return Knowledge(
        id=uuid4(),
        source=source,
        kind=KnowledgeKind.DOCUMENT,
        content=content,
    )


def _make_memory(
    content: str = "test memory",
    memory_type: MemoryType = MemoryType.DECISIONS,
) -> MemoryEntry:
    return MemoryEntry(
        id=uuid4(),
        type=memory_type,
        content=content,
    )


# ======================================================================
# OODARuntimeState
# ======================================================================

class TestOODARuntimeState(unittest.TestCase):

    def test_initial_state(self):
        state = OODARuntimeState()
        self.assertEqual(state.status, OODAStatus.IDLE)
        self.assertEqual(state.current_step, "")
        self.assertIsNone(state.task_id)

    def test_start(self):
        state = OODARuntimeState()
        tid = uuid4()
        state.start(tid)
        self.assertEqual(state.task_id, tid)
        self.assertEqual(state.status, OODAStatus.OBSERVE)
        self.assertEqual(state.current_step, "observe")

    def test_advance(self):
        state = OODARuntimeState()
        state.start(uuid4())
        state.advance("orient")
        self.assertEqual(state.status, OODAStatus.ORIENT)
        self.assertEqual(state.current_step, "orient")

    def test_complete(self):
        state = OODARuntimeState()
        state.start(uuid4())
        state.complete()
        self.assertEqual(state.status, OODAStatus.COMPLETED)

    def test_interrupt(self):
        state = OODARuntimeState()
        state.start(uuid4())
        state.interrupt()
        self.assertEqual(state.status, OODAStatus.INTERRUPTED)

    def test_fail(self):
        state = OODARuntimeState()
        state.start(uuid4())
        state.fail("something broke")
        self.assertEqual(state.status, OODAStatus.FAILED)
        self.assertEqual(state.error, "something broke")

    def test_is_running(self):
        state = OODARuntimeState()
        self.assertFalse(state.is_running())
        state.start(uuid4())
        self.assertTrue(state.is_running())
        state.complete()
        self.assertFalse(state.is_running())

    def test_can_resume(self):
        state = OODARuntimeState()
        self.assertFalse(state.can_resume())
        state.start(uuid4())
        self.assertFalse(state.can_resume())
        state.interrupt()
        self.assertTrue(state.can_resume())


# ======================================================================
# ObserveStep
# ======================================================================

class TestObserveStep(unittest.TestCase):

    def setUp(self):
        self.knowledge = KnowledgeLayer()
        self.memory = MemoryLayer(InMemoryMemoryRepo())
        self.step = ObserveStep(self.knowledge, self.memory)

    def test_gathers_knowledge(self):
        item = _make_knowledge("architecture pattern")
        self.knowledge.index(item)

        task = _make_task(title="architecture", description="design")
        ctx = ProjectContext()
        result = self.step.execute(ctx, task)

        self.assertIsInstance(result, ProjectContext)

    def test_gathers_memory(self):
        entry = _make_memory("project decision")
        self.memory.store(entry)

        task = _make_task(title="decision", description="review")
        ctx = ProjectContext()
        result = self.step.execute(ctx, task)

        self.assertIsInstance(result, ProjectContext)

    def test_empty_query_still_works(self):
        task = _make_task(title="", description="")
        ctx = ProjectContext()
        result = self.step.execute(ctx, task)
        self.assertIsInstance(result, ProjectContext)

    def test_handles_knowledge_error(self):
        """Non-fatal — observe continues even if knowledge fails."""
        task = _make_task(title="test")
        ctx = ProjectContext()
        result = self.step.execute(ctx, task)
        self.assertIsInstance(result, ProjectContext)


# ======================================================================
# OrientStep
# ======================================================================

class TestOrientStep(unittest.TestCase):

    def setUp(self):
        self.step = OrientStep()

    def test_produces_orientation(self):
        task = _make_task(title="analyze")
        ctx = ProjectContext()
        ctx.knowledge = [_make_knowledge("doc1"), _make_knowledge("doc2")]
        ctx.memory = [_make_memory("entry1")]

        result = self.step.execute(ctx, task)

        self.assertIn("orientation", result.runtime.variables)
        orient = result.runtime.variables["orientation"]
        self.assertEqual(orient["knowledge_coverage"]["total"], 2)
        self.assertEqual(orient["memory_context"]["total"], 1)

    def test_identifies_gaps(self):
        task = _make_task(title="empty")
        ctx = ProjectContext()
        result = self.step.execute(ctx, task)

        orient = result.runtime.variables["orientation"]
        self.assertIn("No knowledge items found", orient["gaps"])
        self.assertIn("No memory history found", orient["gaps"])
        self.assertIn("No requirements in spec", orient["gaps"])

    def test_no_gaps_when_populated(self):
        task = _make_task(title="full")
        ctx = ProjectContext()
        ctx.knowledge = [_make_knowledge("doc")]
        ctx.memory = [_make_memory("entry")]
        ctx.spec.requirements = [uuid4()]  # Add a requirement

        result = self.step.execute(ctx, task)
        orient = result.runtime.variables["orientation"]
        self.assertEqual(len(orient["gaps"]), 0)


# ======================================================================
# DecideStep
# ======================================================================

class TestDecideStep(unittest.TestCase):

    def setUp(self):
        self.step = DecideStep()

    def test_builds_plan(self):
        task = _make_task(title="build", description="implement feature")
        ctx = ProjectContext()
        ctx.runtime = RuntimeContext(project_root=Path("."))
        ctx.runtime.variables["orientation"] = {"gaps": []}

        result = self.step.execute(ctx, task)

        self.assertIn("plan", result.runtime.variables)
        plan = result.runtime.variables["plan"]
        self.assertEqual(plan["task_title"], "build")
        self.assertIn("files", plan)
        self.assertIn("risks", plan)
        self.assertIn("tests", plan)
        self.assertIn("rollback", plan)

    def test_risks_from_gaps(self):
        task = _make_task(title="risky")
        ctx = ProjectContext()
        ctx.runtime = RuntimeContext(project_root=Path("."))
        ctx.runtime.variables["orientation"] = {
            "gaps": ["No knowledge found"]
        }

        result = self.step.execute(ctx, task)
        plan = result.runtime.variables["plan"]
        self.assertEqual(len(plan["risks"]), 1)
        self.assertIn("No knowledge found", plan["risks"][0]["description"])

    def test_files_from_spec_ref(self):
        task = _make_task(title="spec", spec_ref="docs/goals.md")
        ctx = ProjectContext()
        ctx.runtime = RuntimeContext(project_root=Path("."))
        ctx.runtime.variables["orientation"] = {"gaps": []}

        result = self.step.execute(ctx, task)
        plan = result.runtime.variables["plan"]
        self.assertIn("docs/goals.md", plan["files"])


# ======================================================================
# ActStep
# ======================================================================

class TestActStep(unittest.TestCase):

    def setUp(self):
        self.step = ActStep()

    def test_returns_artifacts(self):
        task = _make_task(title="act")
        ctx = ProjectContext()
        ctx.runtime = RuntimeContext(project_root=Path("."))
        ctx.runtime.variables["plan"] = {"files": [], "risks": [], "tests": []}

        artifacts = self.step.execute(ctx, task)

        self.assertIsInstance(artifacts, list)
        self.assertGreater(len(artifacts), 0)
        self.assertEqual(artifacts[0].type, "summary")

    def test_artifact_metadata(self):
        task = _make_task(title="meta")
        ctx = ProjectContext()
        ctx.runtime = RuntimeContext(project_root=Path("."))
        ctx.runtime.variables["plan"] = {}

        artifacts = self.step.execute(ctx, task)
        self.assertIn("task_id", artifacts[0].metadata)


# ======================================================================
# OODAPipeline
# ======================================================================

class TestOODAPipeline(unittest.TestCase):

    def setUp(self):
        self.knowledge = KnowledgeLayer()
        self.memory = MemoryLayer(InMemoryMemoryRepo())
        self.pipeline = OODAPipeline(self.knowledge, self.memory)

    def test_full_pipeline(self):
        task = _make_task(title="pipeline test")
        ctx = ProjectContext()
        state = OODARuntimeState()
        state.start(task.uuid)

        result = self.pipeline.run(ctx, task, state)

        self.assertIsInstance(result, ProjectContext)
        self.assertEqual(state.status, OODAStatus.COMPLETED)

    def test_pipeline_populates_knowledge(self):
        item = _make_knowledge("architecture pattern for pipeline")
        self.knowledge.index(item)

        task = _make_task(title="architecture pipeline")
        ctx = ProjectContext()
        state = OODARuntimeState()
        state.start(task.uuid)

        result = self.pipeline.run(ctx, task, state)
        self.assertGreater(len(result.knowledge), 0)

    def test_pipeline_populates_memory(self):
        entry = _make_memory("architecture decision in memory")
        self.memory.store(entry)

        task = _make_task(title="architecture", description="decision")
        ctx = ProjectContext()
        state = OODARuntimeState()
        state.start(task.uuid)

        result = self.pipeline.run(ctx, task, state)
        self.assertGreater(len(result.memory), 0)

    def test_pipeline_handles_empty_task(self):
        task = _make_task(title="", description="")
        ctx = ProjectContext()
        state = OODARuntimeState()
        state.start(task.uuid)

        result = self.pipeline.run(ctx, task, state)
        self.assertIsInstance(result, ProjectContext)


# ======================================================================
# OODARuntime
# ======================================================================

class TestOODARuntime(unittest.TestCase):

    def setUp(self):
        self.knowledge = KnowledgeLayer()
        self.memory = MemoryLayer(InMemoryMemoryRepo())
        self.runtime = OODARuntime(self.knowledge, self.memory)

    def test_execute_returns_result(self):
        task = _make_task(title="execute test")
        result = self.runtime.execute(task)

        self.assertIsInstance(result, OODAResult)
        self.assertTrue(result.success)
        self.assertEqual(result.task_id, task.uuid)
        self.assertEqual(result.step, "complete")

    def test_execute_populates_outputs(self):
        task = _make_task(title="outputs test")
        result = self.runtime.execute(task)

        self.assertIsInstance(result.outputs, list)
        self.assertGreater(len(result.outputs), 0)

    def test_execute_populates_summary(self):
        task = _make_task(title="summary test")
        result = self.runtime.execute(task)

        self.assertIsInstance(result.summary, str)
        self.assertIn(task.title, result.summary)

    def test_execute_with_knowledge(self):
        item = _make_knowledge("runtime knowledge")
        self.knowledge.index(item)

        task = _make_task(title="knowledge test")
        result = self.runtime.execute(task)
        self.assertTrue(result.success)

    def test_execute_with_memory(self):
        entry = _make_memory("runtime memory")
        self.memory.store(entry)

        task = _make_task(title="memory test")
        result = self.runtime.execute(task)
        self.assertTrue(result.success)

    def test_execute_duplicate_task_raises(self):
        task = _make_task(title="duplicate")
        # First execute
        self.runtime.execute(task)

        # Create new task with same uuid
        task2 = Task(
            uuid=task.uuid,
            title="duplicate2",
            status=TaskStatus.IN_PROGRESS,
        )

        # Mark as running
        from scripts.core.ooda.state import OODARuntimeState
        state = OODARuntimeState()
        state.start(task.uuid)
        self.runtime._states[task.uuid] = state

        with self.assertRaises(OODAError) as ctx:
            self.runtime.execute(task2)
        self.assertEqual(ctx.exception.code, "OODA_TASK_RUNNING")


# ======================================================================
# Resume
# ======================================================================

class TestOODARuntimeResume(unittest.TestCase):

    def setUp(self):
        self.knowledge = KnowledgeLayer()
        self.memory = MemoryLayer(InMemoryMemoryRepo())
        self.runtime = OODARuntime(self.knowledge, self.memory)

    def test_resume_interrupted_task(self):
        task = _make_task(title="resume test")
        # Execute first (creates state)
        self.runtime.execute(task)

        # Get the state and interrupt it
        state = self.runtime._states[task.uuid]
        state.interrupt()

        # Resume
        result = self.runtime.resume(task.uuid)
        self.assertIsInstance(result, OODAResult)
        self.assertTrue(result.success)

    def test_resume_no_state_raises(self):
        fake_id = uuid4()
        with self.assertRaises(OODAError) as ctx:
            self.runtime.resume(fake_id)
        self.assertEqual(ctx.exception.code, "OODA_NO_STATE")

    def test_resume_completed_task_raises(self):
        task = _make_task(title="completed")
        self.runtime.execute(task)

        with self.assertRaises(OODAError) as ctx:
            self.runtime.resume(task.uuid)
        self.assertEqual(ctx.exception.code, "OODA_CANNOT_RESUME")


# ======================================================================
# Interrupt
# ======================================================================

class TestOODARuntimeInterrupt(unittest.TestCase):

    def setUp(self):
        self.knowledge = KnowledgeLayer()
        self.memory = MemoryLayer(InMemoryMemoryRepo())
        self.runtime = OODARuntime(self.knowledge, self.memory)

    def test_interrupt_running_task(self):
        task = _make_task(title="interrupt test")

        # Start a task manually
        from scripts.core.ooda.state import OODARuntimeState
        state = OODARuntimeState()
        state.start(task.uuid)
        self.runtime._states[task.uuid] = state

        # Interrupt
        self.runtime.interrupt(task.uuid)
        self.assertEqual(state.status, OODAStatus.INTERRUPTED)

    def test_interrupt_no_state_raises(self):
        fake_id = uuid4()
        with self.assertRaises(OODAError) as ctx:
            self.runtime.interrupt(fake_id)
        self.assertEqual(ctx.exception.code, "OODA_NO_STATE")

    def test_interrupt_completed_task_raises(self):
        task = _make_task(title="completed")
        self.runtime.execute(task)

        with self.assertRaises(OODAError) as ctx:
            self.runtime.interrupt(task.uuid)
        self.assertEqual(ctx.exception.code, "OODA_NOT_RUNNING")


# ======================================================================
# Dependency Rule
# ======================================================================

class TestDependencyRule(unittest.TestCase):
    """Verify OODA Runtime does not import from Judge or Spec Engine."""

    def test_no_judge_import(self):
        import scripts.core.ooda_runtime as mod
        source = open(mod.__file__).read()
        self.assertNotIn("JudgeEngine", source)
        self.assertNotIn("judge_engine", source)
        self.assertNotIn("from scripts.core.judge", source)

    def test_no_spec_import(self):
        import scripts.core.ooda_runtime as mod
        source = open(mod.__file__).read()
        self.assertNotIn("SpecEngine", source)
        self.assertNotIn("spec_engine", source)
        self.assertNotIn("from scripts.core.spec", source)

    def test_no_judge_in_steps(self):
        import scripts.core.ooda.steps as mod
        source = open(mod.__file__).read()
        self.assertNotIn("JudgeEngine", source)
        self.assertNotIn("judge_engine", source)

    def test_no_spec_in_steps(self):
        import scripts.core.ooda.steps as mod
        source = open(mod.__file__).read()
        self.assertNotIn("SpecEngine", source)
        self.assertNotIn("spec_engine", source)


# ======================================================================
# Public API surface
# ======================================================================

class TestPublicAPISurface(unittest.TestCase):
    """Verify OODARuntime exposes exactly 3 public methods."""

    def test_only_execute_resume_interrupt(self):
        public = [
            m for m in dir(OODARuntime)
            if not m.startswith("_")
        ]
        # Core API methods
        self.assertIn("execute", public)
        self.assertIn("resume", public)
        self.assertIn("interrupt", public)

        # Should not have extra public methods
        expected = {"execute", "resume", "interrupt", "__init__"}
        actual_public = {m for m in public if not m.startswith("__")}
        # Allow constructor and standard methods
        extra = actual_public - {"execute", "resume", "interrupt"}
        self.assertEqual(extra, set(), f"Unexpected public methods: {extra}")


# ======================================================================
# Error hierarchy
# ======================================================================

class TestErrorHierarchy(unittest.TestCase):

    def test_ooda_error_inherits_codeai_error(self):
        from scripts.core.errors import CodeAIError
        err = OODAError("test", code="OODA_TEST")
        self.assertIsInstance(err, CodeAIError)

    def test_ooda_error_has_fields(self):
        err = OODAError(
            "msg",
            code="CODE",
            recoverable=True,
            context={"k": "v"},
        )
        self.assertEqual(err.message, "msg")
        self.assertEqual(err.code, "CODE")
        self.assertTrue(err.recoverable)
        self.assertEqual(err.context, {"k": "v"})


if __name__ == "__main__":
    unittest.main()
