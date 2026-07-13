# MEMORY_LAYER_REVIEW.md

**Date:** 2026-07-13  
**Scope:** Independent Architecture Review of MEMORY_LAYER_DESIGN.md  
**Reviewer:** Architecture Review (automated)  
**Version:** 1.0

---

## Executive Summary

**Architecture Score:** 8/10  
**API Stability:** 7/10  
**Extensibility:** 9/10  
**Risk Level:** MEDIUM

**Verdict:** CHANGES REQUIRED

---

## P0 Critical

None.

---

## P1 High

### P1-1: MemoryEntry Redefinition Violates Frozen Types

**Section:** §14 (API Contract)  
**Reference:** `scripts/core/types/memory.py`, CORE_RUNTIME.md §5 (line 516-522)  
**Issue:** The design defines a new `MemoryEntry` with fields `scope`, `content_hash`, `version` that do not exist in the frozen type at `types/memory.py:12-19`. The frozen type has `id: UUID, type: MemoryType, content: str, timestamp: datetime, metadata: dict`.

**Impact:** Violates frozen types rule. Two conflicting definitions will exist.

**Fix:** Extend the existing `MemoryEntry` in `types/memory.py` via ADR, or move the extended definition into `scripts/core/memory/entry.py` as a separate internal type (e.g., `MemoryRecord`) that wraps the frozen `MemoryEntry`.

---

### P1-2: store() Return Type Deviates from Frozen API

**Section:** §4 (External API)  
**Reference:** CORE_RUNTIME.md §2.5 (line 188)  
**Issue:** CORE_RUNTIME.md defines `store(entry: MemoryEntry) -> None`. The design changes this to `store(entry: MemoryEntry) -> MemoryEntry`.

**Impact:** Frozen API violation. Existing callers expecting `None` will not break (return value ignorable), but the contract is changed.

**Fix:** Keep `store() -> None` in the frozen API. Use an output parameter or separate method (`store_and_return()`) for callers needing the assigned ID. Alternatively, document this as a deliberate API evolution requiring ADR.

---

## P2 Medium

### P2-1: load() Signature Extends Frozen API Without ADR

**Section:** §4 (External API)  
**Reference:** CORE_RUNTIME.md §2.5 (line 191)  
**Issue:** CORE_RUNTIME.md defines `load(query: str, scope: str = "project") -> list[MemoryEntry]`. The design adds `memory_type: MemoryType | None = None` and `limit: int = 50`.

**Impact:** Frozen API extension without ADR. Backward-compatible (new params have defaults), but technically a contract change.

**Fix:** Document as deliberate extension in ADR-0002, or keep the frozen signature and implement filtering/limiting inside the method (load all, filter in MemoryLayer).

---

### P2-2: InMemoryMemoryRepository Contradicts TECH_STACK.md

**Section:** §11 (Storage Format)  
**Reference:** TECH_STACK.md (line 17)  
**Issue:** TECH_STACK.md states Memory Layer technology is "JSON + SQLite". The design lists `InMemoryMemoryRepository` as v1 default, which has no persistence across restarts.

**Impact:** Technology mismatch with frozen tech stack.

**Fix:** Make `JsonMemoryRepository` the v1 default. `InMemoryMemoryRepository` should be test-only (not listed as v1 default).

---

### P2-3: summarize() Implementation Vague

**Section:** §4 (External API)  
**Issue:** The docstring says "Internally calls the most relevant entries and produces a text summary." It is unclear whether this uses an LLM, concatenation, or template-based approach.

**Impact:** Implementation ambiguity. If LLM is required, Memory Layer gains an external dependency.

**Fix:** Specify: v1 uses template-based summarization (count per type, list recent entries). LLM-based summarization is a future extension.

---

### P2-4: GC on Every store() May Be Expensive

**Section:** §8 (Deletion Policy)  
**Issue:** "Runs on every `store()` call (amortized)." For high-frequency stores, this adds latency to every write.

**Impact:** Performance risk under load.

**Fix:** Change to: "Runs lazily — triggered when entry count exceeds threshold (e.g., 100 over max). Not on every store()."

---

## P3 Low

### P3-1: memory.loaded Event Not Defined in EVENTS.md

**Section:** §17 (Future Extensions)  
**Reference:** EVENTS.md §3.6  
**Issue:** EVENTS.md defines `memory.stored` event but not `memory.loaded`. The design references `memory.loaded` as a future event.

**Impact:** Minor documentation gap.

**Fix:** Add `memory.loaded` event definition to EVENTS.md, or remove reference from design.

---

### P3-2: No Validation That scope Is "project" or "global"

**Section:** §4 (External API)  
**Issue:** `load()` accepts `scope: str` with no validation that it is one of the allowed values.

**Impact:** Typos (e.g., `scope="projcet"`) silently return empty results.

**Fix:** Add invariant: scope must be "project" or "global". Reject invalid values with `MEM_INVALID_ENTRY`.

---

### P3-3: content_hash field in MemoryEntry Is Implementation Detail

**Section:** §14 (API Contract)  
**Issue:** `content_hash` is an internal implementation detail for deduplication. Exposing it in the public `MemoryEntry` type leaks implementation.

**Impact:** Minor API pollution.

**Fix:** Remove `content_hash` from public `MemoryEntry`. Compute and store it internally in `MemoryIndex` or repository.

---

## Positive Findings

### 1. Clear Boundary Separation

§3 (Responsibilities) explicitly lists what Memory Layer does and does not do. No responsibility leaks detected.

### 2. Repository Pattern Correctly Applied

MemoryLayer → MemoryRepository (abstract) → JsonMemoryRepository / SqliteMemoryRepository. Backend swap requires zero changes to MemoryLayer.

### 3. Deduplication Policy Is Well-Defined

§9 (Deduplication Policy) covers detection (hash-based), merge rules, and exceptions (iterations, project_history with different phase_id).

### 4. Invariants Are Enforceable

MINV-1 through MINV-7 are concrete, testable rules with clear enforcement points.

### 5. Error Hierarchy Correct

All errors use `MemoryError(CodeAIError)` with stable codes (`MEM_STORE_FAILED`, etc.). Follows existing pattern from WorkflowEngine.

### 6. Future Extensions Are Non-Breaking

SQLite, Vector DB, event emission — all are repository implementations or optional callbacks. No API changes required.

### 7. Standalone Usage Possible

Memory Layer has no imports from other subsystems. Can be used independently.

---

## Recommendation

**CHANGES REQUIRED** — 2 high issues, 4 medium issues.

**Required before implementation:**
1. Resolve MemoryEntry frozen type conflict (P1-1)
2. Resolve store() return type deviation (P1-2)
3. Align with TECH_STACK.md technology (P2-2)
4. Clarify summarize() implementation (P2-3)

**Can be addressed during implementation:**
- P2-1: Document as ADR or refactor
- P2-4: Adjust GC strategy
- P3-1 through P3-3: Minor fixes
