# SERIALIZATION.md — JSON Serialization Model

**Date:** 2026-07-11  
**Status:** Frozen  
**Constraint:** No external dependencies (stdlib only)

---

## 1. Approach

All dataclasses inherit from `Serializable` mixin, which provides:

```python
obj.to_dict()        # dict[str, Any] — JSON-safe
obj.to_json(**kw)    # str — JSON string
ClassName.from_dict(d)    # reconstruct from dict
ClassName.from_json(s)    # reconstruct from JSON string
```

---

## 2. Type Conversion Rules

| Python Type | JSON Representation | Example |
|-------------|-------------------|---------|
| `UUID` | `string` (ISO format) | `"550e8400-e29b-41d4-a716-446655440000"` |
| `datetime` | `string` (ISO 8601) | `"2026-07-12T21:54:38.474531"` |
| `Path` | `string` (POSIX path) | `"/Users/test/project"` |
| `Enum` | `string` (enum value) | `"must"`, `"PASS"`, `"in_progress"` |
| `None` | `null` | `null` |
| `list[X]` | `[to_json_value(x) for x]` | `["uuid1", "uuid2"]` |
| `dict[K, V]` | `{k: to_json_value(v)}` | `{"key": "val"}` |
| `Optional[X]` | `X \| null` | `"uuid"` or `null` |
| Nested dataclass | `{...}` (recursive) | `{"id": "p1", "tasks": [...]}` |
| `str, int, float, bool` | passthrough | `"hello"`, `42`, `3.14`, `true` |
| Other | `str(value)` | fallback |

---

## 3. Usage

### Serialize

```python
from scripts.core.types import ProjectContext, Task, Phase

ctx = ProjectContext(...)
d = ctx.to_dict()         # dict
json_str = ctx.to_json(indent=2)  # JSON string
```

### Deserialize

```python
ctx = ProjectContext.from_dict(d)
ctx = ProjectContext.from_json(json_str)
```

### File I/O

```python
import json
from pathlib import Path

# Write
path = Path("state.json")
path.write_text(ctx.to_json(indent=2))

# Read
ctx = ProjectContext.from_json(path.read_text())
```

---

## 4. Complete Type Coverage

| Module | Types | Serializable |
|--------|-------|-------------|
| `common.py` | `Artifact`, `Event`, `RuntimeContext` | ✅ |
| `spec.py` | `Requirement`, `AC`, `DataModel`, `APIContract`, `Scope`, `StructuredSpec`, `ValidationResult` | ✅ |
| `workflow.py` | `Task`, `Phase`, `WorkflowState` | ✅ |
| `ooda.py` | `OODAResult` | ✅ |
| `knowledge.py` | `Knowledge`, `Context` | ✅ |
| `memory.py` | `MemoryEntry` | ✅ |
| `judge.py` | `Verdict`, `Score`, `RouteAction`, `RubricCriterion`, `Rubric` | ✅ |
| `project.py` | `ProjectContext` | ✅ |

**Total: 24 dataclasses, all serializable.**

---

## 5. Edge Cases

### Nested dataclasses
```python
Phase → contains list[Task] → each Task serialized recursively
WorkflowState → contains Phase | None → None serialized as null
```

### Optional fields
```python
RuntimeContext.session_id: UUID | None
# serialized as: "uuid-string" or null
```

### Empty collections
```python
StructuredSpec()  # all fields empty
# to_dict: {"requirements": [], "acceptance_criteria": [], ...}
```

### dict[str, Any] fields
```python
Event.data = {"nested": {"key": [1, 2, 3]}}
# serialized as-is (values may be complex)
# deserialized as-is (no type reconstruction)
```

---

## 6. Implementation: Serializable Mixin

```python
# scripts/core/serialization.py

class Serializable:
    def to_dict(self) -> dict[str, Any]:
        # Iterates dataclass fields, converts each value via to_json_value()

    def to_json(self, **kwargs) -> str:
        # json.dumps(self.to_dict(), **kwargs)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Serializable:
        # Reads field types via get_type_hints(), converts via from_json_value()

    @classmethod
    def from_json(cls, text: str) -> Serializable:
        # cls.from_dict(json.loads(text))
```

### Conversion functions
```python
def to_json_value(value: Any) -> Any:
    # UUID → str
    # datetime → isoformat()
    # Path → str
    # Enum → .value
    # Serializable → .to_dict()
    # list → [to_json_value(v) for v]
    # dict → {k: to_json_value(v)}

def from_json_value(value: Any, target_type: Any) -> Any:
    # str → UUID
    # str → datetime.fromisoformat()
    # str → Path(value)
    # str → EnumType(value)
    # dict → SerializableClass.from_dict(d)
    # list → [from_json_value(v, item_type) for v]
    # Optional[X] → unwrap and convert
```

---

## 7. Limitations

| Limitation | Workaround |
|------------|------------|
| `dict[str, Any]` values not typed | Store type metadata in context |
| Polymorphic lists not supported | Use discriminator field in dict |
| Circular references not supported | Break cycle with ID reference |
| `set` not natively JSON-serializable | Convert to list before serialization |
