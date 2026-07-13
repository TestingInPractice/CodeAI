# ARCHITECTURE_REVIEW_VALIDATION.md — P0/P1 Finding Validation

**Date:** 2026-07-12
**Reviewer:** Principal Software Architect
**Scope:** P0 and P1 findings from ARCHITECTURE_REVIEW.md
**Status:** COMPLETE — No code changes made

---

## Summary

| Finding | Verdict | Reason |
|---------|---------|--------|
| V-001 | **TRUE POSITIVE** | Method names differ from frozen API |
| V-002 | **TRUE POSITIVE** | Extra parameter not in frozen API |
| V-003 | **TRUE POSITIVE** | Extra methods not in frozen API |
| V-004 | **TRUE POSITIVE** | Types not in frozen contract |
| V-005 | **TRUE POSITIVE** | Enum not in frozen contract |
| V-006 | **TRUE POSITIVE** | Error not in frozen hierarchy |

**Result: 6/6 TRUE POSITIVE** — No false positives found.

---

## V-001: WorkflowEngine Method Names

### Status: TRUE POSITIVE

### Frozen Contract

**Source:** `docs/architecture/ARCHITECTURE_FREEZE.md:48-51`

```python
class WorkflowEngine:
    def start(phase_id: str) -> None:      # ✅ Matches
    def next() -> Phase | None:            # ❌ Mismatch
    def complete(phase_id: str, judge_passed: bool) -> None:  # ❌ Mismatch
    def rollback(phase_id: str, reason: str) -> None:         # ✅ Matches
```

### Actual Implementation

**File:** `scripts/core/workflow_engine.py:135,202,238,309`

```python
class WorkflowEngine:
    def start(self, phase_id: str) -> None:      # ✅ Matches
    def next_phase(self) -> Phase | None:         # ❌ Should be next()
    def complete_phase(self, phase_id: str, judge_passed: bool) -> None:  # ❌ Should be complete()
    def rollback(self, phase_id: str, reason: str) -> None:              # ✅ Matches
```

### Why It Violates

1. `next()` → `next_phase()` — method renamed
2. `complete()` → `complete_phase()` — method renamed

The frozen contract at `ARCHITECTURE_FREEZE.md:157` states: "Changing method signatures" is prohibited without ADR. While technically a rename, not a signature change, the method name is part of the public API contract.

### Recommended Fix

**Option A (Preferred):** Rename methods to match frozen API:
```python
def next(self) -> Phase | None:     # rename from next_phase()
def complete(self, phase_id: str, judge_passed: bool) -> None:  # rename from complete_phase()
```

**Option B:** Create ADR-0002 to update frozen API with new names.

---

## V-002: JudgeEngine Extra Parameter

### Status: TRUE POSITIVE

### Frozen Contract

**Source:** `docs/architecture/ARCHITECTURE_FREEZE.md:80`

```python
class JudgeEngine:
    def evaluate(response: str, context: str, spec: str) -> Verdict:  # 3 params
```

### Actual Implementation

**File:** `scripts/core/judge_engine.py:159-165`

```python
class JudgeEngine:
    def evaluate(
        self,
        response: str,
        context: str = "",
        spec: str = "",
        acceptance_criteria: list[str] | None = None,  # ← EXTRA PARAMETER
    ) -> Verdict:
```

### Why It Violates

1. Frozen API has 3 positional parameters
2. Actual implementation has 4 parameters (extra `acceptance_criteria`)
3. The extra parameter changes the method signature

The frozen contract at `ARCHITECTURE_FREEZE.md:157` states: "Changing method signatures" is prohibited without ADR.

### Recommended Fix

**Option A (Preferred):** Move AC checking to a separate method:
```python
def evaluate(self, response: str, context: str, spec: str) -> Verdict:
    """Full evaluation without AC check."""
    ...

def evaluate_with_ac(self, response: str, context: str, spec: str, acceptance_criteria: list[str]) -> Verdict:
    """Full evaluation with AC check."""
    ...
```

**Option B:** Create ADR-0003 to add `acceptance_criteria` parameter to frozen API.

---

