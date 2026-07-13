# Architecture Review: Knowledge Layer Design

**Review Date:** 2026-07-13
**Reviewer:** Independent Architecture Audit
**Scope:** `docs/architecture/KNOWLEDGE_LAYER_DESIGN.md` vs all frozen contracts

---

# Executive Summary

**Architecture Score:** 7/10
**API Stability:** 6/10
**Extensibility:** 9/10
**Risk Level:** MEDIUM

**Verdict: CHANGES REQUIRED**

---

## Criteria Audit (28 points)

| # | Criterion | Status | Notes |
|---|-----------|--------|-------|
| 1 | CORE_RUNTIME.md §2.4 | ⚠️ | `retrieve()` params signature changed |
| 2 | TECH_STACK.md | ✅ | MCP + Obsidian + OHS matches |
| 3 | All ADRs | ✅ | ADR-0001 "passive knowledge provider" matches |
| 4 | Frozen API | ⚠️ | `retrieve()` params: required → optional |
| 5 | Frozen Types | ⚠️ | `Context` gains `metadata` field; `KnowledgeRepository` gains methods |
| 6 | Frozen Errors | ✅ | `KnowledgeError(CodeAIError)` correct |
| 7 | Frozen Event Model | ✅ | `knowledge.requested`, `knowledge.retrieved` correct |
| 8 | Dependency Rule | ⚠️ | KL → ML dependency not in original architecture |
| 9 | SOLID | ✅ | All 5 principles respected |
| 10 | Clean Architecture | ⚠️ | Cross-layer dependency KL → ML |
| 11 | DDD Boundaries | ⚠️ | Bounded context coupling KL ↔ ML |
| 12 | Open/Closed | ✅ | New backends without modification |
| 13 | Workflow Engine compat | ✅ | No coupling |
| 14 | Memory Layer compat | ⚠️ | Read-only but creates dependency |
| 15 | Spec Engine compat | ✅ | No reverse coupling |
| 16 | Judge Engine compat | ✅ | No reverse coupling |
| 17 | OODA Runtime compat | ✅ | No reverse coupling |
| 18 | MCP no business logic | ✅ | Transport only |
| 19 | RAG retrieval only | ✅ | Generation is caller's job |
| 20 | GraphRAG optional | ✅ | v1 fallback documented |
| 21 | Memory Layer read-only | ✅ | No write methods called |
| 22 | No KL responsibility leak | ✅ | Exclusions listed |
| 23 | No OODA responsibility leak | ✅ | No OODA imports in KL |
| 24 | No cyclic dependencies | ✅ | KL → ML one-way only |
| 25 | Backend swappable | ✅ | MCP → API → Local documented |
| 26 | Hybrid Search replaceable | ✅ | Behind SearchIndex abstraction |
| 27 | No hidden Obsidian deps | ⚠️ | "Primary document store" in §8.1 |
| 28 | Single Source of Truth | ⚠️ | §19: "types/knowledge.py (or CORE_RUNTIME.md §5)" |

---

## P1 High — Must Fix Before Implementation

### P1-1: `retrieve()` params signature changed from required to optional

**File:** `docs/architecture/KNOWLEDGE_LAYER_DESIGN.md` §5
**Section:** Public API — Method Signatures (frozen)
**Frozen contract:** CORE_RUNTIME.md §2.4, ARCHITECTURE_FREEZE.md §3.4

**Evidence:**

CORE_RUNTIME.md §2.4:
```python
def retrieve(context_type: KnowledgeType, params: dict[str, Any]) -> Context:
```

DESIGN §5:
```python
def retrieve(
    self,
    context_type: KnowledgeType,
    params: dict[str, Any] | None = None,  # ← changed to optional
) -> Context:
```

**Problem:** `params` is a required parameter in the frozen API. Making it optional changes the contract. Existing callers that don't pass `params` would break if the implementation expects it.

**Minimum fix:** Revert to `params: dict[str, Any]` (required). Callers who don't need filtering can pass `{}`.

---

### P1-2: `KnowledgeRepository` ABC adds methods not in CORE_RUNTIME.md §4

