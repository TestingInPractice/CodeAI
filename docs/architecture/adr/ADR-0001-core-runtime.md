# ADR-0001: Core Runtime Architecture

**Date:** 2026-07-12
**Status:** Accepted
**Deciders:** CodeAI Team

---

## Context

CodeAI Platform had 3 operating modes (A/B/C) with duplicated state machines, judges, and agent orchestration. Each mode had its own:
- State management (shell scripts + state.json)
- Judge evaluation (evaluate_judge.py with mode-specific rubrics)
- Agent dispatch (run-task.sh with mode-specific steps)
- Error handling (ad-hoc shell script checks)

This duplication caused:
- Inconsistent behavior between modes
- Hard to add new features (changes needed in 3 places)
- No shared type system (each mode defined its own data structures)
- No event-driven architecture (tightly coupled)

---

## Decision

Adopt a **6-subsystem + Event Bus architecture** with:

1. **Spec Engine** — specification lifecycle (generate → validate → human gate → parse)
2. **Workflow Engine** — pipeline state management (phases, tasks, transitions, invariants)
3. **OODA Runtime** — agent orchestration (observe/orient/decide/act cycle)
4. **Knowledge Layer** — passive knowledge provider (search, retrieve context)
5. **Memory Layer** — history and learned patterns (store, load, summarize)
6. **Judge Engine** — evaluation and routing (evaluate, score, route)
7. **Event Bus** — extension point for subsystem communication

---

## Alternatives Considered

### Alternative 1: Monolithic Runtime

**Description:** Single class with all responsibilities (spec + workflow + OODA + judge).

**Pros:**
- Simpler to implement initially
- No inter-subsystem communication needed
- Single state machine

**Cons:**
- Violates Single Responsibility Principle
- Hard to test individual components
- Tight coupling between spec generation and execution
- Cannot swap Knowledge Layer implementation without touching everything

**Rejected because:** Scalability and testability concerns. Each subsystem has distinct responsibilities that should be independently testable.

### Alternative 2: Plugin Architecture

**Description:** Core runtime with dynamically loaded plugins for each subsystem.

**Pros:**
- Maximum flexibility
- Third-party extensions possible
- Runtime subsystem replacement

**Cons:**
- Over-engineered for current needs
- Dynamic loading makes static analysis impossible
- Plugin versioning complexity
- No clear benefit over static subsystems

**Rejected because:** Current team is small (1-2 developers). Plugin overhead not justified. Can always refactor to plugins later if needed.

### Alternative 3: Message Queue Architecture

**Description:** Subsystems communicate via message queue (Redis, RabbitMQ).

**Pros:**
- Loose coupling via async messaging
- Natural event-driven pattern
- Scalable to distributed systems

**Cons:**
- Requires external infrastructure (message broker)
- Adds latency for synchronous operations
- Overkill for single-machine development tool
- Debugging harder (message tracing)

**Rejected because:** CodeAI is a single-machine development tool. Message queue adds operational complexity without proportional benefit. Event Bus (in-process) provides loose coupling without infrastructure.

### Alternative 4: Keep Existing Shell Scripts

**Description:** Continue with build-loop.sh, run-task.sh, state.json approach.

**Pros:**
- No migration cost
- Already working
- Team familiar with it

**Cons:**
- No type safety (JSON strings everywhere)
- Duplicated logic across modes
- Hard to add new features
- No shared state model
- Shell script error handling is fragile

**Rejected because:** The duplication and fragility were blocking feature development. Migration cost is one-time; maintenance savings are permanent.

---

## Consequences

### Positive

1. **Type safety:** All data flows through typed dataclasses (23 dataclasses, 8 enums)
2. **Single source of truth:** One state machine in Workflow Engine, one judge in Judge Engine
3. **Testability:** Each subsystem independently unit-testable
4. **Extensibility:** Event Bus allows adding observability, logging, analytics without modifying subsystems
5. **Knowledge separation:** Knowledge Layer (passive) vs Memory Layer (active history) — clean domain model
6. **Frozen contracts:** API_CONTRACT.md defines stable interfaces; implementations can change freely

### Negative

1. **Migration cost:** Existing shell scripts need to be replaced (Phase 2-4)
2. **Learning curve:** Team needs to understand 6 subsystems instead of 3 modes
3. **Overhead:** More files, more imports, more indirection
4. **Stub phase:** Currently all implementations are `raise NotImplementedError`

### Mitigations

- Migration is incremental (one subsystem at a time)
- Architecture docs provide clear guidance
- Stub implementations allow testing the structure before logic
- EVENT_BUS.md documents future extension points

---

## References

- `docs/architecture/CORE_RUNTIME.md` — frozen architecture
- `docs/architecture/API_CONTRACT.md` — stable API contracts
- `docs/architecture/TECH_STACK.md` — technology choices
- `docs/architecture/STATE_FLOW.md` — state machine design
- `docs/architecture/EVENTS.md` — event catalog
- `docs/architecture/DEPENDENCY_GRAPH.md` — dependency rules
- `docs/architecture/ARCHITECTURE_HEALTH.md` — quality audit (8.40/10)