## V-003: WorkflowEngine Extra Methods

### Status: TRUE POSITIVE

### Frozen Contract

**Source:** `docs/architecture/ARCHITECTURE_FREEZE.md:48-51`

```python
class WorkflowEngine:
    def start(phase_id: str) -> None:
    def next() -> Phase | None:
    def complete(phase_id: str, judge_passed: bool) -> None:
    def rollback(phase_id: str, reason: str) -> None:
```

**Total: 4 methods**

### Actual Implementation

**File:** `scripts/core/workflow_engine.py`

```python
class WorkflowEngine:
    # Frozen methods (4)
    def start(self, phase_id: str) -> None:                                          # line 135
    def next_phase(self) -> Phase | None:                                             # line 202
    def complete_phase(self, phase_id: str, judge_passed: bool) -> None:              # line 238
    def rollback(self, phase_id: str, reason: str) -> None:                          # line 309

    # Extra methods (8) — NOT in frozen contract
    def load(self) -> None:                                                           # line 78
    def save(self) -> None:                                                           # line 108
    def current_phase(self) -> Phase | None:                                          # line 230
    def current_task(self) -> Task | None:                                            # line 371
    def start_task(self, task_id: UUID) -> None:                                      # line 379
    def complete_task(self, task_id: UUID) -> None:                                   # line 427
    def fail_task(self, task_id: UUID) -> None:                                       # line 462
    def status(self) -> dict[str, Any]:                                               # line 499
```

**Total: 12 methods** (4 frozen + 8 extra)

### Why It Violates

The frozen contract at `ARCHITECTURE_FREEZE.md:157` states: "Adding new methods to existing engine classes" is prohibited without ADR.

8 methods were added that weren't in the frozen API:
- `load()`, `save()` — persistence (related to Repository Pattern)
- `current_phase()`, `current_task()` — state accessors
- `start_task()`, `complete_task()`, `fail_task()` — task lifecycle
- `status()` — status summary

### Recommended Fix

**Option A (Preferred):** Create ADR-0004 to add these methods to frozen API. They are useful and follow the single responsibility principle.

**Option B:** Extract task operations to a separate `TaskManager` class:
```python
class TaskManager:
    def __init__(self, engine: WorkflowEngine): ...
    def start_task(self, task_id: UUID) -> None: ...
    def complete_task(self, task_id: UUID) -> None: ...
    def fail_task(self, task_id: UUID) -> None: ...
```

---

## V-004: WorkflowSnapshot and RollbackEntry Not in Frozen Types

### Status: TRUE POSITIVE

### Frozen Contract

**Source:** `docs/architecture/ARCHITECTURE_FREEZE.md:93-127`

Lists 23 approved dataclasses. Neither `WorkflowSnapshot` nor `RollbackEntry` is included.

### Actual Implementation

**File:** `scripts/core/types/workflow.py:50-83`

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

### Why It Violates

1. `RollbackEntry` — frozen dataclass for rollback history (6 fields)
2. `WorkflowSnapshot` — mutable dataclass for state persistence (9 fields)

The frozen contract at `ARCHITECTURE_FREEZE.md:157` states: "Adding new fields to frozen dataclasses" is prohibited without ADR. While these are new types (not fields), they are new dataclasses that should be in the frozen contract.

### Recommended Fix

**Option A (Preferred):** Create ADR-0005 to add these types to frozen contract. They are essential for the Repository Pattern.

**Option B:** Move these types to `repositories/` package if they are persistence-specific:
```python
# scripts/core/repositories/models.py
@dataclass(frozen=True)
class RollbackEntry(Serializable): ...

@dataclass
class WorkflowSnapshot(Serializable): ...
```

---

## V-005: WorkflowStatus Enum Not in Frozen Enums

### Status: TRUE POSITIVE

### Frozen Contract

**Source:** `docs/architecture/ARCHITECTURE_FREEZE.md:130-141`

Lists 8 approved enums. `WorkflowStatus` is not included.

### Actual Implementation

**File:** `scripts/core/enums.py:77-84`

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

### Why It Violates

