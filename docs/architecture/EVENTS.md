# EVENTS.md — Event Bus Design

**Date:** 2026-07-11  
**Status:** Design — not yet implemented

---

## 1. Event Naming Convention

Format: `{domain}.{action}` (lowercase, dot-separated)

```
spec.generated
spec.validated
spec.approved
workflow.started
workflow.completed
workflow.rollback
task.started
task.interrupted
task.completed
knowledge.requested
knowledge.retrieved
memory.stored
memory.loaded
judge.evaluated
judge.routed
```

---

## 2. Event Envelope

All events share a common envelope (`Event` dataclass):

```python
@dataclass
class Event:
    name: str                    # "spec.created"
    source: str                  # "spec_engine"
    event_id: UUID               # auto-generated
    correlation_id: UUID | None  # links related events
    data: dict[str, Any]         # event-specific payload
    timestamp: datetime          # auto-generated
```

**Correlation ID:** Links events within a single execution cycle.  
Example: `task.started` and `task.completed` share the same `correlation_id`.

---

## 3. Event Catalog

### 3.1 Spec Events

#### `spec.created`

**Source:** SpecEngine  
**Trigger:** `SpecEngine.generate()` completes successfully

| Field | Type | Description |
|-------|------|-------------|
| `goals_path` | `str` | Path to generated goals.md |
| `prompt` | `str` | Original user prompt (truncated to 500 chars) |
| `requirements_count` | `int` | Number of F-XXX requirements parsed |

```json
{
  "goals_path": "docs/specs/goals.md",
  "prompt": "Build a REST API for user management...",
  "requirements_count": 5
}
```

---

#### `spec.approved`

**Source:** SpecEngine  
**Trigger:** `SpecEngine.approve()` — human gate passed

| Field | Type | Description |
|-------|------|-------------|
| `goals_path` | `str` | Path to approved goals.md |
| `requirements_count` | `int` | Final requirement count |
| `ac_count` | `int` | Acceptance criteria count |

```json
{
  "goals_path": "docs/specs/goals.md",
  "requirements_count": 5,
  "ac_count": 12
}
```

---

### 3.2 Workflow Events

#### `phase.started`

**Source:** WorkflowEngine  
**Trigger:** `WorkflowEngine.start()` completes

| Field | Type | Description |
|-------|------|-------------|
| `phase_id` | `str` | Phase identifier |
| `phase_title` | `str` | Human-readable title |
| `tasks_count` | `int` | Number of tasks in phase |

```json
{
  "phase_id": "implement-spec",
  "phase_title": "Implement Spec Engine",
  "tasks_count": 3
}
```

---

### 3.3 Task Events

#### `task.started`

**Source:** OODARuntime  
**Trigger:** `OODARuntime.execute()` begins

| Field | Type | Description |
|-------|------|-------------|
| `task_id` | `str` | Task UUID |
| `task_title` | `str` | Task title |
| `phase_id` | `str` | Parent phase |
| `agent` | `str` | Agent performing the task (analyst/dev/tester) |
| `role` | `str` | Agent role (@observe, @decide, @act) |

```json
{
  "task_id": "a1b2c3d4-...",
  "task_title": "Implement generate() method",
  "phase_id": "implement-spec",
  "agent": "developer",
  "role": "@act"
}
```

---

#### `task.completed`

**Source:** OODARuntime  
**Trigger:** `OODARuntime.execute()` completes successfully

| Field | Type | Description |
|-------|------|-------------|
| `task_id` | `str` | Task UUID |
| `step` | `str` | OODA step completed (analyst/dev/tester) |
| `success` | `bool` | Always `true` for this event |
| `outputs` | `list[dict]` | Artifacts produced |
| `summary` | `str` | Execution summary |

```json
{
  "task_id": "a1b2c3d4-...",
  "step": "dev",
  "success": true,
  "outputs": [
    {"name": "dev-summary.md", "path": ".opencode/tasks/p1/dev-summary.md", "type": "markdown"}
  ],
  "summary": "Implemented generate() with LLM integration"
}
```

---

#### `task.interrupted`

**Source:** OODARuntime  
**Trigger:** `OODARuntime.interrupt()` called

| Field | Type | Description |
|-------|------|-------------|
| `task_id` | `str` | Task UUID |
| `reason` | `str` | Interrupt reason (user/timeout/error) |
| `partial_outputs` | `list[dict]` | Artifacts saved before interrupt |

```json
{
  "task_id": "a1b2c3d4-...",
  "reason": "user",
  "partial_outputs": [
    {"name": "observe-summary.md", "path": ".opencode/tasks/p1/observe-summary.md", "type": "markdown"}
  ]
}
```

---

### 3.4 Judge Events

#### `judge.passed`

**Source:** JudgeEngine  
**Trigger:** `JudgeEngine.evaluate()` returns `VerdictStatus.PASS` or `PASS_WITH_CONCERNS`

