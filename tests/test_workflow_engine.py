"""Unit tests for WorkflowEngine state machine.

Tests use ONLY public API from CORE_RUNTIME.md:
- start(phase)
- next()
- complete(phase, judge_passed)
- rollback(phase, reason)
"""

import unittest
from uuid import UUID

from scripts.core.enums import PhaseStatus, TaskStatus
from scripts.core.errors import WorkflowError
from scripts.core.workflow.state import PhaseState, TaskState, WorkflowState
from scripts.core.workflow_engine import WorkflowEngine


def make_phase(phase_id: str, tasks: int = 0, deps: list[str] | None = None) -> PhaseState:
    """Create a PhaseState with optional tasks and dependencies."""
    phase = PhaseState(id=phase_id, title=f"Phase {phase_id}", depends_on=deps or [])
    for i in range(tasks):
        phase.tasks.append(TaskState(uuid=UUID(f"00000000-0000-0000-0000-{i+1:012d}"), title=f"{phase_id}-T{i+1}"))
    return phase


def make_engine(phases: list[PhaseState] | None = None) -> WorkflowEngine:
    """Create a WorkflowEngine (in-memory only)."""
    state = WorkflowState(phases=phases or [])
    return WorkflowEngine(state=state)


def complete_all_tasks(phase: PhaseState) -> None:
    """Mark all tasks in a phase as COMPLETED (for testing complete())."""
    for t in phase.tasks:
        t.status = TaskStatus.COMPLETED


# ── start() ──────────────────────────────────────────────────────

class TestStart(unittest.TestCase):
    def test_start_pending_phase(self):
        p1 = make_phase("p1")
        engine = make_engine([p1])
        engine.start("p1")
        self.assertEqual(p1.status, PhaseStatus.IN_PROGRESS)

    def test_start_twice_fails(self):
        p1, p2 = make_phase("p1"), make_phase("p2")
        engine = make_engine([p1, p2])
        engine.start("p1")
        with self.assertRaises(WorkflowError) as ctx:
            engine.start("p2")
        self.assertEqual(ctx.exception.code, "WF_PHASE_ACTIVE")

    def test_start_nonexistent_fails(self):
        engine = make_engine([])
        with self.assertRaises(WorkflowError) as ctx:
            engine.start("nope")
        self.assertEqual(ctx.exception.code, "WF_PHASE_NOT_FOUND")

    def test_start_completed_fails(self):
        p1 = make_phase("p1")
        p1.status = PhaseStatus.COMPLETED
        engine = make_engine([p1])
        with self.assertRaises(WorkflowError) as ctx:
            engine.start("p1")
        self.assertEqual(ctx.exception.code, "WF_PHASE_WRONG_STATUS")

    def test_start_with_unmet_deps_fails(self):
        p1, p2 = make_phase("p1"), make_phase("p2", deps=["p1"])
        engine = make_engine([p1, p2])
        with self.assertRaises(WorkflowError) as ctx:
            engine.start("p2")
        self.assertEqual(ctx.exception.code, "WF_DEP_NOT_COMPLETED")

    def test_start_with_met_deps(self):
        p1 = make_phase("p1")
        p1.status = PhaseStatus.COMPLETED
        p2 = make_phase("p2", deps=["p1"])
        engine = make_engine([p1, p2])
        engine.start("p2")
        self.assertEqual(p2.status, PhaseStatus.IN_PROGRESS)

    def test_start_with_missing_dep_fails(self):
        p1 = make_phase("p1", deps=["ghost"])
        engine = make_engine([p1])
        with self.assertRaises(WorkflowError) as ctx:
            engine.start("p1")
        self.assertEqual(ctx.exception.code, "WF_DEP_NOT_FOUND")


# ── next() ──────────────────────────────────────────────────────

class TestNext(unittest.TestCase):
    def test_returns_first_pending(self):
        p1, p2 = make_phase("p1"), make_phase("p2")
        engine = make_engine([p1, p2])
        self.assertIs(engine.next(), p1)

    def test_returns_none_when_active(self):
        p1, p2 = make_phase("p1"), make_phase("p2")
        engine = make_engine([p1, p2])
        engine.start("p1")
        self.assertIsNone(engine.next())

    def test_skips_completed(self):
        p1 = make_phase("p1")
        p1.status = PhaseStatus.COMPLETED
        p2 = make_phase("p2")
        engine = make_engine([p1, p2])
        self.assertIs(engine.next(), p2)

    def test_respects_deps(self):
        p1, p2 = make_phase("p1"), make_phase("p2", deps=["p1"])
        engine = make_engine([p1, p2])
        self.assertIs(engine.next(), p1)

    def test_returns_none_when_all_done(self):
        p1 = make_phase("p1")
        p1.status = PhaseStatus.COMPLETED
        engine = make_engine([p1])
        self.assertIsNone(engine.next())

    def test_empty_phases(self):
        engine = make_engine([])
        self.assertIsNone(engine.next())


