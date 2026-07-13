# ADR_REVIEW.md — Architecture Decision Record Audit

**Date:** 2026-07-12
**Scope:** Full repository audit for undocumented architectural decisions
**Status:** COMPLETE — No code changes made

---

## 1. Executive Summary

| Metric | Value |
|--------|-------|
| **Existing ADRs** | 1 |
| **Undocumented Decisions** | 11 |
| **Total Architectural Decisions** | 12 |
| **ADR Coverage** | 8.3% |

**Verdict:** The repository has **significant ADR debt**. Only 1 ADR exists (ADR-0001: Core Runtime Architecture), while 11 architectural decisions were made without documentation. This violates the frozen contract at `ARCHITECTURE_FREEZE.md:15` which states: "Любое изменение публичного API возможно только через ADR."

---

## 2. Existing ADRs

### ADR-0001: Core Runtime Architecture

**File:** `docs/architecture/adr/ADR-0001-core-runtime.md`
**Status:** Accepted
**Covers:** 6-subsystem + Event Bus architecture design

---

## 3. Undocumented Architectural Decisions

### UD-001: Repository Pattern

**File:** `scripts/core/repositories/base.py`, `scripts/core/repositories/json_repo.py`

**Code:**
```python
class WorkflowRepository(ABC):
    """Abstract repository for WorkflowSnapshot persistence."""
    
    @abstractmethod
    def load(self) -> Optional[WorkflowSnapshot]: ...
    
    @abstractmethod
    def save(self, snapshot: WorkflowSnapshot) -> None: ...
    
    @abstractmethod
    def backup(self, label: str = "") -> str: ...
    
    @abstractmethod
    def restore(self, backup_id: str) -> WorkflowSnapshot: ...
    
    @abstractmethod
    def delete(self) -> None: ...
    
    @abstractmethod
    def list_backups(self) -> list[dict]: ...
```

**Why It Should Become an ADR:**
1. Introduces a new architectural pattern not in CORE_RUNTIME.md
2. Adds persistence abstraction not in original design
3. Creates new dependency direction (WorkflowEngine → WorkflowRepository)
4. Adds `WorkflowSnapshot` and `RollbackEntry` types not in frozen contract

**Priority:** HIGH

**Proposed ADR Title:** ADR-0002: Repository Pattern for Workflow State Persistence

---

### UD-002: Serializable Mixin

**File:** `scripts/core/serialization.py`

**Code:**
```python
class Serializable:
    """Mixin for dataclasses to support JSON serialization."""
    
    def to_dict(self) -> dict[str, Any]: ...
    
    @classmethod
    def from_dict(cls, data: dict[str, Any], strict: bool = False) -> Serializable: ...
    
    def to_json(self, **kwargs: Any) -> str: ...
    
    @classmethod
    def from_json(cls, text: str, strict: bool = False) -> Serializable: ...
```

**Why It Should Become an ADR:**
1. Defines serialization format for all types (not in ARCHITECTURE_FREEZE.md)
2. Uses mixin pattern instead of decorators or code generation
3. Handles UUID, datetime, Path, Enum, nested dataclasses
4. Provides `strict` mode for unknown fields

**Priority:** HIGH

**Proposed ADR Title:** ADR-0003: Serializable Mixin for JSON Serialization

---

### UD-003: Error Hierarchy Expansion

**File:** `scripts/core/errors.py`

**Code:**
```python
class CodeAIError(Exception):
    """Base exception for all CodeAI errors."""
    def __init__(self, message: str, code: str, recoverable: bool = False,
                 context: dict[str, Any] | None = None, cause: Exception | None = None): ...

class SpecError(CodeAIError): ...
class WorkflowError(CodeAIError): ...
class OODAError(CodeAIError): ...
class KnowledgeError(CodeAIError): ...
class MemoryError(CodeAIError): ...
class JudgeError(CodeAIError): ...

# NEW (not in CORE_RUNTIME.md):
class ValidationError(CodeAIError): ...
class ConfigurationError(CodeAIError): ...
class InfrastructureError(CodeAIError): ...
```

**Why It Should Become an ADR:**
1. CORE_RUNTIME.md defines 7 error types (1 base + 6 subsystem)
2. Actual implementation has 10 error types (1 base + 6 subsystem + 3 utility)
3. `ValidationError`, `ConfigurationError`, `InfrastructureError` not in frozen contract

**Priority:** MEDIUM

