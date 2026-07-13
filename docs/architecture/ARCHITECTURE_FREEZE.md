# ARCHITECTURE_FREEZE.md — Architecture v1.0 Frozen

**Date:** 2026-07-12
**Version:** v1.0
**Status:** FROZEN — changes require ADR

---

## 1. Freeze Rules

1. Никакой новой функциональности не реализовывать.
2. Не создавать новые подсистемы.
3. Не менять публичный API.
4. Не изменять типы без необходимости.
5. **Любое изменение публичного API возможно только через ADR.**

---

## 2. Approved Subsystems

| # | Subsystem | Module | Status |
|---|-----------|--------|--------|
| 1 | **Spec Engine** | `scripts.core.spec_engine` | Stub |
| 2 | **Workflow Engine** | `scripts.core.workflow_engine` | Stub |
| 3 | **OODA Runtime** | `scripts.core.ooda_runtime` | Stub |
| 4 | **Knowledge Layer** | `scripts.core.knowledge_layer` | Stub |
| 5 | **Memory Layer** | `scripts.core.memory_layer` | Stub |
| 6 | **Judge Engine** | `scripts.core.judge_engine` | Stub |
| 7 | **Event Bus** | `scripts.core.event_bus` | Stub (extension point) |

---

## 3. Official API

### 3.1 SpecEngine

| Method | Signature | Returns |
|--------|-----------|---------|
| `generate` | `(prompt: str) -> Path` | `Path` |
| `validate` | `(goals_path: Path) -> ValidationResult` | `ValidationResult` |
| `approve` | `(goals_path: Path) -> None` | `None` |
| `parse` | `(goals_path: Path) -> StructuredSpec` | `StructuredSpec` |

### 3.2 WorkflowEngine

| Method | Signature | Returns |
|--------|-----------|---------|
| `start` | `(phase_id: str) -> None` | `None` |
| `next` | `() -> Phase \| None` | `Phase \| None` |
| `complete` | `(phase_id: str, judge_passed: bool) -> None` | `None` |
| `rollback` | `(phase_id: str, reason: str) -> None` | `None` |

### 3.3 OODARuntime

| Method | Signature | Returns |
|--------|-----------|---------|
| `execute` | `(task: Task) -> OODAResult` | `OODAResult` |
| `resume` | `(task_id: UUID) -> OODAResult` | `OODAResult` |
| `interrupt` | `(task_id: UUID) -> None` | `None` |

### 3.4 KnowledgeLayer

| Method | Signature | Returns |
|--------|-----------|---------|
| `search` | `(query: str, scope: str = "all") -> list[Knowledge]` | `list[Knowledge]` |
| `retrieve` | `(context_type: KnowledgeType, params: dict[str, Any]) -> Context` | `Context` |

### 3.5 MemoryLayer

| Method | Signature | Returns |
|--------|-----------|---------|
| `store` | `(entry: MemoryEntry) -> None` | `None` |
| `load` | `(query: str, scope: str = "project") -> list[MemoryEntry]` | `list[MemoryEntry]` |
| `summarize` | `(scope: str, depth: str = "brief") -> str` | `str` |

### 3.6 JudgeEngine

| Method | Signature | Returns |
|--------|-----------|---------|
| `evaluate` | `(response: str, context: str, spec: str) -> Verdict` | `Verdict` |
| `score` | `(response: str, rubric: Rubric) -> Score` | `Score` |
| `route` | `(verdict: Verdict) -> RouteAction` | `RouteAction` |

### 3.7 EventBus

| Method | Signature | Returns |
|--------|-----------|---------|
| `subscribe` | `(event: str, handler: Callable[[Event], None]) -> None` | `None` |
| `publish` | `(event: str, data: dict[str, Any]) -> None` | `None` |

---

## 4. Approved Dataclasses (23 total)

### Frozen (immutable)

| # | Type | Module | Fields |
|---|------|--------|--------|
| 1 | `Requirement` | `types/spec.py` | id: UUID, title: str, description: str, priority: Priority, dependencies: list[UUID] |
| 2 | `AC` | `types/spec.py` | id: UUID, requirement_id: UUID, description: str, verifiable: bool |
| 3 | `DataModel` | `types/spec.py` | name: str, fields: dict[str, str], description: str |
| 4 | `APIContract` | `types/spec.py` | method: str, path: str, request: dict, response: dict, description: str |
| 5 | `Scope` | `types/spec.py` | included: list[str], excluded: list[str] |
| 6 | `Knowledge` | `types/knowledge.py` | id: UUID, source: str, kind: KnowledgeKind, content: str, score: float, metadata: dict |
| 7 | `RubricCriterion` | `types/judge.py` | id: str, label: str, weight: int, scale: int, pass_threshold: int, critical: bool |

