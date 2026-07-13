# WORKFLOW_STATE_MODEL.md — Workflow Engine State Model

**Date:** 2026-07-12
**Status:** Implemented (types only, no logic)
**File:** `scripts/core/types/workflow.py`

---

## 1. Overview

State model Workflow Engine — типы состояний и снимки для управления жизненным циклом pipeline.

**Реализовано:** типы (Enum + dataclass), сериализация JSON.
**Не реализовано:** бизнес-логика переходов.

---

## 2. Enums

### WorkflowStatus

Overall pipeline status.

```python
class WorkflowStatus(str, Enum):
    IDLE = "idle"              # No workflow running
    RUNNING = "running"        # Workflow in progress
    PAUSED = "paused"          # Workflow paused by user
    COMPLETED = "completed"    # All phases done
    FAILED = "failed"          # Workflow failed
    ROLLING_BACK = "rolling_back"  # Rollback in progress
```

### PhaseStatus (existing)

```python
class PhaseStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
```

### TaskStatus (existing)

```python
class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"
```

---

## 3. Dataclasses

### Task

```python
@dataclass
class Task(Serializable):
    uuid: UUID
    title: str
    description: str = ""
    status: TaskStatus = TaskStatus.PENDING
    assigned_role: str = ""
    spec_ref: str = ""
    branch: str | None = None
    dependencies: list[UUID] = field(default_factory=list)
```

### Phase

```python
@dataclass
class Phase(Serializable):
    id: str
    title: str
    description: str = ""
    status: PhaseStatus = PhaseStatus.PENDING
    depends_on: list[str] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)
    judge_passed: bool = False
```

### WorkflowState

```python
@dataclass
class WorkflowState(Serializable):
    current_phase: Phase | None = None
    phases: list[Phase] = field(default_factory=list)
    current_task: Task | None = None
    started_at: datetime | None = None
    updated_at: datetime | None = None
```

### RollbackEntry (new, frozen)

```python
@dataclass(frozen=True)
class RollbackEntry(Serializable):
    phase_id: str
    reason: str
    phase_status: PhaseStatus
    tasks_before: list[dict[str, Any]]  # serialized Task snapshots
    judge_passed: bool
    timestamp: datetime = field(default_factory=datetime.now)
```

### WorkflowSnapshot (new)

```python
@dataclass
class WorkflowSnapshot(Serializable):
    context: ProjectContext | None = None
    phase: Phase | None = None
    task: Task | None = None
    status: WorkflowStatus = WorkflowStatus.IDLE
    iteration: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    judge_verdict: Verdict | None = None
    rollback_stack: list[RollbackEntry] = field(default_factory=list)
```

---

## 4. State Transitions

### WorkflowStatus

```
IDLE ──start()──► RUNNING
RUNNING ──pause()──► PAUSED
PAUSED ──resume()──► RUNNING
RUNNING ──complete()──► COMPLETED
RUNNING ──fail()──► FAILED
RUNNING ──rollback()──► ROLLING_BACK
ROLLING_BACK ──(done)──► RUNNING
```

### PhaseStatus

```
PENDING ──start()──► IN_PROGRESS
IN_PROGRESS ──complete()──► COMPLETED
IN_PROGRESS ──fail()──► FAILED
IN_PROGRESS ──rollback()──► PENDING
FAILED ──retry()──► PENDING
```

### TaskStatus

```
PENDING ──start()──► IN_PROGRESS
IN_PROGRESS ──complete()──► COMPLETED
IN_PROGRESS ──fail()──► FAILED
IN_PROGRESS ──block()──► BLOCKED
BLOCKED ──unblock()──► PENDING
```

---

## 5. Serialization

All types implement `Serializable` mixin:
- `to_dict()` → JSON-safe dict
- `from_dict(data)` → reconstructed object
- `to_json()` → JSON string
- `from_json(text)` → reconstructed object

### WorkflowSnapshot custom deserialization

`WorkflowSnapshot` overrides `from_dict()` to handle lazy import of `ProjectContext` (avoids circular dependency with `types/project.py`).

### Example: JSON roundtrip

```python
snapshot = WorkflowSnapshot(
    status=WorkflowStatus.RUNNING,
    iteration=1,
    phase=Phase(id="p1", title="Phase 1"),
    judge_verdict=Verdict(overall=VerdictStatus.PASS),
    rollback_stack=[
        RollbackEntry(
            phase_id="p0",
            reason="Judge FAIL",
            phase_status=PhaseStatus.COMPLETED,
            tasks_before=[],
            judge_passed=False,
        )
    ],
)

# Serialize
json_str = snapshot.to_json()

# Deserialize
restored = WorkflowSnapshot.from_json(json_str)
assert restored.status == WorkflowStatus.RUNNING
assert restored.rollback_stack[0].phase_id == "p0"
```

---

## 6. Frozen vs Mutable

| Type | Frozen | Reason |
|------|--------|--------|
| RollbackEntry | ✅ | Immutable snapshot of past state |
| Task | ❌ | Status transitions during execution |
| Phase | ❌ | Status transitions during execution |
| WorkflowState | ❌ | Mutable pipeline state |
| WorkflowSnapshot | ❌ | Mutable (status, timestamps change) |

---

## 7. Public API

```python
from scripts.core.types import (
    WorkflowStatus,      # Enum: IDLE, RUNNING, PAUSED, COMPLETED, FAILED, ROLLING_BACK
    WorkflowSnapshot,    # Full state snapshot with serialization
    RollbackEntry,       # Frozen rollback record
    Phase,               # Phase with tasks
    Task,                # Task within a phase
    WorkflowState,       # Pipeline state (existing)
)
```

---

## 8. What Is NOT Implemented (yet)

- Transition logic (start, complete, rollback methods)
- Invariant enforcement (INV1-INV6)
- State persistence (load/save to disk)
- Concurrent phase prevention
- Rollback stack management
- Integration with Judge Engine
- Event publishing
