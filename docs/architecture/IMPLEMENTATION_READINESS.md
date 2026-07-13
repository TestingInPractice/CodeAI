# IMPLEMENTATION_READINESS.md — Can a New Developer Implement Every Subsystem?

**Date:** 2026-07-12
**Scope:** Full architecture audit for implementation readiness
**Status:** COMPLETE — No code changes made
**Verdict:** NOT READY — 30 gaps found (8 critical, 12 high, 10 medium)

---

## 1. Executive Summary

| Metric | Value |
|--------|-------|
| **Critical Gaps (Blockers)** | 8 |
| **High Gaps (Ambiguities)** | 12 |
| **Medium Gaps (Missing Contracts)** | 10 |
| **Total Gaps** | 30 |
| **Readiness Score** | **4/10** |

**Answer to the question:** Can a new developer implement every subsystem without asking additional architectural questions?

**No.** A new developer would be blocked by type mismatches between documentation and code, incomplete frozen contracts, missing implementation guidance, and ambiguous interfaces. The architecture documents contradict each other in multiple places, and the frozen contract doesn't match the actual implementation.

---

## 2. Critical Gaps (Blockers)

These gaps prevent a developer from starting implementation.

### G-001: DataModel.fields Type Mismatch

| Source | Type |
|--------|------|
| `CORE_RUNTIME.md §4` | `dict[str, str]` |
| `ARCHITECTURE_FREEZE.md §4` | `dict[str, str]` |
| `spec.py:34` | `list[dict[str, Any]]` |

**Impact:** A developer doesn't know if `DataModel.fields` should be a dict mapping field names to types, or a list of field definition dicts. This affects every subsystem that uses `DataModel`.

**Fix:** Decide which representation is correct and update all documents.

---

### G-002: APIContract Missing Fields

| Source | Fields |
|--------|--------|
| `CORE_RUNTIME.md §4` | `method`, `path`, `request: dict`, `response: dict`, `description` |
| `ARCHITECTURE_FREEZE.md §4` | `method`, `path`, `request: dict`, `response: dict`, `description` |
| `spec.py:38-42` | `method`, `path`, `description` |

**Impact:** A developer doesn't know if `APIContract` should include `request` and `response` schemas. This affects Spec Engine's `parse()` output.

**Fix:** Either add `request`/`response` fields to `spec.py`, or update documentation to remove them.

---

### G-003: WorkflowEngine API Mismatch

| Source | Methods |
|--------|---------|
| `ARCHITECTURE_FREEZE.md §3.2` | `start`, `next`, `complete`, `rollback` (4 methods) |
| `workflow_engine.py` | `start`, `next_phase`, `complete_phase`, `rollback`, `current_phase`, `current_task`, `start_task`, `complete_task`, `fail_task`, `status`, `load`, `save` (12 methods) |

**Impact:** A developer doesn't know which API to implement against. The frozen contract says 4 methods, the actual code has 12.

**Fix:** Create ADR to reconcile, or rename methods to match frozen API.

---

### G-004: JudgeEngine evaluate() Signature Mismatch

| Source | Signature |
|--------|-----------|
| `ARCHITECTURE_FREEZE.md §3.6` | `evaluate(response: str, context: str, spec: str) -> Verdict` |
| `judge_engine.py:159-165` | `evaluate(response: str, context: str = "", spec: str = "", acceptance_criteria: list[str] | None = None) -> Verdict` |

**Impact:** A developer doesn't know the correct signature. The extra `acceptance_criteria` parameter changes the contract.

**Fix:** Create ADR to add `acceptance_criteria`, or move AC checking to a separate method.

---

### G-005: WorkflowEngine Constructor Mismatch

| Source | Constructor |
|--------|-------------|
| `WORKFLOW_ENGINE_SKELETON.md §2` | `__init__(context: ProjectContext, state_path: Path | None)` |
| `workflow_engine.py:57-60` | `__init__(state: WorkflowState | None = None, repository: WorkflowRepository | None = None)` |

**Impact:** A developer doesn't know the correct constructor parameters. The skeleton says `ProjectContext` + `Path`, the actual code says `WorkflowState` + `WorkflowRepository`.

**Fix:** Update documentation to match actual implementation.

---

### G-006: Event Names Inconsistency

| Source | Event Names |
|--------|-------------|
| `EVENTS.md` | `spec.created`, `phase.started`, `judge.passed`, `judge.failed` |
| `CORE_RUNTIME.md` | `spec.generated`, `workflow.started`, `judge.evaluated`, `judge.routed` |
| `API_CONTRACT.md` | `spec.generated`, `workflow.started`, `judge.evaluated`, `judge.routed` |
| `event_bus.py:17-23` | `spec.generated`, `workflow.started`, `judge.evaluated`, `judge.routed` |

