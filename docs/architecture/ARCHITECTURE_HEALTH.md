# ARCHITECTURE_HEALTH.md — Full Architecture Audit

**Date:** 2026-07-11  
**Package:** `scripts/core/` (21 files, 928 lines)

---

## 1. SOLID — 8/10

### Single Responsibility (S) — 9/10

Each module has one clear responsibility:

| Module | Responsibility | Verdict |
|--------|---------------|---------|
| `enums.py` | Enumerations only | ✅ |
| `errors.py` | Exception hierarchy only | ✅ |
| `serialization.py` | JSON serialization only | ✅ |
| `event_bus.py` | Pub/sub only | ✅ |
| `types/*.py` | Data definitions only | ✅ |
| `*_engine.py` | API contract (stub) | ✅ |

**Deduction:** `serialization.py` at 160 lines is the largest file. It handles type detection, conversion, and the mixin. Could be split into `_converters.py` + `mixin.py` if it grows.

### Open/Closed (O) — 8/10

- **Open:** New subsystems add a `types/` module + an `*_engine.py` stub without modifying existing files
- **Open:** New error types inherit from `CodeAIError`
- **Open:** New enums extend `Enum`
- **Closed:** Existing API contracts don't change when new features are added

**Deduction:** `Serializable.from_json_value()` uses type dispatch with fallback `return value`. Unknown types pass through silently rather than raising. Could add strict mode.

### Liskov Substitution (L) — 9/10

- All error subclasses are drop-in replacements for `CodeAIError`
- All `Serializable` subclasses implement the same `to_dict()`/`from_dict()` contract
- All enums use `str, Enum` — values are JSON-serializable strings

**Deduction:** No violation detected. All subtypes honor base contracts.

### Interface Segregation (I) — 8/10

- Each engine stub exposes only the methods it needs
- `Serializable` mixin provides 4 methods — all useful
- `EventBus` has only `subscribe`/`publish` — minimal

**Deduction:** `RuntimeContext` has 7 fields. Some consumers need only `project_root`/`branch`, others need only `current_agent`/`session_id`. Could split into focused protocols, but current size is acceptable.

### Dependency Inversion (D) — 9/10

- Engine stubs depend on `types/` abstractions, not implementations
- `types/` depends only on `enums/` and `serialization/`
- No engine imports another engine

**Deduction:** Dependency direction is clean. No concrete implementations in type definitions.

---

## 2. Clean Architecture — 8/10

### Layers

```
┌─────────────────────────────────┐
│  Frameworks & Drivers (shell)   │  ← scripts/build-loop/
├─────────────────────────────────┤
│  Interface Adapters (engines)   │  ← *_engine.py (stubs)
├─────────────────────────────────┤
│  Domain (types)                 │  ← types/*.py
├─────────────────────────────────┤
│  Use Cases (serialization)      │  ← serialization.py
├─────────────────────────────────┤
│  Entities (enums, errors)       │  ← enums.py, errors.py
└─────────────────────────────────┘
```

**Passes:**
- Domain types have zero framework dependencies
- Engine stubs depend only on types
- Shell scripts are external adapters

**Fails:**
- Engine stubs are currently empty — actual logic lives in shell scripts outside `scripts/core/`
- No use-case layer with business rules (planned but not implemented)

---

## 3. DDD Boundaries — 8/10

### Bounded Contexts

| Context | Module | Entities | Value Objects |
|---------|--------|----------|---------------|
| Spec | `types/spec.py`, `spec_engine.py` | Requirement, AC | StructuredSpec, Scope, ValidationResult |
| Workflow | `types/workflow.py`, `workflow_engine.py` | Task, Phase | WorkflowState |
| OODA | `types/ooda.py`, `ooda_runtime.py` | OODAResult | Artifact |
| Knowledge | `types/knowledge.py`, `knowledge_layer.py` | Knowledge | Context |
| Memory | `types/memory.py`, `memory_layer.py` | MemoryEntry | — |
| Judge | `types/judge.py`, `judge_engine.py` | Verdict, Rubric | Score, RouteAction |

**Passes:**
- Clear separation between contexts
- No cross-context type dependencies (except `ProjectContext` aggregation)
- Each context has its own engine stub

