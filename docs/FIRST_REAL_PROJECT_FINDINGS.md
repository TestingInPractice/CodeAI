# FIRST REAL PROJECT — FINDINGS

**Date:** 2026-07-14
**Project:** Task Manager REST API (FastAPI + SQLite)
**Method:** Ran full CodeAI pipeline end-to-end, then tested the real app

---

## Executive Summary

CodeAI **completed the full pipeline cycle** — Spec → Workflow → OODA (x4 steps) → Judge → Event Bus — for a 2-requirement project. The pipeline did not crash. It produced verdicts, events, and artifacts.

**But it did not produce any real code.** The ActStep is a v1 stub. The "artifacts" are metadata declarations, not files on disk. The SpecEngine's generated spec has hallucinated data models and generic acceptance criteria.

The real FastAPI app in `examples/first-real-project/` works perfectly (15/15 tests pass) — but it was written by a human, not by CodeAI.

---

## 1. Working

### 1.1 Pipeline Orchestration ✅

| Component | Status | Evidence |
|-----------|--------|----------|
| `EndToEndPipeline.run()` | ✅ WORKING | Executes full Spec → Workflow → OODA → Judge cycle without crash |
| `PipelineResult` | ✅ WORKING | Returns complete result with all fields populated |
| Error handling (P0-003) | ✅ WORKING | All exceptions caught, no pipeline crash |
| EventBus data immutability (P0-004) | ✅ WORKING | Caller data not mutated |

### 1.2 SpecEngine ✅ (with quality issues)

| Component | Status | Evidence |
|-----------|--------|----------|
| `generate(prompt)` | ✅ WORKING | Creates `docs/specs/goals.md` (1,287 bytes) |
| `validate(goals_path)` | ✅ WORKING | Returns `ValidationResult(valid=True)` |
| `approve(goals_path)` | ⚠️ STUB | No-op auto-approve |
| `parse(goals_path)` | ✅ WORKING | Returns `StructuredSpec` with 2 requirements, 2 ACs, 3 data models |

### 1.3 WorkflowEngine ✅

| Component | Status | Evidence |
|-----------|--------|----------|
| `start(phase_id)` | ✅ WORKING | Transitions PENDING → IN_PROGRESS |
| `next()` | ✅ WORKING | Returns next PENDING phase |
| `complete(phase_id, judge_passed)` | ✅ WORKING | Transitions IN_PROGRESS → COMPLETED |
| `rollback(phase_id, reason)` | ✅ WORKING | Tested separately (P0-003 tests) |
| Dependency enforcement | ✅ WORKING | Phase-2 blocked until Phase-1 completes |
| Single active phase invariant | ✅ WORKING | Cannot start phase-2 while phase-1 is active |

### 1.4 OODA Runtime ✅ (but ActStep is stub)

| Component | Status | Evidence |
|-----------|--------|----------|
| `execute(task)` | ✅ WORKING | Runs full Observe → Orient → Decide → Act cycle |
| ObserveStep | ✅ WORKING | Gathers knowledge + memory context |
| OrientStep | ✅ WORKING | Analyzes context, identifies gaps |
| DecideStep | ✅ WORKING | Builds plan with files, risks, tests |
| ActStep | ⚠️ STUB | Returns placeholder artifact, no real execution |
| State tracking | ✅ WORKING | OODARuntimeState tracks step progression |

### 1.5 KnowledgeLayer ✅

| Component | Status | Evidence |
|-----------|--------|----------|
| `search(query)` | ✅ WORKING | Found 2 items for "task management" query |
| `retrieve(context_type, params)` | ✅ WORKING | Returns Context with knowledge items |
| BM25 ranking | ✅ WORKING | Results ranked by relevance |
| Cache (TTL + LRU) | ✅ WORKING | Tested in unit tests |
| `index()` / `index_all()` | ✅ WORKING | Pipeline seeds 2 items per phase |

### 1.6 MemoryLayer ✅