**Impact:** EVENTS.md has different event names than all other documents. A developer doesn't know which event names to use.

**Fix:** Update EVENTS.md to match CORE_RUNTIME.md and API_CONTRACT.md.

---

### G-007: RepositoryError Not in Error Hierarchy

| Source | Error Hierarchy |
|--------|-----------------|
| `errors.py` | `CodeAIError` base with 9 error types |
| `json_repo.py:240-269` | `RepositoryError(Exception)` — does NOT inherit from `CodeAIError` |

**Impact:** A developer doesn't know if `RepositoryError` should be part of the unified error hierarchy. It duplicates the `CodeAIError` interface (message, code, recoverable, cause).

**Fix:** Make `RepositoryError` inherit from `CodeAIError`, or create ADR for separate hierarchy.

---

### G-008: Frozen Contract Incomplete

| Source | Dataclasses | Enums |
|--------|-------------|-------|
| `ARCHITECTURE_FREEZE.md §4-5` | 23 dataclasses | 8 enums |
| Actual code | 25 dataclasses | 9 enums |

**Added types:** `RollbackEntry`, `WorkflowSnapshot`
**Added enums:** `WorkflowStatus`

**Impact:** A developer doesn't know which types are part of the frozen contract. The frozen contract claims 23 dataclasses, but the code has 25.

**Fix:** Create ADR to add `RollbackEntry`, `WorkflowSnapshot`, `WorkflowStatus` to frozen contract.

---

## 3. High Gaps (Ambiguities)

These gaps cause confusion but don't block implementation.

### G-009: No Spec Engine Implementation Guidance

`SpecEngine` is a stub with `raise NotImplementedError`. Missing:

- What LLM to use for `generate()`
- What prompt template to use
- What output format goals.md should have
- What rules `validate()` checks
- What parsing strategy `parse()` uses
- What the human gate mechanism is for `approve()`

**Impact:** A developer has too many decisions to make.

---

### G-010: No OODA Runtime Implementation Guidance

`OODARuntime` is a stub with `raise NotImplementedError`. Missing:

- How to run observe/orient/decide/act cycle
- How to manage shared state between agents
- How to validate plans
- How to generate summaries for Judge Engine
- How to resume from artifacts
- How to gracefully interrupt agents

**Impact:** A developer has too many decisions to make.

---

### G-011: No Knowledge Layer Implementation Guidance

`KnowledgeLayer` is a stub with `raise NotImplementedError`. Missing:

- What search algorithm to use
- What indexing strategy to use
- How to assemble context from knowledge items
- How to integrate with MCP, Obsidian, OHS, RAG, GraphRAG, Vector DB

**Impact:** A developer has too many decisions to make.

---

### G-012: No Memory Layer Implementation Guidance

`MemoryLayer` is a stub with `raise NotImplementedError`. Missing:

- What storage backend to use (JSON? SQLite? Both?)
- What schema to use for storage
- What search strategy to use for `load()`
- What ranking algorithm to use
- What summarization strategy to use for `summarize()`

**Impact:** A developer has too many decisions to make.

---

### G-013: No Judge Engine Integration Guidance

`JudgeEngine` is fully implemented but isolated. Missing:

- How to integrate with OODA Runtime
- How to integrate with Workflow Engine
- How to use DeepEval adapter
- When to call `evaluate()` vs `score()` vs `route()`
- How to wire up the 4-pillar scoring

**Impact:** A developer doesn't know how to connect the pieces.

---

### G-014: No EventBus Implementation Guidance

`EventBus` is a stub with basic subscribe/publish. Missing:

- How to handle async handlers
- How to handle handler errors
- How to handle event ordering
- How to handle wildcard subscriptions
- How to handle event persistence

**Impact:** A developer has too many decisions to make.

---

### G-015: Missing Validation Rules

`SpecEngine.validate()` — no guidance on:

- What rules to check
- What makes a valid goals.md
- What error messages to return
- What warnings to return

**Impact:** A developer doesn't know the validation contract.

---

### G-016: Missing Persistence Contract

`WorkflowEngine.load()` / `save()` — no guidance on:

- How it interacts with repository
- When snapshots are created/updated
- What happens when repository is None
- How to handle concurrent access

**Impact:** A developer doesn't know the persistence lifecycle.

---

### G-017: Missing Test Contract

No guidance on:

- What tests to write
- Test coverage requirements
- Test naming conventions
- Test file locations
- Test fixtures
- Mocking strategy

**Impact:** A developer doesn't know the quality bar.

---

### G-018: Missing Configuration Contract

No guidance on:

- How to configure subsystems
- Where configuration lives
- Configuration format (YAML? JSON? env vars?)
- Default values
- Required vs optional settings

