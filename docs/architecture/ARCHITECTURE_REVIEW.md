# ARCHITECTURE_REVIEW.md — Architectural Audit

**Date:** 2026-07-12
**Reviewer:** Principal Software Architect
**Scope:** Full architecture compliance audit
**Status:** COMPLETE — No code changes made

---

## 1. Executive Summary

| Metric | Score |
|--------|-------|
| **Architecture Score** | **6.5 / 10** |
| Compliance with CORE_RUNTIME.md | 6/10 |
| Compliance with ARCHITECTURE_FREEZE.md | 5/10 |
| Compliance with TECH_STACK.md | 8/10 |
| Subsystem Boundary Respect | 9/10 |
| Clean Architecture | 8/10 |

**Verdict:** The implementation has **significant architectural drift** from the frozen contracts. While the core principles are sound (low coupling, clean dependency direction), the actual code diverges from the documented API in multiple places. This requires an ADR to reconcile.

---

## 2. Violations Found

### 2.1 P0 — Critical (API Contract Violations)

#### V-001: WorkflowEngine Method Names Don't Match Frozen API

| Document | Method | Actual Implementation |
|----------|--------|----------------------|
| ARCHITECTURE_FREEZE.md §3.2 | `next()` | `next_phase()` |
| ARCHITECTURE_FREEZE.md §3.2 | `complete()` | `complete_phase()` |

**Evidence:**
- `ARCHITECTURE_FREEZE.md:49-51` defines `next()`, `complete()`
- `workflow_engine.py:202` defines `next_phase()`, `workflow_engine.py:238` defines `complete_phase()`

**Impact:** Any code written against the frozen API will break. This is a breaking change that requires ADR.

**Fix:** Either rename methods to match frozen API, or create ADR to update the frozen API.

---

#### V-002: JudgeEngine Has Extra Parameter Not in Frozen API

| Document | Signature | Actual Implementation |
|----------|-----------|----------------------|
| ARCHITECTURE_FREEZE.md §3.6 | `evaluate(response: str, context: str, spec: str)` | `evaluate(response: str, context: str = "", spec: str = "", acceptance_criteria: list[str] \| None = None)` |

**Evidence:**
- `ARCHITECTURE_FREEZE.md:80` defines 3 parameters
- `judge_engine.py:159-164` defines 4 parameters (extra `acceptance_criteria`)

**Impact:** Adding parameters to a frozen API is a breaking change. Callers using positional arguments will break.

**Fix:** Create ADR to add `acceptance_criteria` parameter, or move AC checking to a separate method.

---

#### V-003: WorkflowEngine Has Extra Methods Not in Frozen API

| Extra Method | Location | Purpose |
|-------------|----------|---------|
| `load()` | `workflow_engine.py:78` | Load state from repository |
| `save()` | `workflow_engine.py:108` | Save state to repository |
| `current_phase()` | `workflow_engine.py:230` | Get active phase |
| `current_task()` | `workflow_engine.py:371` | Get active task |
| `start_task()` | `workflow_engine.py:379` | Start a task |
| `complete_task()` | `workflow_engine.py:427` | Complete a task |
| `fail_task()` | `workflow_engine.py:462` | Mark task as failed |
| `status()` | `workflow_engine.py:499` | Get workflow status |

**Evidence:** ARCHITECTURE_FREEZE.md §3.2 defines only 4 methods: `start`, `next`, `complete`, `rollback`.

**Impact:** These methods are not part of the frozen contract. They may be useful, but they weren't approved.

**Fix:** Create ADR to add these methods to the frozen API.

---

### 2.2 P1 — High (Type/Enum Violations)

#### V-004: WorkflowSnapshot and RollbackEntry Not in Frozen Types

**Evidence:**
- `types/workflow.py:50-83` defines `RollbackEntry` and `WorkflowSnapshot`
- ARCHITECTURE_FREEZE.md §4 lists 23 dataclasses — neither is included

**Impact:** These types are used by the Repository Pattern and WorkflowEngine persistence, but they aren't part of the frozen contract.

**Fix:** Create ADR to add these types to the frozen contract.

---

#### V-005: WorkflowStatus Enum Not in Frozen Enums

**Evidence:**
- `enums.py:77-84` defines `WorkflowStatus` with values: IDLE, RUNNING, PAUSED, COMPLETED, FAILED, ROLLING_BACK
- ARCHITECTURE_FREEZE.md §5 lists 8 enums — `WorkflowStatus` is not included

**Impact:** This enum is used by `WorkflowSnapshot` and `WorkflowEngine.status()`, but it isn't part of the frozen contract.