**Fails:**
- `ProjectContext` knows about all 6 contexts — expected as integration point, but could become a god object if fields accumulate

---

## 4. Dependency Rule — 9/10

**Rule:** Dependencies point inward only. Outer layers depend on inner layers, never reverse.

```
serialization.py  ← foundation (no deps)
enums.py          ← foundation (no deps)
errors.py         ← foundation (no deps)
types/*           ← depends on serialization, enums
*_engine.py       ← depends on types (never on each other)
event_bus.py      ← depends on types
```

**Verified:** No engine imports another engine. No type imports an engine. No circular dependencies.

---

## 5. Single Responsibility — 9/10

Already covered in SOLID section. Summary:

| Module | SRP Score | Notes |
|--------|-----------|-------|
| `serialization.py` | 8/10 | Largest file (160 lines). Handles conversion + mixin. |
| `errors.py` | 9/10 | Pure hierarchy, no logic beyond `__init__`/`__repr__` |
| `event_bus.py` | 9/10 | Pure pub/sub, no side effects |
| `enums.py` | 10/10 | Pure data |
| `types/*.py` | 10/10 | Pure dataclasses |
| `*_engine.py` | 10/10 | Pure stubs |

---

## 6. Open/Closed — 8/10

Already covered in SOLID section. Key extension points:

| Extension Point | Mechanism | Status |
|----------------|-----------|--------|
| New subsystem | Add `types/X.py` + `X_engine.py` | ✅ Works |
| New error type | Inherit `CodeAIError` | ✅ Works |
| New enum value | Extend `Enum` | ✅ Works |
| New event | Add to `EVENTS.md` | ✅ Documented |
| New judge adapter | Add to `judge/adapters/` | ✅ Structured |
| New serialization type | Extend `from_json_value()` | ⚠️ Requires modifying serialization.py |

**Deduction:** Serialization is closed for new types without code changes. Could add a registry pattern, but current set is stable.

---

## 7. Low Coupling — 9/10

| Metric | Value | Verdict |
|--------|-------|---------|
| Engine → Engine imports | 0 | ✅ Excellent |
| Type → Engine imports | 0 | ✅ Excellent |
| Cross-type module imports | 1 (`ooda.py` → `common.py`) | ✅ Minimal |
| Foundation → Domain imports | 0 | ✅ Clean |
| Max fan-in | `Serializable` (24 consumers) | ✅ Expected |

**Deduction:** Coupling is intentionally low. The only convergence point is `ProjectContext` (integration hub by design).

---

## 8. High Cohesion — 8/10

| Module | Cohesion | Notes |
|--------|----------|-------|
| `types/spec.py` | 9/10 | All types belong to Spec domain |
| `types/workflow.py` | 9/10 | All types belong to Workflow domain |
| `types/judge.py` | 9/10 | All types belong to Judge domain |
| `types/knowledge.py` | 9/10 | All types belong to Knowledge domain |
| `types/memory.py` | 10/10 | Single type |
| `types/common.py` | 7/10 | `Artifact`, `Event`, `RuntimeContext` are loosely related — shared by convention, not domain |
| `serialization.py` | 8/10 | All functions serve serialization, but size is growing |

**Deduction:** `common.py` is a "grab bag" — acceptable at 3 types, but should not grow.

---

## 9. Composition Over Inheritance — 9/10

| Pattern | Usage | Verdict |
|---------|-------|---------|
| `ProjectContext` | Composes 6 subsystem types | ✅ Composition |
| `WorkflowState` | Contains `Phase`, `Task` | ✅ Composition |
| `Phase` | Contains `list[Task]` | ✅ Composition |
| `StructuredSpec` | Contains `list[Requirement]`, `list[AC]` | ✅ Composition |
| `Serializable` | Mixin inheritance | ✅ Appropriate (no state, only behavior) |
| Error hierarchy | Exception inheritance | ✅ Appropriate (standard Python pattern) |

**Deduction:** No inappropriate inheritance. `Serializable` as a mixin is the right pattern — it adds behavior without state.

---

## 10. Immutable Contracts — 8/10

| Contract | Immutable? | Notes |
|----------|-----------|-------|
| `CORE_RUNTIME.md` | ✅ Frozen | Changes require ADR |
| `API_CONTRACT.md` | ✅ Frozen | Method signatures are stable |
| `types/*.py` dataclasses | ⚠️ Mutable | Dataclasses are mutable by default |
| `enums.py` | ✅ Immutable | Enum values can't change |
| `errors.py` | ✅ Immutable | Exception structure is stable |

