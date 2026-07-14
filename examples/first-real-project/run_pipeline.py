#!/usr/bin/env python3
"""Run CodeAI Pipeline on the First Real Project.

This script runs the full CodeAI pipeline and documents every issue found.
"""

import sys
import json
import traceback
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.core.pipeline import EndToEndPipeline, PipelineResult
from scripts.core.spec_engine import SpecEngine
from scripts.core.workflow_engine import WorkflowEngine
from scripts.core.ooda_runtime import OODARuntime
from scripts.core.knowledge_layer import KnowledgeLayer
from scripts.core.memory_layer import MemoryLayer
from scripts.core.judge_engine import JudgeEngine
from scripts.core.event_bus import EventBus
from scripts.core.errors import CodeAIError
from scripts.core.workflow.state import WorkflowState

PROMPT = (
    "Create a REST API application for task management using Python, FastAPI, and SQLite. "
    "The API should support CRUD operations on tasks with fields: title, description, status, priority. "
    "Include endpoints for listing tasks with status filtering, task statistics, "
    "proper error handling with HTTP status codes, input validation, and database initialization on startup."
)

findings = {
    "working": [],
    "broken": [],
    "fake_stub": [],
    "observations": [],
    "problems": [],
}


def log(category, title, detail):
    findings[category].append({"title": title, "detail": detail})
    print(f"  [{category.upper()}] {title}: {detail}")