| Field | Type | Description |
|-------|------|-------------|
| `task_id` | `str` | Task UUID (if task-level) |
| `phase_id` | `str` | Phase ID (if phase-level) |
| `overall` | `str` | `"PASS"` or `"PASS_WITH_CONCERNS"` |
| `scores` | `dict[str, float]` | Judge scores |
| `confidence` | `float` | Confidence level (0.0–1.0) |
| `concerns` | `list[str]` | Warnings (empty if PASS) |

```json
{
  "task_id": "a1b2c3d4-...",
  "phase_id": null,
  "overall": "PASS",
  "scores": {"structural": 0.95, "semantic": 0.88},
  "confidence": 0.92,
  "concerns": []
}
```

---

#### `judge.failed`

**Source:** JudgeEngine  
**Trigger:** `JudgeEngine.evaluate()` returns `VerdictStatus.FAIL`

| Field | Type | Description |
|-------|------|-------------|
| `task_id` | `str` | Task UUID |
| `phase_id` | `str` | Phase ID |
| `overall` | `str` | `"FAIL"` |
| `scores` | `dict[str, float]` | Judge scores |
| `confidence` | `float` | Confidence level |
| `failures` | `list[str]` | Failure reasons |
| `route_target` | `str` | `"ooda"` / `"spec"` / `"workflow"` |
| `route_reason` | `str` | Routing explanation |

```json
{
  "task_id": "a1b2c3d4-...",
  "phase_id": "implement-spec",
  "overall": "FAIL",
  "scores": {"structural": 0.45, "semantic": 0.60},
  "confidence": 0.78,
  "failures": ["AC-003 not covered", "Missing error handling"],
  "route_target": "ooda",
  "route_reason": "Retry with updated context"
}
```

---

### 3.5 Knowledge Events

#### `knowledge.retrieved`

**Source:** KnowledgeLayer  
**Trigger:** `KnowledgeLayer.search()` or `KnowledgeLayer.retrieve()` completes

| Field | Type | Description |
|-------|------|-------------|
| `query` | `str` | Original search query |
| `scope` | `str` | Search scope |
| `results_count` | `int` | Number of results |
| `context_type` | `str` | Context type (for retrieve) |

```json
{
  "query": "authentication patterns",
  "scope": "all",
  "results_count": 5,
  "context_type": "best_practice"
}
```

---

### 3.6 Memory Events

#### `memory.stored`

**Source:** MemoryLayer  
**Trigger:** `MemoryLayer.store()` completes

| Field | Type | Description |
|-------|------|-------------|
| `entry_id` | `str` | MemoryEntry UUID |
| `entry_type` | `str` | MemoryType value |
| `content_preview` | `str` | First 200 chars of content |

```json
{
  "entry_id": "e5f6g7h8-...",
  "entry_type": "judge_history",
  "content_preview": "Judge PASS for phase implement-spec with confidence 0.92..."
}
```

---

## 4. Correlation Patterns

### Single Task Execution

```
task.started      correlation_id = abc-123
  ↓
knowledge.retrieved  correlation_id = abc-123
  ↓
task.completed    correlation_id = abc-123
  ↓
judge.passed      correlation_id = abc-123
```

### Retry Flow

```
task.started      correlation_id = abc-123
  ↓
judge.failed      correlation_id = abc-123
  ↓
task.started      correlation_id = def-456  (new cycle)
  ↓
judge.passed      correlation_id = def-456
```

### Phase Lifecycle

```
phase.started     correlation_id = ghi-789
  ↓
task.started      correlation_id = ghi-789
  ↓
task.completed    correlation_id = ghi-789
  ↓
judge.passed      correlation_id = ghi-789
```

---

## 5. Event Bus API (Design)

```python
class EventBus:
    def subscribe(event: str, handler: Callable[[Event], None]) -> None:
        """Subscribe to an event by name pattern.

        Supports exact match: "task.started"
        Supports wildcard: "task.*" (all task events)
        Supports domain: "judge.*" (all judge events)
        """

    def unsubscribe(event: str, handler: Callable[[Event], None]) -> None:
        """Remove a subscription."""

    def publish(event: str, data: dict[str, Any]) -> None:
        """Publish an event. Creates Event envelope automatically."""

    def publish_raw(event: Event) -> None:
        """Publish a pre-built Event (for replay/logging)."""
```

### Handler Signature

```python
def my_handler(event: Event) -> None:
    """Handle an event.

    Args:
        event: Event envelope with name, source, data, timestamp.
    """
    print(f"Received {event.name} from {event.source}")
    print(f"Data: {event.data}")
```

---

## 6. Future Extensions (not implemented now)

| Extension | Description |
|-----------|-------------|
| **Dead Letter Queue** | Failed handlers retry with backoff |
| **Event Store** | Persist events for replay/audit |
| **Saga Pattern** | Multi-step workflows with compensation |
| **Event Sourcing** | Rebuild state from event history |
| **Async Handlers** | Non-blocking event processing |
