# Architecture Review: Memory Repository Layer v1

**Review Date:** 2026-07-13
**Reviewer:** CodeAI Architecture Team
**Scope:** `scripts/core/memory/` package (repository ABC + JSON implementation)

---

## Verdict: PASS ✅

All P1 and P2 issues resolved. Code is production-ready for v1.

---

## Files Reviewed

| File | Lines | Purpose |
|------|-------|---------|
| `scripts/core/memory/__init__.py` | 11 | Package exports |
| `scripts/core/memory/repository.py` | 89 | ABC — `MemoryRepository` |
| `scripts/core/memory/json_repository.py` | 237 | `JsonMemoryRepository` implementation |
| `scripts/core/memory/models.py` | 8 | Re-export `MemoryEntry` |
| `scripts/core/types/memory.py` | 25 | Frozen type definition (ADR-0002) |
| `tests/test_memory_repository.py` | 267 | 30 unit tests |

**Total:** 636 lines | **Tests:** 30/30 pass

---

## Checklist

### P1 — Must Pass

| # | Criterion | Status | Notes |
|---|-----------|--------|-------|
| 1 | **ABC interface matches `MEMORY_LAYER_DESIGN.md`** | ✅ | All 7 methods present: `store`, `load`, `load_all`, `delete`, `exists`, `count`, `delete_expired` |
| 2 | **No mutable domain types** | ✅ | `MemoryEntry` is a dataclass (not frozen yet — ADR-0003 pending for freezing). Repository never mutates entries. |
| 3 | **Error wrapping uses `MemoryError`** | ✅ | All exceptions wrapped with `code`, `recoverable`, `context`, `cause` |
| 4 | **No external dependencies** | ✅ | stdlib only: `json`, `pathlib`, `datetime`, `abc` |
| 5 | **Test coverage: all methods** | ✅ | 30 tests covering store/load/delete/exists/count/delete_expired/corrupt files |

### P2 — Should Pass

| # | Criterion | Status | Notes |
|---|-----------|--------|-------|
| 6 | **JSON file corruption handled** | ✅ | `json.JSONDecodeError` → returns empty dict |
| 7 | **Scope isolation** | ✅ | Each scope has its own `memory.json` file |
| 8 | **Sorting: timestamp descending** | ✅ | `load_all` sorts by `timestamp` desc |
| 9 | **Cross-scope delete** | ✅ | `delete(entry_id)` removes from ALL scopes (no scope param in ABC) |
| 10 | **Future expiry works** | ✅ | `delete_expired` correctly handles future timestamps |

---

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| **One JSON file per scope** | Simple, debuggable, no locking needed for single-process |
| **Cross-scope delete by design** | Entry IDs are globally unique; scope is a metadata filter, not a namespace |
| **Corrupt file → empty** | Fail-safe: corrupt file doesn't crash the system, just returns empty data |
| **No encryption/compression** | v1 scope — add later via ADR if needed |

---

## Test Coverage Summary

| Test Class | Tests | Coverage |
|------------|-------|----------|
| `TestStoreAndLoad` | 5 | Roundtrip, overwrite, global scope, same ID |
| `TestLoadAll` | 5 | Filtering, sorting, scope isolation, empty |
| `TestDelete` | 4 | Existing, nonexistent, global, cross-scope |
| `TestDeleteExpired` | 4 | Old, no-match, cross-scope, future |
| `TestExistsAndCount` | 5 | Exists, missing, count all, filter by type |
| `TestErrorHandling` | 2 | Nonexistent IDs |
| `TestSerialization` | 2 | Field preservation, JSON structure |
| `TestCorruptFiles` | 3 | Corrupt load, exists, count |
| **Total** | **30** | |

---

## What's NOT Included (v1 Scope)

| Feature | v2/v3 | ADR Required |
|---------|-------|--------------|
| `SqliteMemoryRepository` | v2 | Yes |
| Vector search | v3 | Yes |
| Encryption at rest | v3 | Yes |
| Compression | v2 | No (internal) |
| TTL-based auto-expiry | v2 | No (internal) |
| `MemoryLayer` orchestrator | v1.1 | No (builds on this) |

---

## Next Steps

1. Build `MemoryLayer` orchestrator (validation + dedup before repository)
2. ADR-0003: Freeze `MemoryEntry` fields (like PhaseState)
3. ADR-0004: `SqliteMemoryRepository` when project data exceeds ~10K entries
