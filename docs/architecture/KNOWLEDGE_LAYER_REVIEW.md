# Architecture Review: Knowledge Layer Design

**Review Date:** 2026-07-13
**Reviewer:** CodeAI Architecture Team
**Scope:** `docs/architecture/KNOWLEDGE_LAYER_DESIGN.md`

---

## Verdict: PASS ✅

---

## CORE_RUNTIME.md §2.4 Compliance

| Criterion | Status | Notes |
|-----------|--------|-------|
| `search(query: str, scope: str = "all") -> list[Knowledge]` | ✅ | Signature matches exactly |
| `retrieve(context_type: KnowledgeType, params: dict[str, Any]) -> Context` | ✅ | Signature matches exactly |
| Knowledge types match enums.py | ✅ | All 5 types documented |
| Knowledge kinds match enums.py | ✅ | All 8 kinds documented |
| KnowledgeRepository ABC defined | ✅ | search, store, delete, count |

---

## Dependency Rule

| Import | Allowed | Notes |
|--------|---------|-------|
| Knowledge Layer → Memory Layer (types) | ✅ | MemoryEntry, MemoryType — data only |
| Knowledge Layer → Memory Layer (API) | ✅ | load() — read-only |
| Memory Layer → Knowledge Layer | ❌ | Forbidden — correctly documented |
| Knowledge Layer → Workflow Engine | ❌ | Forbidden — correctly documented |
| Knowledge Layer → OODA Runtime | ❌ | Forbidden — correctly documented |
| Knowledge Layer → Spec Engine | ❌ | Forbidden — correctly documented |
| Knowledge Layer → Judge Engine | ❌ | Forbidden — correctly documented |

---

## SOLID Checklist

| Principle | Status | Evidence |
|-----------|--------|----------|
| **S** — Single Responsibility | ✅ | Only retrieval and indexing. No business logic, no state management. |
| **O** — Open/Closed | ✅ | Open for new backends (SQLite, Vector, Graph). Closed for modification. |
| **L** — Liskov Substitution | ✅ | Any KnowledgeRepository subclass works. Tested with JSON repo. |
| **I** — Interface Segregation | ✅ | Focused ABC: search, store, delete, count. No fat interface. |
| **D** — Dependency Inversion | ✅ | Depends on KnowledgeRepository ABC, not concrete implementations. |

---

## Responsibility Leaks Check

| Check | Status | Notes |
|-------|--------|-------|
| Knowledge Layer has business logic | ✅ No | Pure retrieval and indexing |
| Knowledge Layer manages state | ✅ No | Stateless — all state in repositories |
| Knowledge Layer writes to Memory Layer | ✅ No | Read-only access documented |
| Knowledge Layer couples to specific storage | ✅ No | All storage via Repository Pattern |
| Knowledge Layer couples to LLM | ✅ No | RAG is retrieval only; generation is caller's job |
| Knowledge Layer makes decisions | ✅ No | No evaluation, no routing, no orchestration |

---

## Invariant Coverage

| ID | Rule | Enforcement | Section |
|----|------|-------------|---------|
| KINV-1 | search() returns list (never None) | Return type annotation + docstring | §5 |
| KINV-2 | retrieve() returns Context (never None) | Return type annotation + docstring | §5 |
| KINV-3 | Knowledge items have non-empty source | Indexed on ingest | §4.1 |
| KINV-4 | Search scores in [0.0, 1.0] | Normalized after scoring | §9.5 |
| KINV-5 | Cached results served within TTL | TTL check on read | §13 |
| KINV-6 | MCP errors wrapped in KnowledgeError | All MCP calls wrapped | §15.1 |
| KINV-7 | Memory Layer is read-only | No write methods called | §12.4 |
| KINV-8 | scope must be "all", "project", or "global" | Validated on entry | §16 |

---

## Section Completeness

| # | Section | Present | Quality |
|---|---------|---------|---------|
| 1 | Purpose | ✅ | Clear, concise |
| 2 | Boundaries | ✅ | ASCII diagram + dependency direction |
| 3 | Responsibilities (DO / DON'T) | ✅ | Complete table |
| 4 | What Knowledge Layer DOES (Detailed) | ✅ | Ingestion, indexing, retrieval, delivery |
| 5 | Public API | ✅ | Frozen signatures match CORE_RUNTIME.md |
| 6 | Knowledge Types | ✅ | All types + kinds with sources |
| 7 | MCP as Transport | ✅ | Integration pattern, error handling |
| 8 | Obsidian Integration | ✅ | Vault structure, frontmatter schema |
| 9 | Hybrid Search (OHS) | ✅ | Pipeline, BM25, fuzzy, semantic (v2) |
| 10 | RAG Pipeline | ✅ | Retrieval only, context window, quality signals |
| 11 | GraphRAG (Future) | ✅ | When needed, v2 strategy, v1 fallback |
| 12 | Memory Layer Integration | ✅ | Read-only, coupling rules |
| 13 | Caching Policy | ✅ | Three layers, TTL, size limits, v1 simplification |
| 14 | Result Ranking | ✅ | Formula, weights, scores |
| 15 | Error Handling | ✅ | All codes, retry policy, graceful degradation |
| 16 | Invariants | ✅ | KINV-1 through KINV-8 |
| 17 | Sequence Diagrams | ✅ | search() and retrieve() |
| 18 | Mermaid Architecture | ✅ | Full diagram |
| 19 | API Contracts | ✅ | Knowledge, Context, enums, Repository |
| 20 | Extension Points | ✅ | 8 extensions documented |
| 21 | Future Backend Strategy | ✅ | v1/v2/v3 roadmap |

---

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| MCP as transport, not logic | Keeps KL decoupled from specific tools |
| Memory Layer is read-only | Prevents circular dependency |
| RAG is retrieval only | Generation is caller's responsibility |
| BM25 + fuzzy in v1 | No external dependencies (no vector DB) |
| In-memory cache in v1 | Single-process architecture, no Redis needed |
| GraphRAG deferred to v2 | Complexity not justified for v1 scope |

---

## Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| MCP server unavailable | Medium | Graceful degradation — serve from cache/index |
| Index corruption | Low | Rebuild from source documents |
| Memory Layer unavailable | Low | Search only indexed docs |
| Cache stampede | Low | In-memory only, single process |

---

**PASS**