| Component | Status | Evidence |
|-----------|--------|----------|
| `store(entry)` | ✅ WORKING | Stores with dedup (content hash) |
| `load(query, scope)` | ✅ WORKING | Found 2 entries for "task" query |
| `summarize(scope, depth)` | ✅ WORKING | Returns template-based summary |
| Deduplication | ✅ WORKING | Same content not stored twice |
| Retention/GC | ✅ WORKING | TTL + max-count enforcement |

### 1.7 JudgeEngine ✅ (with scoring issues)

| Component | Status | Evidence |
|-----------|--------|----------|
| `evaluate(response, context, spec, ac)` | ✅ WORKING | Returns Verdict with scores |
| `score(response, rubric)` | ✅ WORKING | Weighted scoring |
| `route(verdict)` | ✅ WORKING | Routes PASS→workflow, FAIL→ooda/spec |
| AC evaluation (P0-002) | ✅ WORKING | Now receives ACs from pipeline |
| Consistency | ✅ WORKING | Both phases got PASS (confidence=0.81) |

### 1.8 EventBus ✅

| Component | Status | Evidence |
|-----------|--------|----------|
| `subscribe(event, handler)` | ✅ WORKING | Wildcard `*` subscription works |
| `publish(event, data)` | ✅ WORKING | 10 events across 6 types published |
| `unsubscribe(event, handler)` | ✅ WORKING | Tested in unit tests |
| `publish_raw(event)` | ✅ WORKING | Tested in unit tests |
| Deduplication | ✅ WORKING | Handler subscribed to both exact + wildcard fires once |
| Data immutability (P0-004) | ✅ WORKING | Caller data not mutated |

---

## 2. Broken

### Problem: Artifacts declared but not written to disk

**Problem:** OODA Runtime creates `Artifact` objects with paths like `.opencode/tasks/{uuid}/ooda-summary.md`, but **never creates the actual files**. The `ActStep` only builds summary text in memory.

**Expected:** Artifacts should be written to disk so downstream processes can use them.

**Actual:** 4 artifacts declared, 0 files exist on disk.

**Root cause:** `ActStep.execute()` creates `Artifact` metadata objects but never calls `Path.write_text()`. The `_build_summary()` method returns a string that is never saved.

**Priority:** HIGH

### Problem: State persistence missing

**Problem:** Pipeline does not save `state.json` anywhere. There is no `.workflow/` directory created.

**Expected:** After pipeline run, a `state.json` file should exist with workflow state for resumption.

**Actual:** No `state.json`, no `.workflow/` directory.

**Root cause:** `EndToEndPipeline` operates entirely in-memory. There is no serialization step at the end of `run()`.

**Priority:** HIGH

### Problem: Spec quality — hallucinated data models

**Problem:** SpecEngine generates data models named "Create", "Python", "Include" — these are prompt tokens, not real entities.

**Expected:** Data models should be `Task`, `User`, etc. — actual domain entities.

**Actual:**
```
### Create
- `id: UUID`
- `name: str`

### Python
- `id: UUID`
- `name: str`

### Include
- `id: UUID`
- `name: str`
```

**Root cause:** `_extract_entities_for_models()` uses entity extraction that picks up prompt verbs/nouns as entity names. The hardcoded `field_hints` dict maps known entities to fields, but "Create", "Python", "Include" are not in it, so they get default `["id: UUID", "name: str"]`.

**Priority:** HIGH

### Problem: Spec quality — generic acceptance criteria

**Problem:** ACs are boilerplate, not specific to the prompt.

**Expected:** ACs like "POST /tasks returns 201 with created task", "GET /tasks?status=pending returns filtered list"

**Actual:**
```
[AC-001] All requirements implemented and working
[AC-002] No regressions in existing functionality
```

**Root cause:** `_extract_acs()` falls back to hardcoded generic ACs when prompt-specific ACs cannot be detected via regex.

**Priority:** MEDIUM

### Problem: Spec quality — no API contracts detected

**Problem:** `_extract_api_contracts()` returns empty list for a prompt that explicitly mentions "REST API", "endpoints", "CRUD operations".

