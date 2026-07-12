# DEPENDENCY_GRAPH.md — Architecture Dependency Audit

**Date:** 2026-07-11  
**Package:** `scripts/core/`  
**Result:** PASS — no violations

---

## 1. Dependency Tree

```
Level 0: Foundation (no internal deps)
├── enums.py          → stdlib only
├── errors.py         → stdlib only
└── types/
    ├── common.py     → stdlib only
    ├── spec.py       → enums
    ├── workflow.py   → enums
    ├── knowledge.py  → enums
    ├── memory.py     → enums
    ├── judge.py      → enums
    ├── ooda.py       → types/common
    ├── project.py    → types/{common,spec,workflow,knowledge,memory,judge}
    └── __init__.py   → re-export only

Level 1: Subsystems (depend on types only)
├── spec_engine.py       → types (StructuredSpec, ValidationResult)
├── workflow_engine.py   → types (Phase)
├── ooda_runtime.py      → types (OODAResult, Task)
├── knowledge_layer.py   → types (Context, Knowledge)
├── memory_layer.py      → types (MemoryEntry)
├── judge_engine.py      → types (RouteAction, Rubric, Score, Verdict)
├── event_bus.py         → types (Event)
└── judge/
    └── adapters/
        └── deepeval.py  → types (Score, Verdict)
```

---

## 2. Dependency Diagram

```
                    ┌────────────┐
                    │  stdlib    │
                    └─────┬──────┘
                          │
              ┌───────────┼───────────┐
              ▼           ▼           ▼
          enums.py    errors.py   types/common.py
              │                     │
    ┌─────────┼─────────┐          │
    ▼         ▼         ▼          │
  spec.py  workflow  knowledge     │
    │       .py       .py          │
    │         │         │          │
    │         ▼         │          │
    │      memory.py    │          │
    │         │         │          │
    │         ▼         │          │
    │      judge.py     │          │
    │         │         │          │
    │         ▼         ▼          ▼
    │      ┌─────────────────────────┐
    │      │     types/project.py    │
    │      │   (integration point)   │
    │      └────────────┬────────────┘
    │                   │
    │      ┌────────────┴────────────────────────────┐
    │      │            types/__init__.py             │
    │      │          (re-export only)                │
    │      └────────────────────┬────────────────────┘
    │                           │
    ▼                           ▼
┌──────────────────────────────────────────────────┐
│              Level 1: Subsystems                  │
│                                                   │
│  spec_engine ──┐                                  │
│  workflow_eng ─┤                                  │
│  ooda_runtime ─┼── all import only from types     │
│  knowledge_lay─┤                                  │
│  memory_layer ─┤                                  │
│  judge_engine ─┤                                  │
│  event_bus ────┤                                  │
│  deepeval.py ──┘                                  │
└──────────────────────────────────────────────────┘
```

---

## 3. Import Matrix

| Module | Imports from |
|--------|-------------|
| `enums.py` | stdlib |
| `errors.py` | stdlib |
| `types/common.py` | stdlib |
| `types/spec.py` | `enums` |
| `types/workflow.py` | `enums` |
| `types/knowledge.py` | `enums` |
| `types/memory.py` | `enums` |
| `types/judge.py` | `enums` |
| `types/ooda.py` | `types/common` |
| `types/project.py` | `types/{common,spec,workflow,knowledge,memory,judge}` |
| `types/__init__.py` | all type modules (re-export) |
| `spec_engine.py` | `types` |
| `workflow_engine.py` | `types` |
| `ooda_runtime.py` | `types` |
| `knowledge_layer.py` | `types` |
| `memory_layer.py` | `types` |
| `judge_engine.py` | `types` |
| `event_bus.py` | `types` |
| `judge/adapters/deepeval.py` | `types` |

---

## 4. Violation Check

| Rule | Status |
|------|--------|
| No circular imports | PASS |
| types imports nothing from core | PASS |
| subsystems import only from types | PASS |
| no subsystem imports another subsystem | PASS |
| project.py is integration point only | PASS |
| __init__.py is re-export only | PASS |

---

## 5. Notes

- `project.py` lives inside `types/` package — it's a type-level integration point, not a business logic module. It imports from sibling type modules only.
- `event_bus.py` imports only `Event` from types — it's a stub extension point.
- `judge/adapters/` is a sub-package for adapter implementations — imports only from types.
- All Level 1 modules are currently stubs (`raise NotImplementedError`). When real implementations are added, they may need to import from `errors.py` — this is allowed (same level).