**Deduction:** Dataclasses are mutable (`Task.status = "completed"` works). Could add `frozen=True` for immutability, but mutability is needed for workflow state transitions. Acceptable tradeoff — state transitions are intentional.

---

## 11. Backward Compatibility — 9/10

| Mechanism | Status |
|-----------|--------|
| `types/__init__.py` re-exports | ✅ `from scripts.core.types import Task` works |
| `from_dict()` reconstructs full objects | ✅ Roundtrip tested |
| `str, Enum` for JSON safety | ✅ Values are strings, not enum objects |
| Error codes are stable strings | ✅ Won't change with refactoring |
| API signatures use `Path`/`UUID` | ⚠️ Changed from `str` — breaking for old callers |

**Deduction:** The `str` → `Path`/`UUID` migration in API signatures was a breaking change. Since stubs had no real implementations, impact is zero. Future signature changes require ADR.

---

## Summary Scorecard

| Criterion | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| SOLID | 8/10 | 20% | 1.60 |
| Clean Architecture | 8/10 | 15% | 1.20 |
| DDD Boundaries | 8/10 | 15% | 1.20 |
| Dependency Rule | 9/10 | 15% | 1.35 |
| Single Responsibility | 9/10 | 10% | 0.90 |
| Open/Closed | 8/10 | 5% | 0.40 |
| Low Coupling | 9/10 | 5% | 0.45 |
| High Cohesion | 8/10 | 5% | 0.40 |
| Composition > Inheritance | 9/10 | 5% | 0.45 |
| Immutable Contracts | 8/10 | 5% | 0.40 |
| Backward Compatibility | 9/10 | 5% | 0.45 |
| **Total** | | **100%** | **8.40/10** |

---

## Improvement List (sorted by priority)

### P0 — Critical (do before first implementation)

1. **Add `frozen=True` to immutable types** — `Requirement`, `AC`, `DataModel`, `APIContract`, `Scope`, `RubricCriterion`, `Knowledge`. Keep mutable: `Task`, `Phase`, `WorkflowState`, `RuntimeContext`, `ProjectContext`, `Rubric`, `Verdict`, `Score`, `RouteAction`, `OODAResult`, `MemoryEntry`, `Context`, `StructuredSpec`, `ValidationResult`, `Artifact`, `Event`.

2. **Move `KnowledgeType` import from `knowledge_layer.py` to use `types` barrel** — Minor dependency leak. Change `from scripts.core.enums import KnowledgeType` to import through `types`.

### P1 — High (do before v1.0)

3. **Add `__all__` to `serialization.py`** — Currently exports internal helpers. Should only export `Serializable`, `to_json_value`, `from_json_value`.

4. **Add type validation to `Serializable.from_dict()`** — Currently silently ignores unknown keys. Should warn or error on unexpected fields.

5. **Add `to_dict()` tests for all 24 dataclasses** — Roundtrip tests exist informally. Should be formalized in `tests/`.

### P2 — Medium (do before v2.0)

6. **Split `serialization.py`** — If it grows beyond 200 lines, split into `_converters.py` (functions) + `_mixin.py` (Serializable class).

7. **Add `ProjectContext.validate()` method** — Validate internal consistency (e.g., `workflow.current_phase` exists in `workflow.phases`).

8. **Add event naming registry** — Currently event names are strings in `EVENTS.md`. Could add `EventName` enum for type safety.

9. **Add `Serializable.to_dict(indent=...)` support** — Currently `to_json()` supports `**kwargs` but `to_dict()` doesn't support pretty-printing.

### P3 — Low (nice to have)

10. **Add `@dataclass_json`-style decorator** — If the `Serializable` mixin pattern proves insufficient, consider code generation. But current approach is simpler and dependency-free.

11. **Add `Protocol` types for engine interfaces** — Currently stubs define APIs via docstrings. Could add `typing.Protocol` classes for formal interface contracts.

12. **Add `common.py` size guard** — Prevent it from growing beyond 5 types. If more shared types emerge, consider a `types/shared.py` split.
