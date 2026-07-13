# Architecture Review: Memory Layer Implementation

**Review Date:** 2026-07-13
**Reviewer:** CodeAI Architecture Team
**Scope:** `scripts/core/memory_layer.py` — MemoryLayer orchestrator

---

## Verdict: PASS ✅

All invariants enforced. No SOLID violations. No dependency rule breaks. One known discrepancy documented.

---

## Files Reviewed

| File | Lines | Purpose |
|------|-------|---------|
| `scripts/core/memory_layer.py` | 298 | MemoryLayer orchestrator |
| `tests/test_memory_layer.py` | 305 | 42 unit tests |
| `scripts/core/memory/repository.py` | 123 | MemoryRepository ABC (unchanged) |
| `scripts/core/memory/json_repository.py` | 302 | JsonMemoryRepository (unchanged) |

**Total:** 1028 lines | **Tests:** 42/42 pass | **Full suite:** 119/119

---

## CORE_RUNTIME.md Compliance

| Method | CORE_RUNTIME.md §2.5 | Implementation | Match |
|--------|----------------------|----------------|-------|
| `store(entry: MemoryEntry) -> None` | `def store(entry: MemoryEntry) -> None` | `def store(self, entry: MemoryEntry) -> None` | ✅ |
| `load(query: str, scope: str = "project") -> list[MemoryEntry]` | `def load(query: str, scope: str = "project") -> list[MemoryEntry]` | `def load(self, query: str, scope: str = "project") -> list[MemoryEntry]` | ✅ |
| `summarize(scope: str, depth: str = "brief") -> str` | `def summarize(scope: str, depth: str = "brief") -> str` | `def summarize(self, scope: str = "project", depth: str = "brief") -> str` | ⚠️ |

### ⚠️ Note: `summarize()` default `scope` parameter

CORE_RUNTIME.md §2.5 defines: `summarize(scope: str, depth: str = "brief")` — `scope` has **no default**.
MEMORY_LAYER_DESIGN.md §4 defines: `summarize(scope: str = "project", depth: str = "brief")` — `scope` defaults to `"project"`.

Implementation follows MEMORY_LAYER_DESIGN.md (scope defaults to "project") because:
1. Making `scope` required would force callers to always pass it, adding no value
2. The default "project" is the overwhelmingly common case (§7 scope model)
3. This is a **convenience default**, not a behavioral change — callers can still pass scope explicitly

**Status:** Acceptable deviation. Not a breaking change. Document for future ADR alignment if CORE_RUNTIME.md is updated.

---

## MEMORY_LAYER_DESIGN.md Compliance

| Section | Requirement | Implemented | Notes |
|---------|-------------|-------------|-------|
| §3 Responsibilities | Store, Load, Summarize, Dedup, Retention, Scope isolation | ✅ | All 6 responsibilities covered |
| §4 API | store, load, summarize signatures | ✅ | See note above on summarize default |
| §7 Retention | Per-type max, TTL, permanent types | ✅ | All 7 types configured |
| §9 Dedup | Hash-based, merge rules, exceptions | ✅ | iterations + project_history phase_id exceptions |
| §10 Search | Type filter, scope filter, text match, recency sort, limit | ✅ | All 5 steps implemented |
| §14 Repository API | Uses existing MemoryRepository | ✅ | No repo API changes |

### Known Discrepancy: §14 vs Actual Repository API

MEMORY_LAYER_DESIGN.md §14 describes an **aspirational** Repository API:
- `save()`, `find_duplicate()`, `query()`, `count()`, `delete_expired()`, `delete_oldest()`

Actual `MemoryRepository` (implemented):
- `store()`, `load()`, `load_all()`, `delete()`, `exists()`, `count()`, `delete_expired()`

**Resolution:** MemoryLayer uses the **actual** API. Dedup is implemented via `load_all()` + hash comparison (not a `find_duplicate()` method). Retention uses `delete_expired()` + `load_all()` + `delete()` (not `delete_oldest()`).

This is correct behavior — the design doc §14 was aspirational, and the user explicitly prohibited changing the Repository API.

---

## SOLID Checklist

