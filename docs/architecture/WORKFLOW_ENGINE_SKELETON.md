# WORKFLOW_ENGINE_SKELETON.md — Workflow Engine Skeleton

**Date:** 2026-07-12
**Status:** Skeleton (interface only, no business logic)
**File:** `scripts/core/workflow_engine.py`

---

## 1. Overview

Workflow Engine — управление жизненным циклом pipeline: фазы, задачи, переходы, rollback, сохранение состояния.

**Реализация:** только интерфейс + docstring + `raise NotImplementedError`.
**Бизнес-логика:** не реализована.
**Внешние библиотеки:** не используются.

---

## 2. Class: WorkflowEngine

### Dependencies

```python
from pathlib import Path
from uuid import UUID

from scripts.core.types import (
    Phase,
    ProjectContext,
    RuntimeContext,
    Task,
    Verdict,
    WorkflowState,
)
```

### Constructor

| Parameter | Type | Description |
|-----------|------|-------------|
| `context` | `ProjectContext` | Unified project context |
| `state_path` | `Path \| None` | Path to state file for persistence |

---

## 3. Methods

### Lifecycle

| Method | Signature | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `(context: ProjectContext, state_path: Path \| None)` | `None` | Initialize engine with context and optional state path |
| `load` | `() -> None` | `None` | Load workflow state from disk |
| `save` | `() -> None` | `None` | Save workflow state to disk |
| `status` | `() -> dict` | `dict` | Get current workflow status snapshot |

### Phase Management

| Method | Signature | Returns | Description |
|--------|-----------|---------|-------------|
| `start` | `(phase_id: str) -> None` | `None` | Start a phase (PENDING → IN_PROGRESS) |
| `next_phase` | `() -> Phase \| None` | `Phase \| None` | Find next ready phase |
| `current_phase` | `() -> Phase \| None` | `Phase \| None` | Get currently active phase |
| `complete_phase` | `(phase_id: str, judge_passed: bool) -> None` | `None` | Complete a phase (requires judge pass) |
| `rollback` | `(phase_id: str, reason: str) -> None` | `None` | Rollback phase (Judge decision) |

### Task Management

| Method | Signature | Returns | Description |
|--------|-----------|---------|-------------|
| `current_task` | `() -> Task \| None` | `Task \| None` | Get currently active task |
| `start_task` | `(task_id: UUID) -> None` | `None` | Start a task (PENDING → IN_PROGRESS) |
| `complete_task` | `(task_id: UUID) -> None` | `None` | Complete a task (IN_PROGRESS → COMPLETED) |
| `fail_task` | `(task_id: UUID) -> None` | `None` | Fail a task (IN_PROGRESS → FAILED) |

---

## 4. State Transitions

### Phase States

```
PENDING ──start()──► IN_PROGRESS ──complete_phase()──► COMPLETED
    │                      │
    │                      └──rollback()──► PENDING
    │
    └──(cannot start if deps not met)
```

### Task States

```
PENDING ──start_task()──► IN_PROGRESS ──complete_task()──► COMPLETED
                               │
                               └──fail_task()──► FAILED
```

---

## 5. Invariants

| ID | Rule | Enforcement |
|----|------|-------------|
| INV1 | implement-spec-stage cannot be active without tasks | `start()` checks tasks exist |
| INV2 | write-tests cannot start until implement is completed | `start()` checks deps |
| INV3 | completed phase requires all tasks completed | `complete_phase()` checks task status |
| INV4 | pending phase cannot have completed tasks | `start()` resets tasks |
| INV5 | task_cycle cannot start until decompose is completed | `start()` checks deps |
| INV6 | complete cannot happen until all phases are completed | `complete_phase()` checks all phases |

---

## 6. Usage Example

```python
from pathlib import Path
from scripts.core.workflow_engine import WorkflowEngine
from scripts.core.types import ProjectContext

# Initialize
context = ProjectContext()
engine = WorkflowEngine(context, state_path=Path(".workflow/state.json"))

# Load existing state
engine.load()

# Get next phase
phase = engine.next_phase()
if phase:
    # Start phase
    engine.start(phase.id)

    # Work on tasks
    task = engine.current_task()
    if task:
        engine.start_task(task.uuid)
        # ... do work ...
        engine.complete_task(task.uuid)

    # Complete phase (after judge passes)
    engine.complete_phase(phase.id, judge_passed=True)

# Save state
engine.save()

# Check status
print(engine.status())
```

---

## 7. What Is NOT Implemented (yet)

- Business logic for invariant enforcement
- State serialization/deserialization
- Phase dependency resolution
- Task dependency resolution
- Error handling (WorkflowError)
- Event publishing (EventBus integration)
- Concurrent phase prevention
- Retry limits
- Integration with Judge Engine

---

## 8. Next Steps

1. Implement `load()` / `save()` — JSON state persistence
2. Implement `start()` / `complete_phase()` with INV checks
3. Implement `start_task()` / `complete_task()` / `fail_task()`
4. Implement `rollback()` with task reset
5. Add `WorkflowError` exceptions
6. Add EventBus integration
7. Add tests
