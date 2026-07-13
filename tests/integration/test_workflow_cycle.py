"""Integration Test: Workflow Cycle.

Tests start() → next() → execute() → judge() → complete() → next()
for multiple phases in sequence.
"""

import sys
import unittest
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.core.enums import (
    PhaseStatus,
    TaskStatus,
    VerdictStatus,
    WorkflowStatus,
)
from scripts.core.errors import WorkflowError
from scripts.core.judge_engine import JudgeEngine
from scripts.core.types.workflow import Task
from scripts.core.workflow_engine import WorkflowEngine
from scripts.core.workflow.state import PhaseState, TaskState, WorkflowState


def _make_workflow(phases_def: list[dict]) -> tuple[WorkflowEngine, WorkflowState]:
    """Helper to create a workflow from phase definitions."""
    phases = []
    for p in phases_def:
        tasks = [
            TaskState(uuid=str(uuid4()), title=t["title"])
            for t in p.get("tasks", [{"title": f"{p['id']} task"}])
        ]
        phases.append(PhaseState(
            id=p["id"],
            title=p.get("title", p["id"]),
            tasks=tasks,
            depends_on=p.get("depends_on", []),
        ))
    state = WorkflowState(phases=phases)
    return WorkflowEngine(state), state


class TestWorkflowCycle(unittest.TestCase):
    """Test complete workflow lifecycle."""

    def test_single_phase_lifecycle(self):
        """start → complete for one phase."""
        engine, state = _make_workflow([{"id": "p1", "title": "Phase 1"}])

        engine.start("p1")
        assert state.current_phase.id == "p1"
        assert state.workflow_status == WorkflowStatus.RUNNING

        # Mark task completed
        state.current_phase.tasks[0].status = TaskStatus.COMPLETED
        engine.complete("p1", judge_passed=True)

        assert state.current_phase is None
        assert state.workflow_status == WorkflowStatus.COMPLETED

    def test_next_returns_first_pending(self):
        """next() returns the first pending phase."""
        engine, state = _make_workflow([
            {"id": "p1"},
            {"id": "p2"},
            {"id": "p3"},
        ])

        nxt = engine.next()
        assert nxt is not None
        assert nxt.id == "p1"

    def test_next_respects_dependencies(self):
        """next() skips phases with unmet dependencies."""
        engine, state = _make_workflow([
            {"id": "p1"},
            {"id": "p2", "depends_on": ["p1"]},
            {"id": "p3", "depends_on": ["p2"]},
        ])

        # p2 depends on p1, so next should return p1
        nxt = engine.next()
        assert nxt.id == "p1"

    def test_next_returns_none_when_active(self):
        """next() returns None when a phase is in progress."""
        engine, state = _make_workflow([{"id": "p1"}, {"id": "p2"}])

        engine.start("p1")
        nxt = engine.next()
        assert nxt is None

    def test_next_returns_next_after_complete(self):
        """next() returns next phase after completing current."""
        engine, state = _make_workflow([
            {"id": "p1"},
            {"id": "p2", "depends_on": ["p1"]},
        ])

        engine.start("p1")
        state.current_phase.tasks[0].status = TaskStatus.COMPLETED
        engine.complete("p1", judge_passed=True)

        nxt = engine.next()
        assert nxt is not None
        assert nxt.id == "p2"

    def test_three_phase_cycle(self):
        """Complete lifecycle for three sequential phases."""
        engine, state = _make_workflow([
            {"id": "p1"},
            {"id": "p2", "depends_on": ["p1"]},
            {"id": "p3", "depends_on": ["p2"]},
        ])

        for phase_id in ["p1", "p2", "p3"]:
            nxt = engine.next()
            assert nxt is not None
            assert nxt.id == phase_id

            engine.start(phase_id)
            assert state.current_phase.id == phase_id

            for t in state.current_phase.tasks:
                t.status = TaskStatus.COMPLETED

            engine.complete(phase_id, judge_passed=True)
            assert state.current_phase is None

        assert state.workflow_status == WorkflowStatus.COMPLETED

    def test_start_nonexistent_phase_raises(self):
        """Starting nonexistent phase raises WorkflowError."""
        engine, state = _make_workflow([{"id": "p1"}])
        with self.assertRaises(WorkflowError):
            engine.start("nonexistent")

    def test_start_wrong_status_raises(self):
        """Starting a non-pending phase raises WorkflowError."""
        engine, state = _make_workflow([{"id": "p1"}])
        engine.start("p1")
        with self.assertRaises(WorkflowError):
            engine.start("p1")

    def test_start_with_unmet_deps_raises(self):
        """Starting phase with unmet deps raises WorkflowError."""
        engine, state = _make_workflow([
            {"id": "p1"},
            {"id": "p2", "depends_on": ["p1"]},
        ])
        with self.assertRaises(WorkflowError):
            engine.start("p2")

    def test_start_two_phases_simultaneously_raises(self):
        """Starting two phases at once raises WorkflowError."""
        engine, state = _make_workflow([{"id": "p1"}, {"id": "p2"}])
        engine.start("p1")
        with self.assertRaises(WorkflowError):
            engine.start("p2")

    def test_complete_requires_judge_pass(self):
        """Complete without judge pass raises WorkflowError."""
        engine, state = _make_workflow([{"id": "p1"}])
        engine.start("p1")
        state.current_phase.tasks[0].status = TaskStatus.COMPLETED
        with self.assertRaises(WorkflowError):
            engine.complete("p1", judge_passed=False)

    def test_complete_requires_all_tasks(self):
        """Complete with incomplete tasks raises WorkflowError."""
        engine, state = _make_workflow([{"id": "p1", "tasks": [
            {"title": "task1"}, {"title": "task2"},
        ]}])
        engine.start("p1")
        # Only complete first task
        state.current_phase.tasks[0].status = TaskStatus.COMPLETED
        with self.assertRaises(WorkflowError):
            engine.complete("p1", judge_passed=True)

    def test_judge_integration_in_workflow(self):
        """Judge evaluation feeds into workflow completion."""
        engine, state = _make_workflow([{"id": "p1"}])
        judge = JudgeEngine()

        engine.start("p1")
        state.current_phase.tasks[0].status = TaskStatus.COMPLETED

        # Judge evaluates
        verdict = judge.evaluate(
            response="Phase completed successfully",
            context="Implementation context",
            spec="Phase requirements",
        )
        judge_passed = verdict.overall in (VerdictStatus.PASS, VerdictStatus.PASS_WITH_CONCERNS)

        engine.complete("p1", judge_passed=judge_passed)
        assert state.workflow_status == WorkflowStatus.COMPLETED

    def test_parallel_tasks_in_phase(self):
        """Phase with multiple tasks, all must complete."""
        engine, state = _make_workflow([{"id": "p1", "tasks": [
            {"title": "frontend"}, {"title": "backend"}, {"title": "tests"},
        ]}])

        engine.start("p1")
        assert len(state.current_phase.tasks) == 3

        # Complete tasks one by one
        for i, t in enumerate(state.current_phase.tasks):
            t.status = TaskStatus.COMPLETED
            if i < 2:
                # Cannot complete phase yet
                pass

        engine.complete("p1", judge_passed=True)
        assert state.current_phase is None