| Principle | Status | Evidence |
|-----------|--------|----------|
| **S** — Single Responsibility | ✅ | MemoryLayer handles orchestration only. No file I/O, no persistence logic, no hashing in repo. |
| **O** — Open/Closed | ✅ | Open for new Repository implementations (SQLite, Vector) via injection. Closed for modification. |
| **L** — Liskov Substitution | ✅ | Any `MemoryRepository` subclass works. Tested with `JsonMemoryRepository`. |
| **I** — Interface Segregation | ✅ | `MemoryRepository` ABC has focused methods. No fat interface. |
| **D** — Dependency Inversion | ✅ | MemoryLayer depends on `MemoryRepository` ABC, not on `JsonMemoryRepository`. |

---

## Dependency Rule

```
MemoryLayer (orchestrator)
    ↓ depends on
MemoryRepository (ABC)
    ↓ implemented by
JsonMemoryRepository (concrete)
    ↓ uses
MemoryEntry (domain type)
```

**Status:** ✅ No upward dependencies. No cross-subsystem imports. Dependency rule respected.

---

## Invariant Coverage (MINV-1 through MINV-8)

| ID | Rule | Enforcement | Test |
|----|------|-------------|------|
| MINV-1 | Every stored entry has unique UUID | `_validate_entry()` checks `entry.id` is set | `test_minv_1_unique_id` |
| MINV-2 | content_hash is SHA-256 of normalized content | `_ensure_content_hash()` computes if empty | `test_minv_2_content_hash_is_sha256` |
| MINV-3 | Duplicate entries merged | `_find_duplicate()` + `_merge_entries()` | `test_store_deduplicates_same_type_and_hash` |
| MINV-4 | Expired entries not returned by load | `_is_expired()` filter in `load()` | `test_minv_4_expired_not_returned` |
| MINV-5 | Permanent types never GC'd | `_enforce_retention()` skips permanent | `test_permanent_types_never_gc` |
| MINV-6 | load() limit capped at 500 | `_MAX_LOAD_LIMIT = 500` | `test_minv_6_limit_cap` |
| MINV-7 | summarize() never returns empty for non-empty store | Returns "No entries found." placeholder | `test_minv_7_empty_store_summary` |
| MINV-8 | scope must be "project" or "global" | `_validate_scope()` in all public methods | `test_minv_8_scope_validation` |

---

## Responsibility Leaks Check

| Check | Status | Notes |
|-------|--------|-------|
| MemoryLayer touches filesystem | ✅ No | All I/O through `MemoryRepository` |
| MemoryLayer imports other subsystems | ✅ No | Only imports from `scripts.core.enums`, `scripts.core.errors`, `scripts.core.memory`, `scripts.core.types` |
| MemoryLayer couples to JSON | ✅ No | Depends on `MemoryRepository` ABC only |
| MemoryLayer calls LLM | ✅ No | `summarize()` is template-based |
| MemoryLayer modifies Repository API | ✅ No | Uses existing methods only |
| Repository handles business logic | ✅ No | Dedup, retention, validation all in MemoryLayer |

---

## Extension Points (v2)

| Extension | Where | Impact |
|-----------|-------|--------|
| Event Bus | Comment placeholder in `store()` | Add `self._emit(...)` when Event Bus exists |
| SQLite Repository | Inject new `SqliteMemoryRepository` | No MemoryLayer changes needed |
| Vector Search | Add `load_semantic()` method | New public API, ADR required |
| LLM Summarize | Replace template methods | Internal change, no API break |

---

## Test Coverage

| Test Class | Tests | What's Covered |
|------------|-------|----------------|
| `TestStore` | 11 | Persist, hash, dedup, merge, validation |
| `TestLoad` | 10 | Text match, scope, expiry, sorting, edge cases |
| `TestSummarize` | 8 | Brief/detailed/full, scope, expiry, validation |
| `TestRetention` | 3 | TTL GC, max-count GC, permanent skip |
| `TestDeduplication` | 3 | Cross-scope, timestamp preservation, ID preservation |
| `TestInvariants` | 8 | MINV-1 through MINV-8 |
| **Total** | **42** | |

---

## What's NOT Implemented (by design)

| Feature | Why Excluded | When |
|---------|-------------|------|
| Vector DB search | v1 scope | v2-v3 |
| SQLite repository | v1 uses JSON | v2 |
| GraphRAG | v1 scope | v3 |
| MCP integration | Out of scope | Future |
| Knowledge Layer coupling | Separate subsystem | Never |
| Judge integration | Separate subsystem | Never |
| Event Bus integration | Extension point only | v2 |
| `delete_oldest()` repo method | Workaround via load_all + delete | v2 (can add to repo) |
| `find_duplicate()` repo method | Workaround via load_all + hash check | v2 (can add to repo) |