**Proposed ADR Title:** ADR-0004: Extended Error Hierarchy for Cross-Cutting Concerns

---

### UD-004: WorkflowStatus Enum

**File:** `scripts/core/enums.py`

**Code:**
```python
class WorkflowStatus(str, Enum):
    """Overall workflow pipeline status."""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLING_BACK = "rolling_back"
```

**Why It Should Become an ADR:**
1. ARCHITECTURE_FREEZE.md §5 lists 8 enums — `WorkflowStatus` is not included
2. Used by `WorkflowSnapshot.status` field
3. Tracks overall workflow pipeline state (distinct from `PhaseStatus`)

**Priority:** HIGH

**Proposed ADR Title:** ADR-0005: WorkflowStatus Enum for Pipeline State Tracking

---

### UD-005: WorkflowSnapshot Type

**File:** `scripts/core/types/workflow.py`

**Code:**
```python
@dataclass
class WorkflowSnapshot(Serializable):
    """Full workflow state snapshot at a point in time."""
    context: Any = None
    phase: Phase | None = None
    task: Task | None = None
    status: WorkflowStatus = WorkflowStatus.IDLE
    iteration: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    judge_verdict: Verdict | None = None
    rollback_stack: list[RollbackEntry] = field(default_factory=list)
```

**Why It Should Become an ADR:**
1. ARCHITECTURE_FREEZE.md §4 lists 23 dataclasses — `WorkflowSnapshot` is not included
2. Essential for Repository Pattern persistence
3. Contains `judge_verdict` field that creates cross-type dependency (workflow → judge)

**Priority:** HIGH

**Proposed ADR Title:** ADR-0006: WorkflowSnapshot for State Persistence

---

### UD-006: RollbackEntry Type

**File:** `scripts/core/types/workflow.py`

**Code:**
```python
@dataclass(frozen=True)
class RollbackEntry(Serializable):
    """Snapshot of a rolled-back phase state."""
    phase_id: str
    reason: str
    phase_status: PhaseStatus
    tasks_before: list[dict[str, Any]]
    judge_passed: bool
    timestamp: datetime = field(default_factory=datetime.now)
```

**Why It Should Become an ADR:**
1. ARCHITECTURE_FREEZE.md §4 lists 23 dataclasses — `RollbackEntry` is not included
2. Essential for rollback history tracking
3. Used by `WorkflowSnapshot.rollback_stack`

**Priority:** HIGH

**Proposed ADR Title:** ADR-0007: RollbackEntry for Rollback History Tracking

---

### UD-007: WorkflowEngine Extra Methods

**File:** `scripts/core/workflow_engine.py`

**Code:**
```python
class WorkflowEngine:
    # Frozen API (4 methods):
    def start(self, phase_id: str) -> None: ...
    def next_phase(self) -> Phase | None: ...
    def complete_phase(self, phase_id: str, judge_passed: bool) -> None: ...
    def rollback(self, phase_id: str, reason: str) -> None: ...
    
    # NEW (8 methods not in frozen API):
    def load(self) -> None: ...
    def save(self) -> None: ...
    def current_phase(self) -> Phase | None: ...
    def current_task(self) -> Task | None: ...
    def start_task(self, task_id: UUID) -> None: ...
    def complete_task(self, task_id: UUID) -> None: ...
    def fail_task(self, task_id: UUID) -> None: ...
    def status(self) -> dict[str, Any]: ...
```

**Why It Should Become an ADR:**
1. ARCHITECTURE_FREEZE.md §3.2 defines 4 methods — actual has 12
2. Extra methods add persistence, task operations, status queries
3. Violates "Adding new methods to existing engine classes" rule

**Priority:** HIGH

**Proposed ADR Title:** ADR-0008: Extended WorkflowEngine Methods for Task Management

---

### UD-008: JudgeEngine Extra Parameter

**File:** `scripts/core/judge_engine.py`

**Code:**
```python
class JudgeEngine:
    def evaluate(
        self,
        response: str,
        context: str = "",
        spec: str = "",
        acceptance_criteria: list[str] | None = None,  # ← EXTRA
    ) -> Verdict: ...
```

**Why It Should Become an ADR:**
1. ARCHITECTURE_FREEZE.md §3.6 defines `evaluate(response, context, spec)` — 3 params
2. Actual has 4 params (extra `acceptance_criteria`)
3. Violates "Changing method signatures" rule

**Priority:** HIGH

**Proposed ADR Title:** ADR-0009: Acceptance Criteria Parameter in JudgeEngine.evaluate()

