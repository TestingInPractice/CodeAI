# Event Bus — Implementation Review

**Date:** 2026-07-13  
**Status:** PASS  
**Reviewer:** opencode/big-pickle  

---

## 1. Files Created/Modified

| File | Action | Lines |
|------|--------|-------|
| `scripts/core/event_bus.py` | Rewritten | 107 |
| `tests/test_event_bus.py` | Created | 195 |

**Total:** ~302 lines (implementation + tests)

---

## 2. EVENTS.md §5 Compliance

### API Signature

```python
class EventBus:
    def subscribe(event: EventType | str, handler: Callable) -> None    # ✓ Implemented
    def unsubscribe(event: EventType | str, handler: Callable) -> None   # ✓ Implemented
    def publish(event: EventType | str, data: dict) -> None              # ✓ Implemented
    def publish_raw(event: Event) -> None                                # ✓ Implemented
```

### Wildcard Support

| Pattern | Matches | Status |
|---------|---------|--------|
| `"task.started"` | Exact event name | ✓ |
| `"task.*"` | All task events | ✓ |
| `"judge.*"` | All judge events | ✓ |
| `"*"` | All events | ✓ |

### Event Envelope

| Field | Type | Status |
|-------|------|--------|
| `name` | `str` | ✓ Set from EventType or string |
| `source` | `str` | ✓ From data["source"] or "unknown" |
| `event_id` | `UUID` | ✓ Auto-generated (Event dataclass default) |
| `correlation_id` | `UUID | None` | ✓ Supported (Event dataclass default) |
| `data` | `dict[str, Any]` | ✓ Payload from publish() |
| `timestamp` | `datetime` | ✓ Auto-generated (Event dataclass default) |

---

## 3. Backward Compatibility

| Before | After | Compatible |
|--------|-------|------------|
| `subscribe(EventType.X, handler)` | `subscribe(EventType \| str, handler)` | ✓ EventType still works |
| `publish(EventType.X, data)` | `publish(EventType \| str, data)` | ✓ EventType still works |
| `subscribe("task.started", handler)` | Same | ✓ |
| `publish("task.started", data)` | Same | ✓ |
| No `unsubscribe` | `unsubscribe()` added | ✓ New API |
| No `publish_raw` | `publish_raw()` added | ✓ New API |

---

## 4. Dispatch Deduplication

When a handler is subscribed to both an exact pattern and a wildcard pattern, it fires only once per publish:

```python
bus.subscribe("task.started", handler)  # exact
bus.subscribe("task.*", handler)        # wildcard
bus.publish("task.started", data)       # handler called ONCE
```

**Implementation:** `_dispatch()` uses `handled: set[int]` to track `id(handler)` and skip duplicates.

---

## 5. Test Coverage

### Test Count: 30

| Category | Tests |
|----------|-------|
| `TestSubscribe` | 5 |
| `TestUnsubscribe` | 4 |
| `TestPublishExact` | 6 |
| `TestPublishWildcards` | 6 |
| `TestPublishRaw` | 3 |
| `TestMultipleSubscribers` | 2 |
| `TestEdgeCases` | 4 |

### Test Categories

| Category | Coverage |
|----------|----------|
| Exact subscribe/unsubscribe | ✓ Full lifecycle |
| Wildcard subscribe | ✓ Domain, catch-all, exact |
| publish() | ✓ EventType, string, source default, fields |
| publish_raw() | ✓ Dispatches, wildcard, no envelope modification |
| Deduplication | ✓ Handler not called twice |
| Edge cases | ✓ No subscribers, empty data, no-dot names |

---

## 6. pytest Results

```
Ran 264 tests in 0.123s

OK
```

- Event Bus: 30/30 pass
- Full suite: 264/264 pass
- No regressions

---

## 7. Deviations

### `publish()` Modifies Data Dict

**Design:** Data dict passed to `publish()` is used as the event payload.

**Implementation:** `data.pop("source", "unknown")` extracts source from the data dict, modifying it in place. The `source` field becomes an Event-level attribute, not part of `data`.

**Reason:** Matches the EVENTS.md spec where `source` is a top-level Event field, not in `data`. The original data dict is still available as `event.data` (minus the source key).

### `publish_raw()` Does Not Create Envelope

**Implementation:** `publish_raw()` dispatches the pre-built Event directly without creating a new envelope.

**Reason:** Correct behavior — `publish_raw()` is for replay/logging where the Event already exists.

---

## 8. Verdict

**PASS**

| Criterion | Status |
|-----------|--------|
| API matches EVENTS.md §5 | ✓ |
| Wildcard support | ✓ |
| Backward compatible | ✓ |
| Deduplication | ✓ |
| 30 tests pass | ✓ |
| Full suite 264/264 | ✓ |
| No compilation errors | ✓ |
| No regressions | ✓ |
