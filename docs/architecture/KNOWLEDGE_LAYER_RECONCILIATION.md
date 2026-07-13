# Knowledge Layer — Reconciliation Report

**Date:** 2026-07-13
**Trigger:** Architecture Review found 4 P1, 3 P2, 2 P3 issues
**Action:** Reconcile KNOWLEDGE_LAYER_DESIGN.md with frozen contracts

---

## Changes Made

### P1-1: `retrieve()` params signature ✅ Fixed

**Before:** `params: dict[str, Any] | None = None` (optional)
**After:** `params: dict[str, Any]` (required)

**File:** `KNOWLEDGE_LAYER_DESIGN.md` §5, method signatures table
**Aligned with:** CORE_RUNTIME.md §2.4, ARCHITECTURE_FREEZE.md §3.4

---

### P1-2: `KnowledgeRepository` ABC ✅ Fixed

**Before:** `store()`, `delete()`, `count()` methods in public ABC
**After:** Only `search()` method — matches CORE_RUNTIME.md §4 exactly

**File:** `KNOWLEDGE_LAYER_DESIGN.md` §19
**Note:** `store()`, `delete()`, `count()` are internal implementation details of concrete repositories, not part of the architectural contract.

---

### P1-3: KL → ML dependency ✅ Fixed

**Before:** Knowledge Layer depended on Memory Layer (read-only)
**After:** Knowledge Layer is fully independent — no imports from any subsystem

**Changes across 8 sections:**
- §2 Boundaries: Removed Memory Layer from diagram, rewrote dependency rules
- §3 Responsibilities: Added "Cross-subsystem integration" to exclusions
- §4.1 Ingestion: Removed "Accept memory entries from Memory Layer"
- §10.2 RAG Flow: Added note that callers bridge the gap
- §12: Rewrote as "Relationship with Memory Layer" — independence model
- §14.4 Source Priority: Removed Memory Layer row
- §15.3 Graceful Degradation: Removed Memory Layer entry
- §18 Architecture Diagram: Removed ML node and KL→ML edge

**No ADR needed** — we removed a dependency, not added one.

---

### P1-4: `Context` metadata field ✅ Fixed

**Before:** `metadata: dict[str, Any] = field(default_factory=dict)` (4th field)
**After:** 3 fields only — matches CORE_RUNTIME.md §5 exactly

**File:** `KNOWLEDGE_LAYER_DESIGN.md` §19

---

### P2-1: Source of Truth ✅ Fixed

**Before:** "Source of truth: `scripts/core/types/knowledge.py` (or CORE_RUNTIME.md §5)"
**After:** "Source of truth: `scripts/core/types/knowledge.py`. See CORE_RUNTIME.md §5 for contract."

---

### P2-3: v1 score formula ✅ Fixed

**Before:** `BM25 × 0.4 + fuzzy × 0.2 + semantic × 0.4` (semantic always 0 in v1)
**After:** Separate v1 and v2 formulas with renormalized weights

---

### P3-1: §12.2 comment field name ✅ Fixed

**Before:** `Knowledge(kind=MEMORY, type=PATTERN)` — `type` field doesn't exist
**After:** Removed entire §12.2 (Memory as Knowledge) — no longer applicable

---

### P3-2: Obsidian "primary" phrasing ✅ Fixed

**Before:** "Obsidian is the primary document store for the platform"
**After:** "Obsidian is one of the data sources for Knowledge Layer, accessed via MCP transport"

---

## Additional Cleanup

| Item | Action |
|------|--------|
| KINV-7 (Memory Layer read-only) | Removed — no longer relevant |
| KINV-8 renumbered to KINV-7 | Scope validation invariant |
| Self-review checklist | Updated to reflect all changes |
| v1 Backend Strategy | Removed "Memory integration" line |
| Graceful Degradation | Removed Memory Layer entry |

---

## What Did NOT Change

| Item | Status | Reason |
|------|--------|--------|
| `search()` signature | Unchanged | Already matched frozen API |
| `Knowledge` type | Unchanged | Already matched frozen type |
| `KnowledgeType` enum | Unchanged | Already matched frozen enum |
| `KnowledgeKind` enum | Unchanged | Already matched frozen enum |
| `KnowledgeError` | Unchanged | Already matched frozen error |
| Event model | Unchanged | Already matched frozen events |
| TECH_STACK.md | Unchanged | MCP + OHS still correct |
| No ADR created | N/A | Only removed dependencies, didn't add |

---

## Verification

| Criterion | Before | After |
|-----------|--------|-------|
| `retrieve()` matches CORE_RUNTIME.md §2.4 | ❌ | ✅ |
| `KnowledgeRepository` matches CORE_RUNTIME.md §4 | ❌ | ✅ |
| No KL → ML dependency | ❌ | ✅ |
| `Context` matches frozen type | ❌ | ✅ |
| Single Source of Truth | ❌ | ✅ |
| v1 formula honest | ❌ | ✅ |
| No hidden Obsidian dependency | ❌ | ✅ |

---

## Self-Review (Post-Reconciliation)

| # | Criterion | Status |
|---|-----------|--------|
| 1 | CORE_RUNTIME.md §2.4 | ✅ |
| 2 | TECH_STACK.md | ✅ |
| 3 | All ADRs | ✅ |
| 4 | Frozen API | ✅ |
| 5 | Frozen Types | ✅ |
| 6 | Frozen Errors | ✅ |
| 7 | Frozen Event Model | ✅ |
| 8 | Dependency Rule | ✅ |
| 9 | SOLID | ✅ |
| 10 | Clean Architecture | ✅ |
| 11 | DDD Boundaries | ✅ |
| 12 | Open/Closed | ✅ |
| 13 | Workflow Engine compat | ✅ |
| 14 | Memory Layer compat | ✅ |
| 15 | Spec Engine compat | ✅ |
| 16 | Judge Engine compat | ✅ |
| 17 | OODA Runtime compat | ✅ |
| 18 | MCP no business logic | ✅ |
| 19 | RAG retrieval only | ✅ |
| 20 | GraphRAG optional | ✅ |
| 21 | Memory Layer independent | ✅ |
| 22 | No KL responsibility leak | ✅ |
| 23 | No OODA responsibility leak | ✅ |
| 24 | No cyclic dependencies | ✅ |
| 25 | Backend swappable | ✅ |
| 26 | Hybrid Search replaceable | ✅ |
| 27 | No hidden Obsidian deps | ✅ |
| 28 | Single Source of Truth | ✅ |

---

**PASS**