def run_pipeline():
    print("=" * 70)
    print("CodeAI — First Real Project Pipeline Run")
    print("=" * 70)
    print(f"\nPrompt: {PROMPT[:100]}...\n")

    pipeline = EndToEndPipeline()

    # ── Test 1: SpecEngine.generate() ────────────────────────
    print("\n── Step 1: SpecEngine.generate() ──")
    try:
        goals_path = pipeline.spec_engine.generate(PROMPT)
        print(f"  goals_path = {goals_path}")
        print(f"  exists = {goals_path.exists()}")
        if goals_path.exists():
            content = goals_path.read_text()
            print(f"  size = {len(content)} bytes")
            print(f"  first 500 chars:\n{content[:500]}")
            log("working", "SpecEngine.generate()", f"Created {goals_path} ({len(content)} bytes)")
        else:
            log("broken", "SpecEngine.generate()", "Returned path that does not exist")
    except Exception as e:
        log("broken", "SpecEngine.generate()", f"Exception: {e}")
        traceback.print_exc()
        return

    # ── Test 2: SpecEngine.validate() ────────────────────────
    print("\n── Step 2: SpecEngine.validate() ──")
    try:
        validation = pipeline.spec_engine.validate(goals_path)
        print(f"  valid = {validation.valid}")
        print(f"  errors = {validation.errors}")
        print(f"  warnings = {validation.warnings}")
        if validation.valid:
            log("working", "SpecEngine.validate()", "Spec validated successfully")
        else:
            log("broken", "SpecEngine.validate()", f"Validation failed: {validation.errors}")
    except Exception as e:
        log("broken", "SpecEngine.validate()", f"Exception: {e}")
        traceback.print_exc()
        return

    # ── Test 3: SpecEngine.approve() ────────────────────────
    print("\n── Step 3: SpecEngine.approve() ──")
    try:
        pipeline.spec_engine.approve(goals_path)
        log("fake_stub", "SpecEngine.approve()", "No-op auto-approve, no human gate")
    except Exception as e:
        log("broken", "SpecEngine.approve()", f"Exception: {e}")

    # ── Test 4: SpecEngine.parse() ────────────────────────
    print("\n── Step 4: SpecEngine.parse() ──")
    try:
        spec = pipeline.spec_engine.parse(goals_path)
        print(f"  requirements = {len(spec.requirements)}")
        print(f"  acceptance_criteria = {len(spec.acceptance_criteria)}")
        print(f"  data_models = {len(spec.data_models)}")
        print(f"  api_contracts = {len(spec.api_contracts)}")
        print(f"  scope.included = {spec.scope.included}")
        for i, req in enumerate(spec.requirements):
            print(f"    req[{i}]: {req.title} (priority={req.priority.value})")
        for i, ac in enumerate(spec.acceptance_criteria):
            print(f"    ac[{i}]: {ac.description[:80]}")
        log("working", "SpecEngine.parse()", f"Parsed {len(spec.requirements)} requirements, {len(spec.acceptance_criteria)} ACs")
    except Exception as e:
        log("broken", "SpecEngine.parse()", f"Exception: {e}")
        traceback.print_exc()
        return

    # ── Test 5: WorkflowEngine phase creation ────────────────
    print("\n── Step 5: WorkflowEngine setup ──")
    try:
        from uuid import uuid4
        from scripts.core.workflow.state import PhaseState, TaskState

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

        state = WorkflowState(phases=phases)
        workflow = WorkflowEngine(state)
        print(f"  phases created = {len(phases)}")
        for p in phases:
            print(f"    {p.id}: {p.title} (tasks={len(p.tasks)}, deps={p.depends_on})")
        log("working", "WorkflowEngine setup", f"{len(phases)} phases created from spec")
    except Exception as e:
        log("broken", "WorkflowEngine setup", f"Exception: {e}")
        traceback.print_exc()
        return

    # ── Test 6: WorkflowEngine transitions ────────────────────
    print("\n── Step 6: WorkflowEngine transitions ──")
    transition_log = []
    try:
        for phase in phases:
            try:
                workflow.start(phase.id)
                transition_log.append(f"start({phase.id}) -> OK")
                print(f"  start({phase.id}) -> OK")
            except Exception as e:
                transition_log.append(f"start({phase.id}) -> ERROR: {e}")
                print(f"  start({phase.id}) -> ERROR: {e}")

            try:
                task_state = phase.tasks[0]
                task_state.status = "completed"  # simulate completion
                workflow.complete(phase.id, judge_passed=True)
                transition_log.append(f"complete({phase.id}) -> OK")
                print(f"  complete({phase.id}) -> OK")
            except Exception as e:
                transition_log.append(f"complete({phase.id}) -> ERROR: {e}")
                print(f"  complete({phase.id}) -> ERROR: {e}")

        log("working", "WorkflowEngine transitions", f"{len(transition_log)} transitions executed")
    except Exception as e:
        log("broken", "WorkflowEngine transitions", f"Exception: {e}")
        traceback.print_exc()

    # ── Test 7: Full Pipeline Execution ──────────────────────
    print("\n── Step 7: Full Pipeline Execution ──")
    try:
        result = pipeline.run(PROMPT)
        print(f"  workflow_status = {result.workflow_status}")
        print(f"  phases_completed = {result.phases_completed}")
        print(f"  phases_failed = {result.phases_failed}")
        print(f"  ooda_results = {len(result.ooda_results)}")
        print(f"  judge_verdicts = {len(result.judge_verdicts)}")
        print(f"  events = {len(result.events)}")
        print(f"  artifacts = {len(result.artifacts)}")
        print(f"  errors = {len(result.errors)}")

        for jv in result.judge_verdicts:
            print(f"    judge: {jv['phase']} -> {jv['overall']} (confidence={jv['confidence']:.2f})")

        for err in result.errors:
            print(f"    error: {err['phase']}: {err['error']} ({err['code']})")

        if result.errors:
            log("broken", "Full pipeline", f"{len(result.errors)} errors occurred")
        elif result.phases_failed:
            log("broken", "Full pipeline", f"{len(result.phases_failed)} phases failed judge")
        else:
            log("working", "Full pipeline", f"All {len(result.phases_completed)} phases completed")

    except Exception as e:
        log("broken", "Full pipeline", f"Exception: {e}")
        traceback.print_exc()

    # ── Test 8: OODA step details ────────────────────────────
    print("\n── Step 8: OODA Results Detail ──")
    for i, ooda_r in enumerate(result.ooda_results):
        print(f"  [{i}] success={ooda_r.success}, step={ooda_r.step}")
        print(f"      summary_preview={ooda_r.summary[:200]}")
        print(f"      outputs={len(ooda_r.outputs)}")
        for out in ooda_r.outputs:
            print(f"        -> {out.name} ({out.type})")

        # Check if ActStep was a stub
        if "v1 stub" in ooda_r.summary.lower():
            log("fake_stub", f"OODA phase {i+1} ActStep", "Produced v1 stub, not real execution")
        elif ooda_r.success:
            log("working", f"OODA phase {i+1}", "Completed successfully")

    # ── Test 9: Knowledge usage ──────────────────────────────
    print("\n── Step 9: Knowledge Layer ──")
    try:
        knowledge = pipeline.knowledge.search("task management")
        print(f"  knowledge items found = {len(knowledge)}")
        for k in knowledge[:5]:
            print(f"    [{k.kind.value}] {k.source}: {k.content[:80]}")

        if knowledge:
            log("working", "Knowledge search", f"Found {len(knowledge)} items")
        else:
            log("broken", "Knowledge search", "No items found")
    except Exception as e:
        log("broken", "Knowledge search", f"Exception: {e}")

    # ── Test 10: Memory usage ────────────────────────────────
    print("\n── Step 10: Memory Layer ──")
    try:
        memory = pipeline.memory.load("task", scope="project")
        print(f"  memory entries found = {len(memory)}")
        for m in memory[:5]:
            print(f"    [{m.type.value}] {m.content[:80]}")

        if memory:
            log("working", "Memory load", f"Found {len(memory)} entries")
        else:
            log("broken", "Memory load", "No entries found")
    except Exception as e:
        log("broken", "Memory load", f"Exception: {e}")

    # ── Test 11: Judge verdicts impact ───────────────────────
    print("\n── Step 11: Judge System ──")
    if result.judge_verdicts:
        all_passed = all(jv["overall"] in ("PASS", "PASS_WITH_CONCERNS") for jv in result.judge_verdicts)
        print(f"  all passed = {all_passed}")
        for jv in result.judge_verdicts:
            print(f"    {jv['phase']}: {jv['overall']} -> route={jv['route']}")
        log("working" if all_passed else "broken", "Judge system",
            f"{'All phases passed' if all_passed else 'Some phases failed'}")
    else:
        log("broken", "Judge system", "No verdicts produced")

    # ── Test 12: Events published ────────────────────────────
    print("\n── Step 12: Event Bus ──")
    if result.events:
        event_counts = {}
        for evt in result.events:
            event_counts[evt] = event_counts.get(evt, 0) + 1
        for evt, count in sorted(event_counts.items()):
            print(f"    {evt}: {count}x")
        log("working", "Event Bus", f"{len(result.events)} events published across {len(event_counts)} types")
    else:
        log("broken", "Event Bus", "No events published")

    # ── Test 13: Artifact creation ───────────────────────────
    print("\n── Step 13: Artifacts ──")
    if result.artifacts:
        for art in result.artifacts:
            exists = art.path.exists()
            print(f"    {art.name} ({art.type}) exists={exists}")
            if not exists:
                log("broken", f"Artifact {art.name}", f"File does not exist at {art.path}")
        log("working", "Artifacts", f"{len(result.artifacts)} artifacts declared")
    else:
        log("broken", "Artifacts", "No artifacts produced")

    # ── Test 14: state.json persistence ──────────────────────
    print("\n── Step 14: State Persistence ──")
    state_json = Path(".workflow/state.json")
    if state_json.exists():
        print(f"  state.json exists at {state_json}")
        log("working", "State persistence", "state.json found")
    else:
        print(f"  state.json NOT found at {state_json}")
        log("broken", "State persistence", "state.json does not exist — pipeline does not persist state")

    # ── Summary ──────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"\nWorking:    {len(findings['working'])}")
    print(f"Broken:     {len(findings['broken'])}")
    print(f"Fake/Stub:  {len(findings['fake_stub'])}")
    print(f"Observations: {len(findings['observations'])}")

    return result


if __name__ == "__main__":
    result = run_pipeline()

    # Write findings to JSON
    output = Path(__file__).parent.parent.parent / "docs" / "first-real-project-findings.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w") as f:
        json.dump(findings, f, indent=2, default=str)
    print(f"\nFindings written to {output}")