# ── complete() ──────────────────────────────────────────────────

class TestComplete(unittest.TestCase):
    def test_complete_all_tasks_done(self):
        p = make_phase("p1", tasks=2)
        engine = make_engine([p])
        engine.start("p1")
        complete_all_tasks(p)
        engine.complete("p1", judge_passed=True)
        self.assertEqual(p.status, PhaseStatus.COMPLETED)
        self.assertTrue(p.judge_passed)

    def test_incomplete_tasks_fails(self):
        p = make_phase("p1", tasks=2)
        engine = make_engine([p])
        engine.start("p1")
        p.tasks[0].status = TaskStatus.COMPLETED
        with self.assertRaises(WorkflowError) as ctx:
            engine.complete("p1", judge_passed=True)
        self.assertEqual(ctx.exception.code, "WF_TASKS_INCOMPLETE")

    def test_judge_not_passed_fails(self):
        p = make_phase("p1", tasks=1)
        engine = make_engine([p])
        engine.start("p1")
        complete_all_tasks(p)
        with self.assertRaises(WorkflowError) as ctx:
            engine.complete("p1", judge_passed=False)
        self.assertEqual(ctx.exception.code, "WF_JUDGE_FAILED")

    def test_wrong_status_fails(self):
        p = make_phase("p1")
        engine = make_engine([p])
        with self.assertRaises(WorkflowError) as ctx:
            engine.complete("p1", judge_passed=True)
        self.assertEqual(ctx.exception.code, "WF_PHASE_WRONG_STATUS")

    def test_not_found_fails(self):
        engine = make_engine([])
        with self.assertRaises(WorkflowError) as ctx:
            engine.complete("x", judge_passed=True)
        self.assertEqual(ctx.exception.code, "WF_PHASE_NOT_FOUND")

    def test_all_phases_done(self):
        """When all phases completed, next() returns None."""
        p = make_phase("p1", tasks=1)
        engine = make_engine([p])
        engine.start("p1")
        complete_all_tasks(p)
        engine.complete("p1", judge_passed=True)
        self.assertIsNone(engine.next())


# ── rollback() ───────────────────────────────────────────────────

class TestRollback(unittest.TestCase):
    def test_rollback_in_progress(self):
        p1 = make_phase("p1", tasks=2)
        engine = make_engine([p1])
        engine.start("p1")
        engine.rollback("p1", reason="Judge FAIL")
        self.assertEqual(p1.status, PhaseStatus.PENDING)
        self.assertFalse(p1.judge_passed)
        self.assertTrue(all(t.status == TaskStatus.PENDING for t in p1.tasks))

    def test_rollback_failed_phase(self):
        p1 = make_phase("p1")
        p1.status = PhaseStatus.FAILED
        engine = make_engine([p1])
        engine.rollback("p1", reason="retry")
        self.assertEqual(p1.status, PhaseStatus.PENDING)

    def test_rollback_pending_fails(self):
        p1 = make_phase("p1")
        engine = make_engine([p1])
        with self.assertRaises(WorkflowError) as ctx:
            engine.rollback("p1", reason="x")
        self.assertEqual(ctx.exception.code, "WF_PHASE_WRONG_STATUS")

    def test_rollback_completed_fails(self):
        p1 = make_phase("p1")
        p1.status = PhaseStatus.COMPLETED
        engine = make_engine([p1])
        with self.assertRaises(WorkflowError) as ctx:
            engine.rollback("p1", reason="x")
        self.assertEqual(ctx.exception.code, "WF_PHASE_WRONG_STATUS")

    def test_rollback_not_found_fails(self):
        engine = make_engine([])
        with self.assertRaises(WorkflowError) as ctx:
            engine.rollback("x", reason="x")
        self.assertEqual(ctx.exception.code, "WF_PHASE_NOT_FOUND")

    def test_multiple_rollbacks(self):
        """Phase can be rolled back multiple times."""
        p1 = make_phase("p1")
        engine = make_engine([p1])
        engine.start("p1")
        engine.rollback("p1", reason="first")
        self.assertEqual(p1.status, PhaseStatus.PENDING)
        engine.start("p1")
        engine.rollback("p1", reason="second")
        self.assertEqual(p1.status, PhaseStatus.PENDING)


# ── Full Lifecycle ────────────────────────────────────────────────

