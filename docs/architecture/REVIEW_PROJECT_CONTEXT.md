# REVIEW_PROJECT_CONTEXT.md — ProjectContext & RuntimeContext Audit

**Date:** 2026-07-11  
**Result:** PASS (after fix)

---

## 1. Current State

### ProjectContext (6 fields)

| Field | Type | Source | Status |
|-------|------|--------|--------|
| `spec` | `StructuredSpec` | Spec Engine | ✅ correct |
| `workflow` | `WorkflowState` | Workflow Engine | ✅ correct |
| `memory` | `list[MemoryEntry]` | Memory Layer | ✅ correct |
| `knowledge` | `list[Knowledge]` | Knowledge Layer | ✅ correct |
| `runtime` | `RuntimeContext \| None` | Runtime | ⚠️ had duplication |
| `verdict` | `Verdict \| None` | Judge Engine | ✅ correct |

### RuntimeContext (before fix — 9 fields)

| Field | Type | Purpose | Status |
|-------|------|---------|--------|
| `project_root` | `Path` | Project environment | ✅ |
| `branch` | `str` | Git branch | ✅ |
| `current_phase` | `str` | Workflow tracking | ❌ DUPLICATE |
| `current_task` | `UUID \| None` | Workflow tracking | ❌ DUPLICATE |
| `iteration` | `int` | Execution metadata | ✅ |
| `variables` | `dict[str, Any]` | Runtime variables | ✅ |
| `current_agent` | `str` | OODA tracing | ✅ |
| `current_role` | `str` | OODA tracing | ✅ |
| `session_id` | `UUID \| None` | OODA tracing | ✅ |

---

## 2. Issues Found

### Issue 1: `current_phase` and `current_task` duplication

**Problem:** `RuntimeContext.current_phase` and `RuntimeContext.current_task` duplicate data that already lives in `WorkflowState`:

```
WorkflowState.current_phase  ↔  RuntimeContext.current_phase
WorkflowState.current_task   ↔  RuntimeContext.current_task
```

**Two sources of truth** — risk of desynchronization. When WorkflowEngine advances a phase, it updates `WorkflowState`. If it also needs to update `RuntimeContext`, that's two writes. If it forgets, the contexts diverge.

**Fix:** Remove `current_phase` and `current_task` from `RuntimeContext`. Consumers use `WorkflowState` for workflow state.

### Issue 2: Split RuntimeContext vs ExecutionContext?

**Question:** Should `RuntimeContext` be split into:
- `RuntimeContext` — project environment (project_root, branch)
- `ExecutionContext` — OODA tracing (current_agent, current_role, session_id, iteration)

**Decision: NO split.**

**Reasons:**
1. All fields in `RuntimeContext` describe "current execution environment" — they're tightly coupled
2. OODA tracing fields (`current_agent`, `current_role`, `session_id`) are inherently runtime concerns
3. Splitting creates two small classes that always travel together —增加了 complexity without benefit
4. `iteration` and `variables` bridge both concerns — which class owns them?

**Keep `RuntimeContext` as a single class.** If a future need arises (e.g., serializing OODA tracing separately), refactor then.

---

## 3. What RuntimeContext Now Tracks

After removing duplicates, `RuntimeContext` has 7 fields in 3 groups:

| Group | Fields | Purpose |
|-------|--------|---------|
| **Environment** | `project_root`, `branch` | Where are we running? |
| **Execution** | `iteration`, `variables` | What iteration? What state? |
| **OODA Tracing** | `current_agent`, `current_role`, `session_id` | Who is doing what? |

**Workflow state** lives exclusively in `WorkflowState`:

```
ProjectContext
├── spec: StructuredSpec          ← Spec Engine
├── workflow: WorkflowState       ← Workflow Engine (current_phase, phases, current_task)
├── memory: list[MemoryEntry]     ← Memory Layer
├── knowledge: list[Knowledge]    ← Knowledge Layer
├── runtime: RuntimeContext       ← Environment + OODA tracing
└── verdict: Verdict | None       ← Judge Engine
```

---

## 4. Completeness Check

### What each subsystem needs from ProjectContext

| Subsystem | Reads | Writes |
|-----------|-------|--------|
| Spec Engine | `spec` | `spec` |
| Workflow Engine | `workflow`, `verdict` | `workflow` |
| OODA Runtime | `runtime`, `spec`, `workflow`, `knowledge` | `runtime` |
| Knowledge Layer | `spec` | `knowledge` |
| Memory Layer | — | `memory` |
| Judge Engine | `spec`, `workflow`, `knowledge`, `memory` | `verdict` |

### What's NOT in ProjectContext (and shouldn't be)

| Absent | Why |
|--------|-----|
| Raw goals.md text | `StructuredSpec` is the parsed form |
| File system paths | `RuntimeContext.project_root` + relative paths |
| Agent prompts | Generated at runtime, not stored in context |
| Test results | Ephemeral, belong in OODA outputs |
| Git history | External to runtime |

---

## 5. Changes Made

### `scripts/core/types/common.py`

```diff
  @dataclass
  class RuntimeContext:
-     """Runtime context for current execution."""
+     """Runtime context for current execution.
+
+     Tracks project environment and OODA agent tracing.
+     Workflow state (current_phase, current_task) lives in WorkflowState.
+     """
      project_root: Path
      branch: str = ""
-     current_phase: str = ""
-     current_task: UUID | None = None
      iteration: int = 0
      variables: dict[str, Any] = field(default_factory=dict)
      current_agent: str = ""
      current_role: str = ""
      session_id: UUID | None = None
```

**Removed:** `current_phase`, `current_task`  
**Added:** Docstring explaining separation of concerns

---

## 6. Verdict

| Check | Result |
|-------|--------|
| Missing data? | No — all 6 subsystems have their data |
| Redundant fields? | Fixed — removed `current_phase`/`current_task` from RuntimeContext |
| RuntimeContext sufficient? | Yes — 7 fields, 3 logical groups |
| Split needed? | No — single class is cleaner |
| compileall | PASS |
