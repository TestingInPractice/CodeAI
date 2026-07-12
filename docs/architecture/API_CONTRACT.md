# API_CONTRACT.md — Public API of Core Runtime Subsystems

**Date:** 2026-07-11  
**Status:** Frozen — changes require ADR

---

## 1. SpecEngine

**Module:** `scripts.core.spec_engine`  
**Exceptions:** `SpecError`

| Method | Signature | Returns | Raises | Events |
|--------|-----------|---------|--------|--------|
| `generate` | `(prompt: str) -> Path` | `Path` (to goals.md) | `SpecError` | `spec.generated` |
| `validate` | `(goals_path: Path) -> ValidationResult` | `ValidationResult` | `SpecError` | `spec.validated` |
| `approve` | `(goals_path: Path) -> None` | `None` | `SpecError` | `spec.approved` |
| `parse` | `(goals_path: Path) -> StructuredSpec` | `StructuredSpec` | `SpecError` | — |

**Parameters:**
- `prompt: str` — user's project description (free text)
- `goals_path: Path` — path to goals.md file

**Returns:**
- `ValidationResult { valid: bool, errors: list[str], warnings: list[str] }`
- `StructuredSpec { requirements, acceptance_criteria, data_models, api_contracts, scope }`

---

## 2. WorkflowEngine

**Module:** `scripts.core.workflow_engine`  
**Exceptions:** `WorkflowError`

| Method | Signature | Returns | Raises | Events |
|--------|-----------|---------|--------|--------|
| `start` | `(phase_id: str) -> None` | `None` | `WorkflowError` | `workflow.started` |
| `next` | `() -> Phase \| None` | `Phase \| None` | — | — |
| `complete` | `(phase_id: str, judge_passed: bool) -> None` | `None` | `WorkflowError` | `workflow.completed` |
| `rollback` | `(phase_id: str, reason: str) -> None` | `None` | `WorkflowError` | `workflow.rollback` |

**Parameters:**
- `phase_id: str` — phase identifier (e.g., `"plan-release"`)
- `judge_passed: bool` — whether Judge Engine passed this phase
- `reason: str` — reason for rollback

**Returns:**
- `Phase { id, title, description, status, depends_on, tasks, judge_passed }`

**Invariants enforced:**
- INV1: implement-spec-stage cannot be active without tasks
- INV2: write-tests cannot start until implement is completed
- INV3: completed phase requires all tasks completed
- INV4: pending phase cannot have completed tasks
- INV5: task_cycle cannot start until decompose is completed
- INV6: complete cannot happen until all phases are completed

---

## 3. OODARuntime

**Module:** `scripts.core.ooda_runtime`  
**Exceptions:** `OODAError`

| Method | Signature | Returns | Raises | Events |
|--------|-----------|---------|--------|--------|
| `execute` | `(task: Task) -> OODAResult` | `OODAResult` | `OODAError` | `task.started`, `task.completed` |
| `resume` | `(task_id: UUID) -> OODAResult` | `OODAResult` | `OODAError` | `task.started`, `task.completed` |
| `interrupt` | `(task_id: UUID) -> None` | `None` | `OODAError` | `task.interrupted` |

**Parameters:**
- `task: Task` — task to execute (full Task dataclass)
- `task_id: UUID` — ID of task to resume/interrupt

**Returns:**
- `OODAResult { task_id, step, success, outputs: list[Artifact], summary }`
- `Artifact { name, path: Path, type, checksum, metadata }`

**Step Mappings:**

| Step | Agents | Output |
|------|--------|--------|
| analyst | @observe → @orient | architecture.md |
| dev | @decide → validate → @act | dev-summary.md |
| tester | @decide → validate → @act | tester-summary.md |

---

## 4. KnowledgeLayer

**Module:** `scripts.core.knowledge_layer`  
**Exceptions:** `KnowledgeError`

| Method | Signature | Returns | Raises | Events |
|--------|-----------|---------|--------|--------|
| `search` | `(query: str, scope: str = "all") -> list[Knowledge]` | `list[Knowledge]` | `KnowledgeError` | `knowledge.requested`, `knowledge.retrieved` |
| `retrieve` | `(context_type: KnowledgeType, params: dict[str, Any]) -> Context` | `Context` | `KnowledgeError` | `knowledge.requested`, `knowledge.retrieved` |

**Parameters:**
- `query: str` — search query (free text)
- `scope: str` — search scope: `"all"`, `"docs"`, `"code"`, `"references"`
- `context_type: KnowledgeType` — one of: `ARCHITECTURE`, `BEST_PRACTICE`, `REFERENCE`, `TOOL`, `PATTERN`
- `params: dict[str, Any]` — additional retrieval parameters

**Returns:**
- `Knowledge { id: UUID, source: str, kind: KnowledgeKind, content: str, score: float, metadata }`
- `Context { context_type: KnowledgeType, items: list[Knowledge], summary: str }`

**Note:** KnowledgeLayer is passive — it provides knowledge, never decides or manages state.

