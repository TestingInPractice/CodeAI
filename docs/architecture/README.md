# Architecture Documentation Index

This directory contains the architectural contracts, reviews, audits, and decision records for the CodeAI Build Loop system. The architecture is built around **6 core subsystems** (SpecEngine, WorkflowEngine, OODA Runtime, Knowledge Layer, Memory Layer, Judge) connected by an **Event Bus**.

## Recommended Reading Order

1. **[CORE_RUNTIME.md](CORE_RUNTIME.md)** — Start here. The master architecture document defining the 6-subsystem design.
2. **[TECH_STACK.md](TECH_STACK.md)** — Technology choices per subsystem with rationale.
3. **[STATE_FLOW.md](STATE_FLOW.md)** — Full project lifecycle from user prompt to completion.
4. **[API_CONTRACT.md](API_CONTRACT.md)** — Frozen public API signatures for all subsystems.
5. **[DEPENDENCY_GRAPH.md](DEPENDENCY_GRAPH.md)** — Dependency rules and layer boundaries.
6. Subsystem design docs:
   - [WORKFLOW_ENGINE_SKELETON.md](WORKFLOW_ENGINE_SKELETON.md) — Workflow Engine interface
   - [KNOWLEDGE_LAYER_DESIGN.md](KNOWLEDGE_LAYER_DESIGN.md) — Knowledge Layer design
   - [MEMORY_LAYER_DESIGN.md](MEMORY_LAYER_DESIGN.md) — Memory Layer design
7. **[ARCHITECTURE_FREEZE.md](ARCHITECTURE_FREEZE.md)** — What is frozen and governance rules.
8. Audits and reviews — to understand current compliance status.

## Core Runtime / Contracts

Foundational architecture documents defining the system design, data models, and interfaces.

| Document | Description |
|----------|-------------|
| [CORE_RUNTIME.md](CORE_RUNTIME.md) | Master architecture: 6-subsystem design, frozen dataclasses, dependency rules |
| [API_CONTRACT.md](API_CONTRACT.md) | Frozen public API signatures for all 6 subsystems |
| [ERROR_MODEL.md](ERROR_MODEL.md) | Unified error model with structured errors and context chaining |
| [EVENTS.md](EVENTS.md) | Event Bus design, naming conventions, and subsystem event catalogs |
| [STATE_FLOW.md](STATE_FLOW.md) | Full project lifecycle state flow (Spec → Workflow → OODA → Judge) |
| [SERIALIZATION.md](SERIALIZATION.md) | JSON serialization model using `Serializable` mixin |
| [DEPENDENCY_GRAPH.md](DEPENDENCY_GRAPH.md) | Internal dependency tree validation (no circular deps) |
| [TECH_STACK.md](TECH_STACK.md) | Technology stack per subsystem with versions and rationale |
| [REVIEW_TYPES.md](REVIEW_TYPES.md) | Type definitions for the review system |
| [REVIEW_PROJECT_CONTEXT.md](REVIEW_PROJECT_CONTEXT.md) | Audit of ProjectContext and RuntimeContext data structures |

## Workflow Engine

Design and specification of the pipeline orchestration subsystem.

| Document | Description |
|----------|-------------|
| [WORKFLOW_ENGINE_SKELETON.md](WORKFLOW_ENGINE_SKELETON.md) | Interface-only specification before business logic |
| [WORKFLOW_REPOSITORY.md](WORKFLOW_REPOSITORY.md) | Persistence layer design using Repository Pattern with JSON storage |
| [WORKFLOW_STATE_MODEL.md](WORKFLOW_STATE_MODEL.md) | State model: types, enums, dataclasses, snapshots |

## OODA Runtime

Observe-Orient-Decide-Act runtime for phase execution.

| Document | Description |
|----------|-------------|
| [OODA_RUNTIME_IMPLEMENTATION_REVIEW.md](OODA_RUNTIME_IMPLEMENTATION_REVIEW.md) | Implementation review: state machine, steps, LangGraph integration |

## Knowledge Layer

On-demand context retrieval for domain knowledge.

| Document | Description |
|----------|-------------|
| [KNOWLEDGE_LAYER_DESIGN.md](KNOWLEDGE_LAYER_DESIGN.md) | Design spec for passive, on-demand context retrieval |
| [KNOWLEDGE_LAYER_ARCHITECTURE_REVIEW.md](KNOWLEDGE_LAYER_ARCHITECTURE_REVIEW.md) | Architecture review against frozen contracts (7/10) |
| [KNOWLEDGE_LAYER_REVIEW.md](KNOWLEDGE_LAYER_REVIEW.md) | Team review verifying CORE_RUNTIME compliance (PASS) |
| [KNOWLEDGE_LAYER_IMPLEMENTATION_REVIEW.md](KNOWLEDGE_LAYER_IMPLEMENTATION_REVIEW.md) | Implementation review: contract compliance, SOLID, test coverage |
| [KNOWLEDGE_LAYER_RECONCILIATION.md](KNOWLEDGE_LAYER_RECONCILIATION.md) | Reconciliation of design vs frozen contracts (P1/P2/P3 fixes) |