**Fix:** Create ADR to add `WorkflowStatus` to the frozen contract.

---

#### V-006: RepositoryError Not in Frozen Error Hierarchy

**Evidence:**
- `repositories/json_repo.py:240-268` defines `RepositoryError` as a standalone exception
- ARCHITECTURE_FREEZE.md §Error Handling defines 6 error types — `RepositoryError` is not included

**Impact:** This error doesn't inherit from `CodeAIError`, breaking the unified error hierarchy.

**Fix:** Either make `RepositoryError` inherit from `CodeAIError`, or create ADR for a separate error hierarchy.

---

### 2.3 P2 — Medium (Structural Violations)

#### V-007: Repository Pattern Not in Architecture Docs

**Evidence:**
- `scripts/core/repositories/` package exists with `WorkflowRepository` ABC and `JsonWorkflowRepository`
- Neither CORE_RUNTIME.md nor ARCHITECTURE_FREEZE.md mentions repositories

**Impact:** This is a significant architectural addition that wasn't part of the original design. It introduces persistence concerns into the core runtime.

**Fix:** Create ADR to document the Repository Pattern as part of the architecture.

---

#### V-008: Cross-Type Dependency (workflow.py → judge.py)

**Evidence:**
- `types/workflow.py:12` imports `from scripts.core.types.judge import Verdict`
- `WorkflowSnapshot.judge_verdict: Verdict | None` uses this import
- DEPENDENCY_GRAPH.md §4 states "No circular imports" and "types imports nothing from core"

**Impact:** This creates a dependency from workflow domain to judge domain within the types layer. While not circular, it violates the principle of isolated bounded contexts.

**Fix:** Either remove the dependency (use `Any` or a forward reference), or document this as an intentional integration point.

---

### 2.4 P3 — Low (Technology Violations)

#### V-009: TECH_STACK.md Says python-statemachine, Implementation Is Custom

**Evidence:**
- `TECH_STACK.md:14` states "Workflow Engine | python-statemachine | v3.x"
- `workflow_engine.py` is a custom implementation (553 lines)

**Impact:** Minor documentation inconsistency. The custom implementation is simpler and has fewer dependencies.

**Fix:** Update TECH_STACK.md to reflect the actual implementation.

---

## 3. Subsystem Boundary Respect

| Check | Status | Evidence |
|-------|--------|----------|
| Engine → Engine imports | ✅ PASS | No engine imports another engine |
| Type → Engine imports | ✅ PASS | No type imports an engine |
| Foundation → Domain imports | ✅ PASS | `enums.py`, `errors.py` don't import types |
| Domain → Foundation imports | ✅ PASS | `types/*` imports only `enums`, `serialization` |
| ProjectContext as integration point | ✅ PASS | Aggregates all subsystem types |

**Boundary Violation:**
- `types/workflow.py` imports from `types/judge.py` (V-008) — cross-domain dependency within types layer

---

## 4. Hidden Coupling

| Coupling | Location | Impact |
|----------|----------|--------|
| WorkflowEngine → WorkflowRepository | `workflow_engine.py:19` | Engine depends on persistence abstraction not in frozen API |
| WorkflowSnapshot → ProjectContext | `types/workflow.py:92` | Lazy import to avoid circular dependency |
| JsonWorkflowRepository → WorkflowSnapshot | `repositories/json_repo.py:14` | Repository depends on type not in frozen contract |
| JudgeEngine → re module | `judge_engine.py:12` | Internal implementation detail (acceptable) |

---

## 5. Responsibility Violations

| Module | Assigned Responsibility | Actual Responsibility | Violation? |
|--------|------------------------|----------------------|------------|
| WorkflowEngine | State machine only | State machine + persistence (load/save) | ⚠️ Minor |
| JudgeEngine | Evaluation + routing | Evaluation + routing + scoring helpers | ✅ Acceptable |
| Repository | Not in architecture | Persistence abstraction | ⚠️ Addition |
| Types | Data definitions only | Data definitions + serialization | ✅ Acceptable |

---

## 6. Clean Architecture Compliance

### Layers (as designed)

```
┌─────────────────────────────────┐
│  Frameworks & Drivers (shell)   │  ← scripts/build-loop/
├─────────────────────────────────┤
│  Interface Adapters (engines)   │  ← *_engine.py + repositories/
├─────────────────────────────────┤
│  Domain (types)                 │  ← types/*.py
├─────────────────────────────────┤
│  Use Cases (serialization)      │  ← serialization.py
├─────────────────────────────────┤
│  Entities (enums, errors)       │  ← enums.py, errors.py
└─────────────────────────────────┘
```