1. `WorkflowStatus` is used by `WorkflowSnapshot.status` field
2. It tracks overall workflow pipeline state
3. It is not in the frozen enum list

The frozen contract at `ARCHITECTURE_FREEZE.md:157` states: "Changing enum values" is prohibited without ADR. Adding a new enum is a similar concern.

### Recommended Fix

**Option A (Preferred):** Create ADR-0006 to add `WorkflowStatus` to frozen enums.

**Option B:** Use existing enums if possible. Check if `PhaseStatus` could serve this purpose:
```python
# Current PhaseStatus values: PENDING, IN_PROGRESS, COMPLETED, FAILED
# WorkflowStatus values: IDLE, RUNNING, PAUSED, COMPLETED, FAILED, ROLLING_BACK
```
`PhaseStatus` is missing: IDLE, PAUSED, ROLLING_BACK. So `WorkflowStatus` is needed.

---

## V-006: RepositoryError Not in Frozen Error Hierarchy

### Status: TRUE POSITIVE

### Frozen Contract

**Source:** `docs/architecture/ARCHITECTURE_FREEZE.md:480-510` (in CORE_RUNTIME.md)

```python
class CodeAIError(Exception):       # Base
class SpecError(CodeAIError):       # Spec Engine
class WorkflowError(CodeAIError):   # Workflow Engine
class OODAError(CodeAIError):       # OODA Runtime
class KnowledgeError(CodeAIError):  # Knowledge Layer
class MemoryError(CodeAIError):     # Memory Layer
class JudgeError(CodeAIError):      # Judge Engine
```

**Total: 7 error types** (1 base + 6 subsystem)

### Actual Implementation

**File:** `scripts/core/repositories/json_repo.py:240-269`

```python
class RepositoryError(Exception):  # ← Does NOT inherit from CodeAIError
    """Repository operation error."""
    def __init__(
        self,
        message: str,
        code: str = "REPO_ERROR",
        recoverable: bool = False,
        cause: Exception | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.recoverable = recoverable
        self.cause = cause
```

### Why It Violates

1. `RepositoryError` inherits from `Exception`, not `CodeAIError`
2. It duplicates the `CodeAIError` interface (message, code, recoverable, cause)
3. It is not in the frozen error hierarchy

The frozen contract at `ARCHITECTURE_FREEZE.md:157` states: "Changing error hierarchy" is prohibited without ADR.

### Recommended Fix

**Option A (Preferred):** Make `RepositoryError` inherit from `CodeAIError`:
```python
from scripts.core.errors import CodeAIError

class RepositoryError(CodeAIError):
    """Repository operation error."""
    pass
```

**Option B:** Create ADR-0007 to add `RepositoryError` to frozen hierarchy.

---

## Appendix: Frozen Contract Violations Summary

| Violation | Document | Section | Rule |
|-----------|----------|---------|------|
| V-001 | ARCHITECTURE_FREEZE.md | §3.2 | Method names must match |
| V-002 | ARCHITECTURE_FREEZE.md | §3.6 | Method signatures must match |
| V-003 | ARCHITECTURE_FREEZE.md | §7 | Adding new methods prohibited |
| V-004 | ARCHITECTURE_FREEZE.md | §4 | Adding new types prohibited |
| V-005 | ARCHITECTURE_FREEZE.md | §5 | Adding new enums prohibited |
| V-006 | ARCHITECTURE_FREEZE.md | §7 | Changing error hierarchy prohibited |

---

## Recommended ADRs

| ADR | Title | Finding |
|-----|-------|---------|
| ADR-0002 | Reconcile WorkflowEngine method names | V-001 |
| ADR-0003 | Add acceptance_criteria parameter to JudgeEngine.evaluate() | V-002 |
| ADR-0004 | Add task operations and persistence methods to WorkflowEngine | V-003 |
| ADR-0005 | Add WorkflowSnapshot and RollbackEntry to frozen types | V-004 |
| ADR-0006 | Add WorkflowStatus to frozen enums | V-005 |
| ADR-0007 | Add RepositoryError to frozen error hierarchy | V-006 |

---

*Validation completed. No files were modified.*
