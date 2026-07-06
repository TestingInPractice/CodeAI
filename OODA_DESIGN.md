# OODA_DESIGN.md — OODA Agent Integration Design

## 1. Current Architecture Analysis

CodeAI's build-loop pipeline:

```
decompose.sh → phases.json → build-loop.sh → run-loop.sh → run-task.sh → Judge
```

The execution layer (`run-task.sh`) currently works as:

```
run-task.sh --step analyst --print-prompt
  → outputs prompt text
  → user copies to task() call
  → LLM writes /tmp/p{id}-analyst-summary.txt
  → run-task.sh --step analyst --judge --summary /tmp/p{id}-analyst-summary.txt

run-task.sh --step dev --print-prompt
  → same flow
```

**Problem**: Each step is a single large LLM call with full spec context. No context isolation between search, analysis, planning, and implementation. No tool-level permission boundaries.

**State management** (not changing):
- `phases.json` — phase list with status, judge_passed
- `.workflow/state.json` — workflow state machine
- Judge flags (`judge_passed`) set only by tester step

---

## 2. Integration Points

Where OODA agents enter:

| Current step | OODA mapping | Where |
|-------------|--------------|-------|
| `--step analyst` | `@observe` → `@orient` → Judge | New `--run` mode in `run-task.sh` |
| `--step dev` | `@decide` → validate plan → `@act` → Judge | New `--run` mode in `run-task.sh` |
| `--step tester` | unchanged (future: @act test mode) | Current flow preserved |

All other pipeline components remain untouched:
- `build-loop.sh` — orchestrator, unchanged
- `run-loop.sh` — phase status manager, unchanged
- `decompose.sh` — phase decomposer, unchanged
- `phases.json` — data format, unchanged
- `state.json` — workflow state, unchanged
- `llm-judge.py` — evaluator, unchanged
- `judge-rubrics/` — criteria, unchanged

---

## 3. Files That Will Change

| File | Action | Reason |
|------|--------|--------|
| `~/.config/opencode/agents/observe.md` | Create | New subagent definition |
| `~/.config/opencode/agents/orient.md` | Create | New subagent definition |
| `~/.config/opencode/agents/decide.md` | Create | New subagent definition |
| `~/.config/opencode/agents/act.md` | Create | New subagent definition |
| `scripts/workflow/run-task.sh` | Modify | Add `--run` mode, change artifact paths |
| `AGENTS.md` | Modify | Add OODA section, update task cycle |

---

## 4. Build Loop Preservation Proof

Every shell script in the pipeline:

```
build-loop.sh:
  └── calls run-loop.sh, decompose.sh
  └── no reference to task() or agent invocation
  └→ UNCHANGED ✓

run-loop.sh:
  └── manages phases.json status (pending→in_progress→completed)
  └── calls run-task.sh for execution
  └── has its own --judge mode (separate from run-task.sh --judge)
  └→ UNCHANGED ✓

decompose.sh:
  └── reads goals.md → generates phases.json
  └── no reference to execution model
  └→ UNCHANGED ✓

phases.json:
  └── phase list with {id, name, status, depends_on, acceptance_criteria, judge_passed}
  └→ UNCHANGED ✓

state.json:
  └── workflow state machine (setup→spec→...→complete)
  └→ UNCHANGED ✓

llm-judge.py:
  └── API: --question, --response, --context, --phase-id, --phases-path
  └→ UNCHANGED ✓

run-task.sh:
  └── ONLY this file changes
  └── adds `--run` mode alongside existing `--print-prompt`, `--judge`, `--complete`
  └── `--print-prompt` kept (deprecated) for backward compat
  └→ CHANGES: +new mode, +new paths ✓
```

---

## 5. New Execution Flow (run-task.sh --run)

### `--step analyst`

```
run-task.sh --phase p1 --step analyst --run
  │
  ├── 1. mkdir -p .opencode/tasks/phase-p1/
  │
  ├── 2. opencode run --agent observe --auto --dir $PROJECT
  │       "Spec: ... AC: ... Find relevant files, record facts"
  │     → .opencode/tasks/phase-p1/observe-summary.md
  │
  ├── 3. opencode run --agent orient --auto --dir $PROJECT
  │       "Read observe-summary, analyze architecture, design"
  │     → .opencode/tasks/phase-p1/architecture.md
  │
  └── 4. JUDGE
        llm-judge.py --question "Phase p1 (Analyst)"
          --response .opencode/tasks/phase-p1/architecture.md
          --context "$spec"
```

### `--step dev`

```
run-task.sh --phase p1 --step dev --run
  │
  ├── 1. opencode run --agent decide --auto --dir $PROJECT
  │       "Read architecture.md, write plan.md"
  │     → .opencode/tasks/phase-p1/plan.md
  │
  ├── 2. Validate plan structure
  │       grep "^## Files" plan.md
  │       grep "^## Changes" plan.md
  │       grep "^## Risks" plan.md
  │       grep "^## Tests" plan.md
  │       grep "^## Rollback" plan.md
  │
  ├── 3. opencode run --agent act --auto --dir $PROJECT
  │       "Read plan.md, implement step by step"
  │     → code changes + .opencode/tasks/phase-p1/dev-summary.md
  │
  └── 4. JUDGE
        llm-judge.py --question "Phase p1 (Dev)"
          --response .opencode/tasks/phase-p1/dev-summary.md
          --context "$spec + observe + orient + plan"
```

### `--step tester`

Unchanged. Current flow remains:
```
run-task.sh --step tester --print-prompt → task() → judge
```

---

## 6. Artifact Layout

```
/tmp/p{id}-{step}-summary.txt                    ← OLD (removed)
.opencode/tasks/phase-{id}/
├── observe-summary.md     ← from @observe
├── architecture.md        ← from @orient (judge target for analyst)
├── plan.md                ← from @decide
└── dev-summary.md         ← from @act (judge target for dev)
```

---

## 7. Risks & Rollback

| Risk | Likelihood | Mitigation | Rollback |
|------|-----------|------------|----------|
| `opencode run --agent` not available | Low | `which opencode` check with error message | Keep `--print-prompt` mode |
| Agent ignores plan permission | Medium | Prompt: MUST follow plan, STOP if impossible | Re-run with corrected prompt |
| Judge reads from wrong path | Low | Default path = `.opencode/tasks/phase-{id}/`, fallback to `--summary` flag | Explicit `--summary /tmp/...` |
| Agent observe finds too many files | Medium | Prompt limits to 15 files; orient uses only observe-summary | Tweak prompt |
| Backward compat broken | Low | `--print-prompt` preserved, same output format | Use `--print-prompt` |

**Rollback plan**: revert run-task.sh changes, delete agent files, revert AGENTS.md. The old `--print-prompt` mode is never removed — full rollback is just using old workflow.

---

## 8. Principle

If during implementation it becomes clear that the proposed OODA architecture is worse than the existing single-call approach — the change should NOT be implemented. The existing pipeline works and is battle-tested. OODA integration is only beneficial if it demonstrably improves context isolation and execution quality without breaking reliability.