**Impact:** A developer doesn't know how to make subsystems configurable.

---

### G-019: Missing Logging Contract

No guidance on:

- What to log
- Log levels (DEBUG, INFO, WARNING, ERROR)
- Log format (JSON? text?)
- Log destinations (stdout? file? both?)

**Impact:** A developer doesn't know the observability requirements.

---

### G-020: Missing Error Recovery Guidance

`CodeAIError.recoverable` — no guidance on:

- When is it True? When is it False?
- Retry policies (how many retries? backoff strategy?)
- Fallback strategies
- Escalation paths

**Impact:** A developer doesn't know how to handle errors.

---

## 4. Medium Gaps (Missing Contracts)

These gaps affect code quality but don't block implementation.

### G-021: Missing Context Type Usage

`Context` is defined in `types/knowledge.py` but never used in any engine. No guidance on:

- What `Context` contains
- How to create a `Context`
- How to use a `Context`
- When to create a `Context`

**Impact:** A developer doesn't know how to use this type.

---

### G-022: Missing OODAResult Type Usage

`OODAResult` is defined in `types/ooda.py` but never used in any engine. No guidance on:

- What `OODAResult` contains
- How to create an `OODAResult`
- How to use an `OODAResult`
- When to create an `OODAResult`

**Impact:** A developer doesn't know how to use this type.

---

### G-023: Missing Artifact Type Usage

`Artifact` is defined in `types/common.py` but never used in any engine. No guidance on:

- What `Artifact` contains
- How to create an `Artifact`
- How to use an `Artifact`
- When to create an `Artifact`

**Impact:** A developer doesn't know how to use this type.

---

### G-024: Missing RuntimeContext Usage

`RuntimeContext` is defined in `types/common.py` but never used in any engine. No guidance on:

- How to create a `RuntimeContext`
- How to update a `RuntimeContext`
- When to create a `RuntimeContext`
- Who owns the `RuntimeContext`

**Impact:** A developer doesn't know how to use this type.

---

### G-025: Missing Event Type Usage

`Event` is defined in `types/common.py` but never used in any engine. No guidance on:

- When to create events
- What data to include in events
- How to correlate events
- How to handle event failures

**Impact:** A developer doesn't know how to use this type.

---

### G-026: Missing Protocol Types

No `typing.Protocol` for engine interfaces. Missing:

- `SpecEngineProtocol`
- `WorkflowEngineProtocol`
- `OODARuntimeProtocol`
- `KnowledgeLayerProtocol`
- `MemoryLayerProtocol`
- `JudgeEngineProtocol`

**Impact:** A developer can't verify they're implementing the correct interface.

---

### G-027: Missing Factory Pattern

No guidance on:

- How to create engine instances
- Dependency injection
- Wiring subsystems together
- Initialization order

**Impact:** A developer doesn't know how to wire the system.

---

### G-028: Missing Lifecycle Management

No guidance on:

- Engine initialization order
- Engine shutdown
- Resource cleanup
- Graceful degradation

**Impact:** A developer doesn't know the lifecycle.

---

### G-029: Missing Integration Tests

No guidance on:

- How to test subsystem integration
- Test fixtures
- Test data
- Mocking strategy for external services

**Impact:** A developer doesn't know how to verify correctness.

---

### G-030: Missing Deployment Guidance

No guidance on:

- How to deploy the system
- Environment variables
- Docker/container setup
- CI/CD pipeline

**Impact:** A developer doesn't know how to deploy.

---

## 5. Contradictions Between Documents

| # | Document A | Document B | Contradiction |
|---|-----------|-----------|---------------|
| 1 | `EVENTS.md` | `CORE_RUNTIME.md` | `spec.created` vs `spec.generated` |
| 2 | `EVENTS.md` | `API_CONTRACT.md` | `phase.started` vs `workflow.started` |
| 3 | `EVENTS.md` | `CORE_RUNTIME.md` | `judge.passed/failed` vs `judge.evaluated/routed` |
| 4 | `CORE_RUNTIME.md` | `spec.py` | `DataModel.fields: dict[str, str]` vs `list[dict[str, Any]]` |
| 5 | `CORE_RUNTIME.md` | `spec.py` | `APIContract` has `request`/`response` fields vs not |
| 6 | `ARCHITECTURE_FREEZE.md` | `workflow_engine.py` | 4 methods vs 12 methods |
| 7 | `ARCHITECTURE_FREEZE.md` | `judge_engine.py` | 3 params vs 4 params |
| 8 | `WORKFLOW_ENGINE_SKELETON.md` | `workflow_engine.py` | `ProjectContext`+`Path` vs `WorkflowState`+`WorkflowRepository` |
| 9 | `ARCHITECTURE_FREEZE.md` | actual code | 23 dataclasses vs 25 dataclasses |
| 10 | `ARCHITECTURE_FREEZE.md` | actual code | 8 enums vs 9 enums |