### Actual Layers

```
┌─────────────────────────────────┐
│  Frameworks & Drivers (shell)   │  ← scripts/build-loop/
├─────────────────────────────────┤
│  Interface Adapters             │  ← *_engine.py
├─────────────────────────────────┤
│  Persistence (repositories/)    │  ← NEW: not in original design
├─────────────────────────────────┤
│  Domain (types)                 │  ← types/*.py
├─────────────────────────────────┤
│  Use Cases (serialization)      │  ← serialization.py
├─────────────────────────────────┤
│  Entities (enums, errors)       │  ← enums.py, errors.py
└─────────────────────────────────┘
```

**Observation:** The Repository Pattern adds a new layer that wasn't in the original Clean Architecture diagram. This is a reasonable addition for persistence, but it should be documented.

---

## 7. Risks

| Risk | Severity | Likelihood | Mitigation |
|------|----------|------------|------------|
| API drift causes integration failures | HIGH | HIGH | Create ADR to reconcile API |
| Repository Pattern becomes god object | MEDIUM | LOW | Monitor size, enforce single responsibility |
| Cross-type dependencies proliferate | MEDIUM | MEDIUM | Enforce dependency rules in CI |
| Frozen contract loses credibility | HIGH | HIGH | Follow ADR process for all changes |

---

## 8. Recommended Fixes

### Immediate (Before Next Implementation)

1. **Create ADR-0002** to reconcile WorkflowEngine API:
   - Option A: Rename `next_phase()` → `next()`, `complete_phase()` → `complete()`
   - Option B: Update frozen API to include new method names

2. **Create ADR-0003** to add Repository Pattern to architecture:
   - Document `WorkflowRepository` ABC
   - Document `JsonWorkflowRepository`
   - Add `RepositoryError` to error hierarchy

3. **Create ADR-0004** to add missing types/enums:
   - Add `WorkflowSnapshot`, `RollbackEntry` to frozen types
   - Add `WorkflowStatus` to frozen enums

### Short-Term (Before v1.0)

4. **Resolve cross-type dependency** (V-008):
   - Option A: Use `Any` type for `judge_verdict` field
   - Option B: Document this as intentional integration point

5. **Update TECH_STACK.md** (V-009):
   - Change Workflow Engine technology from "python-statemachine" to "Custom Python"

6. **Make RepositoryError inherit from CodeAIError** (V-006):
   - Ensure unified error hierarchy

### Long-Term (v2.0+)

7. **Consider Protocol types** for engine interfaces:
   - Add `typing.Protocol` classes for formal interface contracts
   - Enable static type checking across subsystem boundaries

8. **Add CI architecture checks**:
   - Detect cross-type dependencies
   - Verify frozen API compliance
   - Monitor module sizes

---

## 9. Summary

The CodeAI architecture is **fundamentally sound** with clean dependency direction, low coupling, and good subsystem separation. However, the implementation has **drifted significantly** from the frozen contracts:

- **3 P0 violations** (API contract mismatches)
- **3 P1 violations** (missing types/enums in frozen contract)
- **2 P2 violations** (structural additions not in architecture)
- **1 P3 violation** (documentation inconsistency)

**Total: 9 violations** across 4 severity levels.

The primary issue is that the implementation evolved faster than the documentation. The Repository Pattern, extra WorkflowEngine methods, and JudgeEngine's `acceptance_criteria` parameter are all reasonable additions, but they weren't approved through the ADR process.

**Recommendation:** Create ADRs to reconcile the implementation with the architecture, then enforce the frozen contract through CI checks.

---

## 10. Appendix: Verification Checklist

| Check | Status | Evidence |
|-------|--------|----------|
| All engine stubs match ARCHITECTURE_FREEZE.md | ❌ FAIL | V-001, V-002, V-003 |
| All dataclasses match ARCHITECTURE_FREEZE.md | ❌ FAIL | V-004 |
| All enums match ARCHITECTURE_FREEZE.md | ❌ FAIL | V-005 |
| Error hierarchy matches ARCHITECTURE_FREEZE.md | ❌ FAIL | V-006 |
| No contradictions between docs | ⚠️ PARTIAL | V-009 |
| `types/__init__.py` exports match contract | ✅ PASS | 31 exports verified |
| No engine-to-engine imports | ✅ PASS | Verified in code |
| No circular imports | ✅ PASS | Verified in code |
| Dependency direction is clean | ✅ PASS | Foundation → Domain → Engines |

---

*Review completed. No files were modified.*