---

### UD-009: Event Bus Implementation

**File:** `scripts/core/event_bus.py`

**Code:**
```python
class EventBus:
    """Event Bus — extension point for subsystem communication."""
    
    def __init__(self):
        self._handlers: defaultdict[str, list[Callable]] = defaultdict(list)
    
    def subscribe(self, event: str, handler: Callable) -> None: ...
    def publish(self, event: str, data: dict[str, Any]) -> None: ...
```

**Why It Should Become an ADR:**
1. ARCHITECTURE_FREEZE.md §3.7 defines API — but implementation details not documented
2. Uses `defaultdict` for handler storage
3. Creates `Event` object with `source` from data dict
4. Synchronous execution (no async/await)

**Priority:** MEDIUM

**Proposed ADR Title:** ADR-0010: Event Bus Implementation Details

---

### UD-010: Dependency Direction Rules

**File:** `docs/architecture/DEPENDENCY_GRAPH.md`

**Code (from documentation):**
```
Level 0: Foundation (no internal deps)
├── enums.py          → stdlib only
├── errors.py         → stdlib only
└── types/common.py   → stdlib only

Level 1: Types (depend on Foundation)
├── types/spec.py       → enums
├── types/workflow.py   → enums
├── types/knowledge.py  → enums
├── types/memory.py     → enums
├── types/judge.py      → enums
├── types/ooda.py       → types/common
└── types/project.py    → types/{all}

Level 2: Subsystems (depend on Types only)
├── spec_engine.py       → types
├── workflow_engine.py   → types, errors, repositories
├── ooda_runtime.py      → types
├── knowledge_layer.py   → types
├── memory_layer.py      → types
├── judge_engine.py      → types, errors
└── event_bus.py         → types
```

**Why It Should Become an ADR:**
1. DEPENDENCY_GRAPH.md documents rules but not the decision process
2. Defines "types → enums only, engines → types only" constraint
3. Exception: `workflow_engine.py` imports from `repositories` (not in original rules)
4. Exception: `judge_engine.py` imports `errors` (allowed but not documented)

**Priority:** MEDIUM

**Proposed ADR Title:** ADR-0011: Dependency Direction Rules and Exceptions

---

### UD-011: str Enum Pattern

**File:** `scripts/core/enums.py`

**Code:**
```python
class Priority(str, Enum):
    """Requirement priority."""
    MUST = "must"
    SHOULD = "should"
    COULD = "could"
    NICE = "nice"
```

**Why It Should Become an ADR:**
1. All enums use `str, Enum` pattern (not just `Enum`)
2. Enables JSON serialization without custom encoder
3. Allows `Priority.MUST == "must"` comparison
4. Not documented in ARCHITECTURE_FREEZE.md or CORE_RUNTIME.md

**Priority:** LOW

**Proposed ADR Title:** ADR-0012: str Enum Pattern for JSON Serialization

---

## 4. Summary by Area

### API Freeze
| Decision | Status | ADR Needed |
|----------|--------|------------|
| WorkflowEngine 4-method API | ⚠️ EXTENDED | UD-007 |
| JudgeEngine 3-param evaluate | ⚠️ EXTENDED | UD-008 |
| EventBus subscribe/publish | ✅ MATCHES | UD-009 (details) |

### Type Freeze
| Decision | Status | ADR Needed |
|----------|--------|------------|
| 23 dataclasses | ⚠️ 25 TYPES | UD-005, UD-006 |
| 8 enums | ⚠️ 9 ENUMS | UD-004 |
| Serializable mixin | ❌ NOT DOCUMENTED | UD-002 |

### Dependency Rule
| Decision | Status | ADR Needed |
|----------|--------|------------|
| types → enums only | ✅ MATCHES | — |
| engines → types only | ⚠️ EXCEPTIONS | UD-010 |

### Repository Pattern
| Decision | Status | ADR Needed |
|----------|--------|------------|
| WorkflowRepository ABC | ❌ NOT DOCUMENTED | UD-001 |
| JsonWorkflowRepository | ❌ NOT DOCUMENTED | UD-001 |
| RepositoryError | ❌ NOT DOCUMENTED | UD-001 |

### Event Bus
| Decision | Status | ADR Needed |
|----------|--------|------------|
| EventBus API | ✅ MATCHES | — |
| Implementation details | ❌ NOT DOCUMENTED | UD-009 |