---

## 6. Recommended Fixes (Priority Order)

### Immediate (Before Any Implementation)

1. **Reconcile DataModel.fields type** — decide `dict[str, str]` vs `list[dict[str, Any]]`
2. **Reconcile APIContract fields** — decide if `request`/`response` should exist
3. **Reconcile WorkflowEngine API** — rename methods or update frozen contract
4. **Reconcile JudgeEngine signature** — add `acceptance_criteria` or separate method
5. **Reconcile WorkflowEngine constructor** — update documentation
6. **Reconcile event names** — update EVENTS.md
7. **Fix RepositoryError hierarchy** — inherit from `CodeAIError`
8. **Update frozen contract** — add `RollbackEntry`, `WorkflowSnapshot`, `WorkflowStatus`

### Short-Term (Before v1.0)

9. **Add implementation guidance for Spec Engine** — LLM, prompt template, output format
10. **Add implementation guidance for OODA Runtime** — agent orchestration, state management
11. **Add implementation guidance for Knowledge Layer** — search, indexing, MCP integration
12. **Add implementation guidance for Memory Layer** — storage, search, summarization
13. **Add Judge Engine integration guide** — how to wire up with other subsystems
14. **Add EventBus implementation guide** — async, errors, wildcards
15. **Add validation rules for SpecEngine** — what makes a valid goals.md
16. **Add persistence contract** — lifecycle, concurrency, recovery
17. **Add test contract** — coverage, naming, fixtures, mocking
18. **Add configuration contract** — format, defaults, required/optional
19. **Add logging contract** — levels, format, destinations
20. **Add error recovery guidance** — retry, backoff, escalation

### Long-Term (v2.0+)

21. **Add Protocol types** — formal interface contracts
22. **Add factory pattern** — dependency injection, wiring
23. **Add lifecycle management** — init, shutdown, cleanup
24. **Add integration tests** — subsystem integration, mocking
25. **Add deployment guidance** — Docker, CI/CD, environment

---

## 7. Appendix: Verification Checklist

| Check | Status | Evidence |
|-------|--------|----------|
| DataModel.fields type consistent | ❌ FAIL | G-001 |
| APIContract fields consistent | ❌ FAIL | G-002 |
| WorkflowEngine API consistent | ❌ FAIL | G-003 |
| JudgeEngine signature consistent | ❌ FAIL | G-004 |
| WorkflowEngine constructor consistent | ❌ FAIL | G-005 |
| Event names consistent | ❌ FAIL | G-006 |
| RepositoryError in hierarchy | ❌ FAIL | G-007 |
| Frozen contract complete | ❌ FAIL | G-008 |
| Spec Engine guidance exists | ❌ FAIL | G-009 |
| OODA Runtime guidance exists | ❌ FAIL | G-010 |
| Knowledge Layer guidance exists | ❌ FAIL | G-011 |
| Memory Layer guidance exists | ❌ FAIL | G-012 |
| Judge Engine integration guide exists | ❌ FAIL | G-013 |
| EventBus guidance exists | ❌ FAIL | G-014 |
| Validation rules documented | ❌ FAIL | G-015 |
| Persistence contract documented | ❌ FAIL | G-016 |
| Test contract documented | ❌ FAIL | G-017 |
| Configuration contract documented | ❌ FAIL | G-018 |
| Logging contract documented | ❌ FAIL | G-019 |
| Error recovery guidance exists | ❌ FAIL | G-020 |
| Context type usage documented | ❌ FAIL | G-021 |
| OODAResult type usage documented | ❌ FAIL | G-022 |
| Artifact type usage documented | ❌ FAIL | G-023 |
| RuntimeContext usage documented | ❌ FAIL | G-024 |
| Event type usage documented | ❌ FAIL | G-025 |
| Protocol types exist | ❌ FAIL | G-026 |
| Factory pattern documented | ❌ FAIL | G-027 |
| Lifecycle management documented | ❌ FAIL | G-028 |
| Integration tests guidance exists | ❌ FAIL | G-029 |
| Deployment guidance exists | ❌ FAIL | G-030 |

**Total: 0/30 PASS**

---

## 8. Minimum Viable Readiness

To reach minimum viable readiness (score 6/10), fix:

1. **G-001 to G-008** — Reconcile all contradictions between docs and code
2. **G-009 to G-012** — Add implementation guidance for 4 stub subsystems
3. **G-015** — Add validation rules for SpecEngine
4. **G-017** — Add test contract

This brings the score from 4/10 to approximately 6/10.

---

*Readiness audit completed. No files were modified.*