**Expected:** At least POST /tasks, GET /tasks, GET /tasks/{id}, PUT /tasks/{id}, DELETE /tasks/{id}

**Actual:** `_No API contracts identified from prompt._`

**Root cause:** `_extract_api_contracts()` looks for patterns like "endpoint", "route", "API for" but the regex patterns are too narrow.

**Priority:** MEDIUM

### Problem: Spec quality — truncated requirement text

**Problem:** Requirements are truncated at 60 characters, losing critical detail.

**Expected:** Full requirement text preserved.

**Actual:**
```
REQ-001: Create a REST API application for task management using Python, FastAPI, and SQL
REQ-002: The API should support CRUD operations on tasks with fields: title, description,
```

REQ-001 loses "ite" and REQ-002 loses "status, priority".

**Root cause:** `_extract_requirements()` truncates at 60 chars.

**Priority:** LOW

---

## 3. Fake / Stub

### 3.1 SpecEngine.approve() — NO-OP

```python
def approve(self, goals_path: Path) -> None:
    # v1: Auto-approves (no human gate in prototype)
    pass
```

**Impact:** Any spec, no matter how poor quality, is approved. No validation of data models, ACs, or API contracts before proceeding.

### 3.2 OODA ActStep — v1 STUB

```python
class ActStep:
    def execute(self, ctx, task):
        # Returns placeholder artifact
        summary = self._build_summary(plan, task)  # "This is a v1 stub execution."
        return [Artifact(name=..., path=..., type="summary")]
```

**Impact:** The entire code generation capability is absent. The pipeline plans but does not execute. No files are written, no code is produced.

### 3.3 Knowledge Seeding — HARDCODED

```python
def _seed_knowledge(self, task_title):
    items = [
        Knowledge(source="architecture.md", content=f"Architecture pattern for {task_title}", score=0.9),
        Knowledge(source="best-practices.md", content=f"Best practices for {task_title}", score=0.8),
    ]
```

**Impact:** Every phase gets the same 2 knowledge items with templated content. No real project documentation is ever indexed. Knowledge search always finds exactly these 2 items.

### 3.4 Memory Seeding — HARDCODED

```python
def _seed_memory(self, task_title):
    entry = MemoryEntry(type=PROJECT_HISTORY, content=f"Previously worked on {task_title}")
```

**Impact:** Memory is seeded with a single templated entry per phase. No real project history is ever stored. Memory search always returns these seeded entries.

### 3.5 OODA Resume — DEAD CODE

```python
state.status = state.status  # Reset to running state
```

**Impact:** Resuming an interrupted task does not actually reset the state. The task remains in INTERRUPTED status.

### 3.6 Judge pass_threshold — DEAD CONFIG

```python
def __init__(self, pass_threshold: float = 0.5):
    self._pass_threshold = pass_threshold  # Never used

def _overall_status(self, scores):
    avg = sum(scores.values()) / len(scores)
    if avg >= 0.7:   # Hardcoded
        return VerdictStatus.PASS
    if avg >= 0.5:   # Hardcoded
        return VerdictStatus.PASS_WITH_CONCERNS
    return VerdictStatus.FAIL
```

**Impact:** Constructor parameter is silently ignored. Thresholds are hardcoded at 0.7/0.5.

---

## 4. Subsystem Audit During Real Execution

### 4.1 Workflow Engine — FULLY WORKING

- Creates state correctly from phases
- Transitions: PENDING → IN_PROGRESS → COMPLETED
- Dependency enforcement works (phase-2 blocked by phase-1)
- Single active phase invariant enforced
- `next()` returns correct phase ordering
- Rollback tested in P0-003 (works correctly)

**Minor issue:** `ROLLING_BACK` status persists after rollback completes.

### 4.2 OODA Agents — PARTIALLY WORKING

| Step | Working? | What it does |
|------|----------|-------------|
| Observe | ✅ | Queries KnowledgeLayer + MemoryLayer, populates context |
| Orient | ✅ | Analyzes knowledge/memory, identifies gaps |
| Decide | ✅ | Builds plan with files, risks, tests |
| Act | ❌ STUB | Returns placeholder, no real execution |

