# REPORT: P0+P1 Health Fixes

**Date:** 2026-07-12
**Based on:** `docs/architecture/ARCHITECTURE_HEALTH.md`

## P0: frozen=True for immutable dataclasses

Added `frozen=True` to 7 dataclasses that represent immutable domain values:

| Type | File | Reason |
|------|------|--------|
| `Requirement` | `types/spec.py` | Domain value, identity by UUID |
| `AC` | `types/spec.py` | Domain value, identity by UUID |
| `DataModel` | `types/spec.py` | Schema definition |
| `APIContract` | `types/spec.py` | Schema definition |
| `Scope` | `types/spec.py` | Immutable constraint set |
| `Knowledge` | `types/knowledge.py` | Immutable fact |
| `RubricCriterion` | `types/judge.py` | Rubric element |

Still mutable (intentionally): `Task`, `Phase`, `WorkflowState`, `Event`, `RuntimeContext`, `Verdict`, `Score`, `RouteAction`, `Rubric`, `OODAResult`, `MemoryEntry`, `StructuredSpec`, `ValidationResult`, `Context`, `Artifact`, `ProjectContext`.

## P1: Import hygiene

- `knowledge_layer.py`: changed `from scripts.core.enums import KnowledgeType` → `from scripts.core.types import KnowledgeType` (public API only)
- `types/__init__.py`: added all 8 enums to barrel exports (`KnowledgeKind`, `KnowledgeType`, `MemoryType`, `PhaseStatus`, `Priority`, `RouteTarget`, `TaskStatus`, `VerdictStatus`)
- `types/__init__.py`: added `WorkflowState` to barrel exports

## P1: Serialization hardening

`serialization.py` improvements:
- Added `__all__` with `Serializable`, `to_json_value`, `from_json_value`
- `from_dict()` now accepts `strict=False` (default, warns on unknown fields) or `strict=True` (raises `ValueError`)
- `from_json()` passes `strict` through

## Verification

| Check | Status |
|-------|--------|
| `python -m compileall scripts/core/` | PASS (exit 0) |
| No circular imports | PASS (all types importable from `scripts.core.types`) |
| Frozen dataclasses | PASS (AttributeError on assignment for all 7) |
| Mutable types | PASS (no frozen) |
| Serialization roundtrip | PASS (`to_dict()` → `from_dict()` identity) |
| Unknown fields warning | PASS (warning emitted) |
| Strict mode | PASS (`ValueError` raised) |
| Public API `__all__` | PASS (31 exports) |