## Memory Layer

Operational history, patterns, and execution context storage.

| Document | Description |
|----------|-------------|
| [MEMORY_LAYER_DESIGN.md](MEMORY_LAYER_DESIGN.md) | Design spec for operational history and pattern storage |
| [MEMORY_LAYER_REVIEW.md](MEMORY_LAYER_REVIEW.md) | Architecture review (8/10 architecture, 9/10 extensibility) |
| [MEMORY_LAYER_IMPLEMENTATION_REVIEW.md](MEMORY_LAYER_IMPLEMENTATION_REVIEW.md) | Implementation review: invariants, SOLID, dependency rules (PASS) |
| [MEMORY_REPOSITORY_REVIEW.md](MEMORY_REPOSITORY_REVIEW.md) | Repository persistence layer review (PASS) |

## Event Bus

Event-driven communication between subsystems.

| Document | Description |
|----------|-------------|
| [EVENT_BUS_IMPLEMENTATION_REVIEW.md](EVENT_BUS_IMPLEMENTATION_REVIEW.md) | Implementation review: publish/subscribe/async support |

## Audits and Validation Gates

Production readiness assessments, gap analyses, and validation reports.

| Document | Description |
|----------|-------------|
| [FINAL_PRODUCTION_AUDIT.md](FINAL_PRODUCTION_AUDIT.md) | First production audit (5.5/10, NOT READY) |
| [FINAL_PRODUCTION_AUDIT_V2.md](FINAL_PRODUCTION_AUDIT_V2.md) | Second independent zero-trust production audit |
| [GAP_ANALYSIS.md](GAP_ANALYSIS.md) | Design vs implementation gap analysis (complete/partial/stub/missing) |
| [IMPLEMENTATION_READINESS.md](IMPLEMENTATION_READINESS.md) | Readiness assessment for new developers (30 gaps found) |
| [END_TO_END_VALIDATION.md](END_TO_END_VALIDATION.md) | Full pipeline validation from user prompt to completion |
| [INTEGRATION_REVIEW.md](INTEGRATION_REVIEW.md) | Integration test coverage for cross-subsystem scenarios |
| [API_CONTRACT_AUDIT.md](API_CONTRACT_AUDIT.md) | Audit of test files against CORE_RUNTIME public API baseline |
| [ARCHITECTURE_HEALTH.md](ARCHITECTURE_HEALTH.md) | Quality scorecard: SOLID compliance, dependency rules (8/10) |

## Architecture Reviews

Compliance audits and post-implementation reviews.

| Document | Description |
|----------|-------------|
| [ARCHITECTURE_REVIEW.md](ARCHITECTURE_REVIEW.md) | Original full compliance audit (6.5/10) |
| [ARCHITECTURE_REVIEW_V2.md](ARCHITECTURE_REVIEW_V2.md) | Post-implementation review verifying frozen API adherence |
| [ARCHITECTURE_REVIEW_VALIDATION.md](ARCHITECTURE_REVIEW_VALIDATION.md) | Validation of P0/P1 findings (true vs false positives) |
| [WORKFLOW_ENGINE_REVIEW.md](WORKFLOW_ENGINE_REVIEW.md) | SOLID compliance audit of WorkflowEngine (v2.0, post-fix) |
| [WORKFLOW_ENGINE_PRODUCTION_REVIEW.md](WORKFLOW_ENGINE_PRODUCTION_REVIEW.md) | Production readiness review (9/10) |

## Freeze and Governance

Architecture freeze declarations, gate checks, and change reports.

| Document | Description |
|----------|-------------|
| [ARCHITECTURE_FREEZE.md](ARCHITECTURE_FREEZE.md) | v1.0 freeze declaration and governance rules |
| [ARCHITECTURE_GATE_FINAL.md](ARCHITECTURE_GATE_FINAL.md) | Final architecture gate: API compliance, type safety, coverage |
| [FREEZE_REPORT.md](FREEZE_REPORT.md) | Changes applied during the v1.0 freeze |
| [IMPLEMENTATION_GATE.md](IMPLEMENTATION_GATE.md) | Release gate check (NOT READY for 20-engineer team) |
| [REPORT_HEALTH_FIXES.md](REPORT_HEALTH_FIXES.md) | P0/P1 health fixes: `frozen=True`, `slots=True` |

## ADR

Architecture Decision Records documenting key design decisions.

| Document | Description |
|----------|-------------|
| [adr/ADR-0001-core-runtime.md](adr/ADR-0001-core-runtime.md) | ADR #1: Unify 3 duplicated modes into single 6-subsystem runtime |
| [ADR_REVIEW.md](ADR_REVIEW.md) | ADR coverage audit: 1 of 12 decisions has an ADR |