**State passing between agents:** Working — each step receives `ProjectContext` and returns it modified. Observe populates `ctx.knowledge` and `ctx.memory`. Orient stores analysis in `ctx.runtime.variables["orientation"]`. Decide stores plan in `ctx.runtime.variables["plan"]`.

### 4.3 Judge System — WORKING (with caveats)

- Evaluation runs on every phase
- Scores are computed across 4 pillars (AC, relevance, faithfulness, context precision)
- Routing works: PASS → workflow, FAIL → ood/a/spec
- Verdicts are recorded in `PipelineResult.judge_verdicts`
- Events published: `judge.evaluated`

**Caveats:**
- Empty ACs get free 0.5 score (inflates average)
- `pass_threshold` config param is dead
- Both phases got identical scores (confidence=0.81) — deterministic but suspicious

### 4.4 Knowledge Base — WORKING (but empty)

- Search works, returns ranked results
- Indexing works, stores items in memory
- Cache with TTL works
- BM25 + fuzzy ranking works

**But:** All knowledge is hardcoded seed data. No real project docs are ever indexed. The search always returns the same 2 templated items.

### 4.5 Memory — WORKING (but empty)

- Store/load works
- Deduplication works
- Retention/GC works
- Scope filtering works

**But:** All memory is seeded templated data. No real project history is ever recorded.

---

## 5. Next Engineering Priorities

Ranked by real-world impact from this first run:

### Priority 1: ActStep Implementation

**What:** Replace the v1 stub with real code generation capability.

**Why:** Without this, CodeAI can plan but cannot execute. The entire value proposition depends on it.

**Scope:** Minimum viable: write generated plan to disk as structured files. Ideal: integrate with an LLM to produce actual code.

### Priority 2: Spec Quality Improvement

**What:** Fix `_extract_entities_for_models()` to detect real domain entities. Fix `_extract_api_contracts()` regex. Remove 60-char truncation.

**Why:** The generated spec is the foundation of the entire pipeline. Hallucinated data models and generic ACs propagate through OODA and Judge, making evaluations meaningless.

### Priority 3: State Persistence

**What:** Serialize `WorkflowState` to `state.json` after each phase. Enable pipeline resumption.

**Why:** Without persistence, pipeline interruption means starting over. Critical for long-running projects.

### Priority 4: Artifact Writing

**What:** Have `ActStep` write its output to disk (even if it's just the summary markdown).

**Why:** Artifacts are declared but never created. Downstream processes (review, testing) have nothing to work with.

### Priority 5: Knowledge Seeding from Real Sources

**What:** Instead of hardcoded template knowledge, index actual project files (README, existing code, docs).

**Why:** Knowledge retrieval is working but useless — it always returns the same 2 templated items regardless of the project.

---

## 6. Metrics

| Metric | Value |
|--------|-------|
| Pipeline completion | ✅ Full cycle completed |
| Phases executed | 2 / 2 |
| Phases passed judge | 2 / 2 |
| OODA steps executed | 8 (4 per phase) |
| Events published | 10 |
| Artifacts declared | 4 |
| Artifacts on disk | 0 |
| Errors | 0 |
| Time to complete | < 1s |
| Real code generated | 0 lines |
| Spec quality (subjective) | 3/10 |
| Judge evaluation quality | 5/10 |
| Knowledge usefulness | 1/10 |
| Memory usefulness | 1/10 |

---

## 7. Verdict

**CodeAI successfully runs the full pipeline cycle.** The infrastructure works. Events flow. State transitions are correct. Judge evaluates. No crashes.

**But it produces nothing useful.** The spec is low quality, the OODA Act step is a stub, knowledge and memory are empty templates, and no code is generated.

**CodeAI is a working orchestration framework looking for a real execution engine.**

The 5 priorities above would transform it from "impressive demo" to "useful tool".

---

*End of findings.*
