"""Unit tests for WorkflowEngine state machine.

Tests use ONLY public API from CORE_RUNTIME.md:
- start(phase)
- next()
- complete(phase, judge_passed)
- rollback(phase, reason)
"""

import unittest

from scripts.core.enums import PhaseStatus, TaskStatus
from scripts.core.errors import WorkflowError
from scripts.core.workflow.state import PhaseState, TaskState, WorkflowState
from scripts.core.workflow_engine import WorkflowEngine


def make_phase(phase_id: str, tasks: int = 0, deps: list[str] | None = None) -> PhaseState:
    """Create a PhaseState with optional tasks and dependencies."""
    phase = PhaseState(id=phase_id, title=f"Phase {phase_id}", depends_on=deps or [])
    for i in range(tasks):
        phase.tasks.append(TaskState(uuid=f"{phase_id}-T{i+1}", title=f"{phase_id}-T{i+1}"))
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


if __name__ == "__main__":
    unittest.main()