**File:** `docs/architecture/KNOWLEDGE_LAYER_DESIGN.md` §19
**Section:** API Contracts — KnowledgeRepository (abstract)
**Frozen contract:** CORE_RUNTIME.md §4

**Evidence:**

CORE_RUNTIME.md §4 defines `KnowledgeRepository` with ONE method:
```python
class KnowledgeRepository(Repository[list[Knowledge]]):
    @abstractmethod
    def search(self, query: str, kind: str | None = None) -> list[Knowledge]:
```

DESIGN §19 adds THREE new methods:
```python
class KnowledgeRepository(Repository[list[Knowledge]]):
    @abstractmethod
    def search(...)  # exists in frozen API ✅
    
    @abstractmethod
    def store(...)   # NEW — not in frozen API ⚠️
    
    @abstractmethod
    def delete(...)  # NEW — signature differs from base ⚠️
    
    @abstractmethod
    def count(...)   # NEW — not in frozen API ⚠️
```

**Problems:**
1. `store()` is not in the frozen `KnowledgeRepository` interface
2. `delete(knowledge_id: str) -> bool` signature conflicts with base `Repository.delete() -> None`
3. `count()` is not in the frozen interface
4. Base class `save()` method is not overridden — naming inconsistency (`store` vs `save`)

**Minimum fix:** Remove `store`, `delete`, `count` from the DESIGN's `KnowledgeRepository`. Use the frozen interface from CORE_RUNTIME.md §4. If additional methods are needed, create an ADR.

---

### P1-3: KL → ML dependency not in original architecture

**File:** `docs/architecture/KNOWLEDGE_LAYER_DESIGN.md` §12
**Section:** Integration with Memory Layer
**Frozen contract:** CORE_RUNTIME.md §1 (architecture diagram), ADR-0001

**Evidence:**

CORE_RUNTIME.md §1 diagram shows:
```
OR <-->|context| KL[Knowledge Layer]
OR <-->|history| ML[Memory Layer]
```

No arrow between KL and ML. They are independent subsystems.

DESIGN §12 introduces:
```
Knowledge Layer → Memory Layer (read-only)
```

And §12.3:
```python
class KnowledgeLayer:
    def __init__(self, memory_layer: MemoryLayer):
        self._memory = memory_layer
```

**Problem:** This creates a new dependency (KL → ML) that doesn't exist in the frozen architecture. ADR-0001 states "Knowledge separation: Knowledge Layer (passive) vs Memory Layer (active) — clean domain model." Coupling them violates this principle.

**Minimum fix:** Either:
1. Remove KL → ML dependency entirely (preferred — keeps subsystems independent), OR
2. Create an ADR documenting this dependency and its rationale

---

### P1-4: `Context` type gains `metadata` field not in frozen definition

**File:** `docs/architecture/KNOWLEDGE_LAYER_DESIGN.md` §19
**Section:** API Contracts — Context
**Frozen contract:** CORE_RUNTIME.md §5, ARCHITECTURE_FREEZE.md §4

**Evidence:**

CORE_RUNTIME.md §5:
```python
@dataclass
class Context:
    context_type: KnowledgeType
    items: list[Knowledge]
    summary: str
```

DESIGN §19:
```python
@dataclass
class Context:
    context_type: KnowledgeType
    items: list[Knowledge]
    summary: str
    metadata: dict[str, Any] = field(default_factory=dict)  # NEW
```

Actual `types/knowledge.py` (3 fields, no metadata):
```python
@dataclass
class Context(Serializable):
    context_type: KnowledgeType
    items: list[Knowledge] = field(default_factory=list)
    summary: str = ""
```

**Problem:** `Context` is listed in ARCHITECTURE_FREEZE.md §4 as an approved mutable dataclass with exactly 3 fields. Adding `metadata` changes the approved definition. While backward-compatible (default value), it requires an ADR per ARCHITECTURE_FREEZE.md §7.

**Minimum fix:** Remove `metadata` from `Context`. Store quality signals in a separate internal dataclass (e.g., `_SearchResult`) that doesn't leak to the public API.

---

## P2 Medium — Should Fix

### P2-1: Source of Truth ambiguity