### Mutable (state transitions)

| # | Type | Module | Fields |
|---|------|--------|--------|
| 8 | `StructuredSpec` | `types/spec.py` | requirements: list[Requirement], acceptance_criteria: list[AC], data_models: list[DataModel], api_contracts: list[APIContract], scope: Scope |
| 9 | `ValidationResult` | `types/spec.py` | valid: bool, errors: list[str], warnings: list[str] |
| 10 | `Task` | `types/workflow.py` | uuid: UUID, title: str, description: str, status: TaskStatus, assigned_role: str, spec_ref: str, branch: str \| None, dependencies: list[UUID] |
| 11 | `Phase` | `types/workflow.py` | id: str, title: str, description: str, status: PhaseStatus, depends_on: list[str], tasks: list[Task], judge_passed: bool |
| 12 | `WorkflowState` | `types/workflow.py` | current_phase: Phase \| None, phases: list[Phase], current_task: Task \| None, started_at: datetime \| None, updated_at: datetime \| None |
| 13 | `OODAResult` | `types/ooda.py` | task_id: UUID, step: str, success: bool, outputs: list[Artifact], summary: str |
| 14 | `Context` | `types/knowledge.py` | context_type: KnowledgeType, items: list[Knowledge], summary: str |
| 15 | `MemoryEntry` | `types/memory.py` | id: UUID, type: MemoryType, content: str, timestamp: datetime, metadata: dict |
| 16 | `Verdict` | `types/judge.py` | overall: VerdictStatus, scores: dict[str, float], failures: list[str], confidence: float |
| 17 | `Score` | `types/judge.py` | value: float, breakdown: dict[str, float], judge: str |
| 18 | `RouteAction` | `types/judge.py` | target: RouteTarget, reason: str, task_id: UUID \| None, phase_id: str \| None |
| 19 | `Rubric` | `types/judge.py` | name: str, criteria: list[RubricCriterion] |
| 20 | `Artifact` | `types/common.py` | name: str, path: Path, type: str, checksum: str \| None, metadata: dict |
| 21 | `Event` | `types/common.py` | name: str, source: str, event_id: UUID, correlation_id: UUID \| None, data: dict, timestamp: datetime |
| 22 | `RuntimeContext` | `types/common.py` | project_root: Path, branch: str, iteration: int, variables: dict, current_agent: str, current_role: str, session_id: UUID \| None |
| 23 | `ProjectContext` | `types/project.py` | spec: StructuredSpec, workflow: WorkflowState, memory: list[MemoryEntry], knowledge: list[Knowledge], runtime: RuntimeContext \| None, verdict: Verdict \| None |

---

## 5. Approved Enums (8 total)

| # | Enum | Module | Values |
|---|------|--------|--------|
| 1 | `KnowledgeKind` | `enums.py` | SPEC, ADR, CODE, DOCUMENT, ARTICLE, TEST, API, MEMORY |
| 2 | `KnowledgeType` | `enums.py` | ARCHITECTURE, BEST_PRACTICE, REFERENCE, TOOL, PATTERN |
| 3 | `MemoryType` | `enums.py` | PROJECT_HISTORY, JUDGE_HISTORY, ITERATIONS, DECISIONS, LONG_TERM, USER_PREFERENCES, LEARNED_PATTERNS |
| 4 | `PhaseStatus` | `enums.py` | PENDING, IN_PROGRESS, COMPLETED, FAILED |
| 5 | `Priority` | `enums.py` | MUST, SHOULD, COULD, NICE |
| 6 | `RouteTarget` | `enums.py` | OODA, SPEC, WORKFLOW |
| 7 | `TaskStatus` | `enums.py` | PENDING, IN_PROGRESS, COMPLETED, BLOCKED, FAILED |
| 8 | `VerdictStatus` | `enums.py` | PASS, PASS_WITH_CONCERNS, FAIL |

---

## 6. Stable Directories

| Directory | Contents | Status |
|-----------|----------|--------|
| `scripts/core/` | Core Runtime modules | Frozen |
| `scripts/core/types/` | Dataclass definitions | Frozen |
| `scripts/core/judge/` | Judge adapters | Frozen |
| `docs/architecture/` | Architecture docs | Frozen |
| `docs/architecture/adr/` | Architecture Decision Records | Active (append-only) |

---

## 7. What Is Prohibited Without New ADR

- Adding new subsystems
- Adding new methods to existing engine classes
- Changing method signatures
- Adding new fields to frozen dataclasses
- Changing enum values
- Changing error hierarchy
- Changing event names
- Changing dependency rules (types → enums only, engines → types only)
- Changing serialization format
- Changing public API barrel (`types/__init__.py`)