---

## 5. MemoryLayer

**Module:** `scripts.core.memory_layer`  
**Exceptions:** `MemoryError`

| Method | Signature | Returns | Raises | Events |
|--------|-----------|---------|--------|--------|
| `store` | `(entry: MemoryEntry) -> None` | `None` | `MemoryError` | `memory.stored` |
| `load` | `(query: str, scope: str = "project") -> list[MemoryEntry]` | `list[MemoryEntry]` | `MemoryError` | `memory.loaded` |
| `summarize` | `(scope: str, depth: str = "brief") -> str` | `str` | `MemoryError` | — |

**Parameters:**
- `entry: MemoryEntry` — entry to store
- `query: str` — search query
- `scope: str` — memory scope: `"project"`, `"session"`, `"global"`
- `depth: str` — summary depth: `"brief"`, `"detailed"`, `"full"`

**Returns:**
- `MemoryEntry { id: UUID, type: MemoryType, content: str, timestamp: datetime, metadata }`

**Memory Types:** `PROJECT_HISTORY`, `JUDGE_HISTORY`, `ITERATIONS`, `DECISIONS`, `LONG_TERM`, `USER_PREFERENCES`, `LEARNED_PATTERNS`

---

## 6. JudgeEngine

**Module:** `scripts.core.judge_engine`  
**Exceptions:** `JudgeError`

| Method | Signature | Returns | Raises | Events |
|--------|-----------|---------|--------|--------|
| `evaluate` | `(response: str, context: str, spec: str) -> Verdict` | `Verdict` | `JudgeError` | `judge.evaluated` |
| `score` | `(response: str, rubric: Rubric) -> Score` | `Score` | `JudgeError` | — |
| `route` | `(verdict: Verdict) -> RouteAction` | `RouteAction` | — | `judge.routed` |

**Parameters:**
- `response: str` — response to evaluate (file path or text)
- `context: str` — context for evaluation
- `spec: str` — spec for AC verification
- `rubric: Rubric` — rubric to score against
- `verdict: Verdict` — verdict from evaluate()

**Returns:**
- `Verdict { overall: VerdictStatus, scores: dict[str, float], failures: list[str], confidence: float }`
- `Score { value: float, breakdown: dict[str, float], judge: str }`
- `RouteAction { target: RouteTarget, reason: str, task_id: UUID | None, phase_id: str | None }`

**VerdictStatus:** `PASS`, `PASS_WITH_CONCERNS`, `FAIL`  
**RouteTarget:** `ooda`, `spec`, `workflow`

---

## 7. EventBus

**Module:** `scripts.core.event_bus`  
**Status:** Extension point — stub, not required for initial implementation.

| Method | Signature | Returns | Raises | Events |
|--------|-----------|---------|--------|--------|
| `subscribe` | `(event: str, handler: Callable[[Event], None]) -> None` | `None` | — | — |
| `publish` | `(event: str, data: dict[str, Any]) -> None` | `None` | — | — |

**Event Names:**

| Event | Source | Description |
|-------|--------|-------------|
| `spec.generated` | Spec Engine | goals.md generated |
| `spec.validated` | Spec Engine | goals.md validated |
| `spec.approved` | Spec Engine | Human gate passed |
| `workflow.started` | Workflow Engine | Phase started |
| `workflow.completed` | Workflow Engine | Phase completed |
| `workflow.rollback` | Workflow Engine | Phase rolled back |
| `task.started` | OODA Runtime | Task started |
| `task.interrupted` | OODA Runtime | Task interrupted |
| `task.completed` | OODA Runtime | Task completed |
| `knowledge.requested` | OODA Runtime | Context requested |
| `knowledge.retrieved` | Knowledge Layer | Context retrieved |
| `memory.stored` | Memory Layer | Entry stored |
| `memory.loaded` | Memory Layer | Entries loaded |
| `judge.evaluated` | Judge Engine | Evaluation completed |
| `judge.routed` | Judge Engine | Next step determined |

---

## 8. Exception Hierarchy

```
CodeAIError
├── SpecError
├── WorkflowError
├── OODAError
├── KnowledgeError
├── MemoryError
└── JudgeError
```

All exceptions inherit from `CodeAIError`. Each subsystem raises only its own exception type.

---

## 9. Stub vs Contract Compliance

| Stub | Issue | Fix |
|------|-------|-----|
| `event_bus.py:52` | `timestamp=datetime.datetime.now().isoformat()` passes `str`, should be `datetime` | Fix type |
| `spec_engine.py:22` | `generate() -> str` should return `Path` | Fix signature |
| `spec_engine.py:33,44,52` | `goals_path: str` should be `Path` | Fix signature |
| `ooda_runtime.py:32,43` | `task_id: str` should be `UUID` | Fix signature |
| `knowledge_layer.py:40` | `context_type: str` should be `KnowledgeType`, `params: dict` should be `dict[str, Any]` | Fix signature |