**File:** `docs/architecture/KNOWLEDGE_LAYER_DESIGN.md` §19
**Section:** API Contracts — Knowledge (frozen dataclass)

**Evidence:**
```python
# Source of truth: scripts/core/types/knowledge.py (or CORE_RUNTIME.md §5)
```

**Problem:** "or" creates ambiguity. There must be ONE source of truth.

**Minimum fix:** Pick one. Recommend: `scripts/core/types/knowledge.py` (code is truth, docs describe it).

---

### P2-2: `store` vs `save` naming inconsistency

**File:** `docs/architecture/KNOWLEDGE_LAYER_DESIGN.md` §19
**Section:** API Contracts — KnowledgeRepository

**Evidence:** Base `Repository[T]` uses `save()`. DESIGN uses `store()`.

**Problem:** Inconsistent with the base class contract.

**Minimum fix:** Use `save()` if extending the base Repository, or document why `store()` is preferred (requires ADR).

---

### P2-3: v1 score formula includes semantic weight (always 0)

**File:** `docs/architecture/KNOWLEDGE_LAYER_DESIGN.md` §9.5
**Section:** Hybrid Search — Score Combination

**Evidence:**
```
final_score = BM25_score × 0.4 + fuzzy_score × 0.2 + semantic_score × 0.4
```

v1: `semantic_score = 0` always.

**Problem:** 40% of the score formula is dead code in v1. Misleading for implementers.

**Minimum fix:** Document v1 formula separately: `final_score = BM25 × 0.67 + fuzzy × 0.33` (renormalized). Keep full formula in v2 section.

---

## P3 Low — Nice to Have

### P3-1: §12.2 comment uses wrong field name

**File:** `docs/architecture/KNOWLEDGE_LAYER_DESIGN.md` §12.2
**Section:** Memory as Knowledge

**Evidence:**
```python
# Knowledge Layer indexes it as Knowledge(kind=MEMORY, type=PATTERN)
```

`Knowledge` doesn't have a `type` field. Should be `kind=MEMORY` only.

**Minimum fix:** `Knowledge(kind=MEMORY, ...)` — remove `type=PATTERN`.

---

### P3-2: Obsidian "primary document store" phrasing

**File:** `docs/architecture/KNOWLEDGE_LAYER_DESIGN.md` §8.1
**Section:** Obsidian Integration — Why Obsidian

**Evidence:** "Obsidian is the primary document store for the platform."

**Problem:** If Obsidian is the ONLY source in v1, the MCP abstraction is theoretical. Phrasing suggests a hard dependency.

**Minimum fix:** Rephrase to: "Obsidian is one of the data sources, accessed via MCP transport."

---

## Findings Summary

| Severity | Count | IDs |
|----------|-------|-----|
| P0 Critical | 0 | — |
| P1 High | 4 | P1-1, P1-2, P1-3, P1-4 |
| P2 Medium | 3 | P2-1, P2-2, P2-3 |
| P3 Low | 2 | P3-1, P3-2 |

---

## What's Correct (no issues)

- ✅ SOLID — all 5 principles
- ✅ Dependency Rule — no reverse imports
- ✅ No cyclic dependencies
- ✅ MCP is transport only, no business logic
- ✅ RAG is retrieval only
- ✅ GraphRAG is fully optional (v2)
- ✅ Memory Layer is read-only
- ✅ No responsibility leaks in KL, OODA, or other subsystems
- ✅ Backend swappable (MCP → API → Local)
- ✅ Hybrid Search replaceable
- ✅ Error hierarchy correct (KnowledgeError → CodeAIError)
- ✅ Event model correct (knowledge.requested, knowledge.retrieved)
- ✅ Invariants documented (KINV-1–8)
- ✅ Sequence diagrams correct
- ✅ Mermaid architecture diagram correct
- ✅ TECH_STACK.md alignment
- ✅ ADR-0001 alignment (passive provider)

---

## Recommendation

Fix P1-1 through P1-4 before starting implementation. P1-3 (KL → ML dependency) is the most architecturally significant — it should either be removed or documented via ADR.

---

**CHANGES REQUIRED**