### Workflow Engine Contract
| Decision | Status | ADR Needed |
|----------|--------|------------|
| Method names | ⚠️ RENAMED | UD-007 |
| Method count | ⚠️ 4 → 12 | UD-007 |
| Invariants INV1-INV6 | ✅ DOCUMENTED | — |

### Judge Contract
| Decision | Status | ADR Needed |
|----------|--------|------------|
| evaluate() signature | ⚠️ EXTENDED | UD-008 |
| 4-pillar scoring | ❌ NOT DOCUMENTED | UD-008 |
| Routing logic | ❌ NOT DOCUMENTED | UD-008 |

### Memory Contract
| Decision | Status | ADR Needed |
|----------|--------|------------|
| MemoryLayer API | ✅ MATCHES | — |
| Storage format | ❌ NOT DOCUMENTED | — |

### Knowledge Contract
| Decision | Status | ADR Needed |
|----------|--------|------------|
| KnowledgeLayer API | ✅ MATCHES | — |
| Internal components | ❌ NOT DOCUMENTED | — |

---

## 5. Priority Matrix

### HIGH Priority (Must Have Before v1.0)

| # | Decision | Why High Priority |
|---|----------|-------------------|
| UD-001 | Repository Pattern | New architectural pattern, changes dependency direction |
| UD-002 | Serializable Mixin | Defines serialization format for all types |
| UD-004 | WorkflowStatus Enum | Not in frozen contract, used by WorkflowSnapshot |
| UD-005 | WorkflowSnapshot Type | Not in frozen contract, essential for persistence |
| UD-006 | RollbackEntry Type | Not in frozen contract, essential for rollback history |
| UD-007 | WorkflowEngine Extra Methods | 8 methods not in frozen API |
| UD-008 | JudgeEngine Extra Parameter | Signature changed from frozen contract |

### MEDIUM Priority (Should Have Before v1.0)

| # | Decision | Why Medium Priority |
|---|----------|---------------------|
| UD-003 | Error Hierarchy Expansion | 3 new error types not in frozen contract |
| UD-009 | Event Bus Implementation | Implementation details not documented |
| UD-010 | Dependency Direction Rules | Exceptions to documented rules |

### LOW Priority (Nice to Have)

| # | Decision | Why Low Priority |
|---|----------|------------------|
| UD-011 | str Enum Pattern | Implementation detail, not architectural |

---

## 6. Recommended ADR Creation Order

| Order | ADR | Title | Depends On |
|-------|-----|-------|------------|
| 1 | ADR-0002 | Repository Pattern for Workflow State Persistence | — |
| 2 | ADR-0003 | Serializable Mixin for JSON Serialization | — |
| 3 | ADR-0004 | Extended Error Hierarchy for Cross-Cutting Concerns | — |
| 4 | ADR-0005 | WorkflowStatus Enum for Pipeline State Tracking | — |
| 5 | ADR-0006 | WorkflowSnapshot for State Persistence | ADR-0002 |
| 6 | ADR-0007 | RollbackEntry for Rollback History Tracking | ADR-0002 |
| 7 | ADR-0008 | Extended WorkflowEngine Methods for Task Management | ADR-0002 |
| 8 | ADR-0009 | Acceptance Criteria Parameter in JudgeEngine.evaluate() | — |
| 9 | ADR-0010 | Event Bus Implementation Details | — |
| 10 | ADR-0011 | Dependency Direction Rules and Exceptions | ADR-0002 |
| 11 | ADR-0012 | str Enum Pattern for JSON Serialization | — |

---

## 7. Appendix: Frozen Contract Violations

| Violation | Document | Section | Rule |
|-----------|----------|---------|------|
| Repository Pattern | ARCHITECTURE_FREEZE.md | §7 | Adding new subsystems |
| Serializable Mixin | ARCHITECTURE_FREEZE.md | §7 | Changing serialization format |
| Error Expansion | ARCHITECTURE_FREEZE.md | §7 | Changing error hierarchy |
| WorkflowStatus | ARCHITECTURE_FREEZE.md | §5 | Adding new enums |
| WorkflowSnapshot | ARCHITECTURE_FREEZE.md | §4 | Adding new types |
| RollbackEntry | ARCHITECTURE_FREEZE.md | §4 | Adding new types |
| Extra Methods | ARCHITECTURE_FREEZE.md | §7 | Adding new methods |
| Extra Parameter | ARCHITECTURE_FREEZE.md | §7 | Changing method signatures |

---

*ADR Audit completed. No files were modified.*