class TestLifecycle(unittest.TestCase):
    def test_complete_lifecycle(self):
        p1 = make_phase("p1", tasks=2)
        p2 = make_phase("p2", tasks=1, deps=["p1"])
        engine = make_engine([p1, p2])

        self.assertIs(engine.next(), p1)
        engine.start("p1")
        complete_all_tasks(p1)
        engine.complete("p1", judge_passed=True)
        self.assertEqual(p1.status, PhaseStatus.COMPLETED)

        self.assertIs(engine.next(), p2)
        engine.start("p2")
        complete_all_tasks(p2)
        engine.complete("p2", judge_passed=True)
        self.assertEqual(p2.status, PhaseStatus.COMPLETED)

        self.assertIsNone(engine.next())

    def test_lifecycle_with_rollback(self):
        p1 = make_phase("p1", tasks=1)
        engine = make_engine([p1])

        engine.start("p1")
        complete_all_tasks(p1)
        engine.rollback("p1", reason="Judge FAIL")
        self.assertEqual(p1.status, PhaseStatus.PENDING)
        self.assertTrue(all(t.status == TaskStatus.PENDING for t in p1.tasks))

        engine.start("p1")
        complete_all_tasks(p1)
        engine.complete("p1", judge_passed=True)
        self.assertEqual(p1.status, PhaseStatus.COMPLETED)


class TestWorkflowStateIdentity(unittest.TestCase):
    """Regression: ensure one canonical WorkflowState class.

    Issue #23 — duplicate WorkflowState definitions.
    The canonical model lives in scripts.core.workflow.state.
    scripts.core.types.workflow must re-export the same object.
    """

    def test_types_reexports_same_class(self):
        from scripts.core.workflow.state import WorkflowState as Canonical
        from scripts.core.types.workflow import WorkflowState as Reexport
        self.assertIs(Canonical, Reexport)

    def test_types_reexports_phase_state(self):
        from scripts.core.workflow.state import PhaseState
        from scripts.core.types.workflow import PhaseState as Reexport
        self.assertIs(PhaseState, Reexport)

    def test_types_reexports_task_state(self):
        from scripts.core.workflow.state import TaskState
        from scripts.core.types.workflow import TaskState as Reexport
        self.assertIs(TaskState, Reexport)

    def test_types_reexports_judge_state(self):
        from scripts.core.workflow.state import JudgeState
        from scripts.core.types.workflow import JudgeState as Reexport
        self.assertIs(JudgeState, Reexport)

    def test_top_level_init_reexports(self):
        from scripts.core.workflow.state import WorkflowState as Canonical
        from scripts.core.types import WorkflowState as FromInit
        self.assertIs(Canonical, FromInit)


# ── INV1 / INV4 / INV5 ───────────────────────────────────────────

class TestInvariants(unittest.TestCase):
    """Tests for INV1, INV4, INV5 enforcement (Issue #27)."""

    def test_inv1_implement_without_tasks(self):
        """INV1: implement-spec-stage cannot start without tasks."""
        p = make_phase("implement-spec-stage", tasks=0)
        engine = make_engine([p])
        with self.assertRaises(WorkflowError) as ctx:
            engine.start("implement-spec-stage")
        self.assertEqual(ctx.exception.code, "WF_INV1_NO_TASKS")

    def test_inv1_implement_with_tasks(self):
        """INV1: implement-spec-stage starts when tasks exist."""
        p = make_phase("implement-spec-stage", tasks=2)
        engine = make_engine([p])
        engine.start("implement-spec-stage")
        self.assertEqual(p.status, PhaseStatus.IN_PROGRESS)

    def test_inv5_task_cycle_before_decompose(self):
        """INV5: task_cycle cannot start before decompose is completed (no deps declared)."""
        decompose = make_phase("decompose", tasks=1)
        task_cycle = make_phase("task_cycle", tasks=1)
        engine = make_engine([decompose, task_cycle])
        with self.assertRaises(WorkflowError) as ctx:
            engine.start("task_cycle")
        self.assertEqual(ctx.exception.code, "WF_INV5_DECOMPOSE_PENDING")

    def test_inv5_task_cycle_after_decompose(self):
        """INV5: task_cycle starts after decompose is completed."""
        decompose = make_phase("decompose", tasks=1)
        decompose.status = PhaseStatus.COMPLETED
        task_cycle = make_phase("task_cycle", tasks=1, deps=["decompose"])
        engine = make_engine([decompose, task_cycle])
        engine.start("task_cycle")
        self.assertEqual(task_cycle.status, PhaseStatus.IN_PROGRESS)

    def test_inv4_rollback_resets_completed_tasks(self):
        """INV4: after rollback, pending phase has no completed tasks."""
        p = make_phase("p1", tasks=2)
        engine = make_engine([p])
        engine.start("p1")
        complete_all_tasks(p)
        engine.rollback("p1", reason="retry")
        self.assertTrue(all(t.status == TaskStatus.PENDING for t in p.tasks))
        self.assertFalse(any(t.status == TaskStatus.COMPLETED for t in p.tasks))


if __name__ == "__main__":
    unittest.main()
