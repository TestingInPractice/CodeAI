# END_TO_END_VALIDATION.md — End-to-End Integration

**Status:** PASS
**Date:** 2026-07-14

## Execution Diagram

```
User Prompt
    │
    ▼
┌─────────────┐
│ SpecEngine   │──→ goals.md → StructuredSpec
└──────┬──────┘
       │
       ▼
┌──────────────┐
│WorkflowEngine│──→ phases → PhaseState[]
└──────┬───────┘
       │
       ▼
┌─────────────┐    ┌──────────────┐    ┌───────────────┐
│ OODARuntime  │◄───│KnowledgeLayer│    │ MemoryLayer    │
│              │◄───│              │    │                │
└──────┬──────┘    └──────────────┘    └────────────────┘
       │
       ▼
┌─────────────┐
│ JudgeEngine  │──→ Verdict → PASS / FAIL / PASS_WITH_CONCERNS
└──────┬──────┘
       │
       ├──→ PASS → WorkflowEngine.complete() → next phase
       └──→ FAIL → WorkflowEngine.rollback() → phase returns to PENDING
```

## Sequence: Successful Pipeline

```
1. SpecEngine.generate(prompt)      → goals.md
2. SpecEngine.validate(goals.md)    → ValidationResult(valid=True)
3. SpecEngine.approve(goals.md)     → phase_id set
4. SpecEngine.parse(goals.md)       → StructuredSpec
5. WorkflowEngine creates phases    → PhaseState[]
6. For each phase:
   a. WorkflowEngine.start(phase)
   b. KnowledgeLayer.index_all(items)
   c. MemoryLayer.store(entry)
   d. OODARuntime.execute(task)     → OODAResult
   e. JudgeEngine.evaluate()        → Verdict
   f. WorkflowEngine.complete(phase) → phase COMPLETED
```

## Sequence: Judge FAIL → Rollback

```
1-5. (same as above)
6. For the phase:
   a. WorkflowEngine.start(phase)
   b. OODARuntime.execute(task)
   c. JudgeEngine.evaluate()        → Verdict(FAIL)
   d. WorkflowEngine.rollback(phase) → phase → PENDING
   e. Pipeline marks phase as failed, moves on
```

## Event Flow

```
spec.created
spec.validated
phase.started
task.completed
judge.evaluated
phase.completed    (or phase.rollback)
```

## State Transitions

| Phase State | Trigger | Next State |
|-------------|---------|------------|
| PENDING | start() | IN_PROGRESS |
| IN_PROGRESS | complete(judge_passed=True) | COMPLETED |
| IN_PROGRESS | rollback() | PENDING |
| PENDING | (loop exit) | — (skipped) |

## Artifacts Produced

- `ooda-summary-{uuid}.md` — OODA execution summary
- `plan-{uuid}.json` — execution plan

## Subsystem Interactions

| From | To | Method | Data |
|------|-----|--------|------|
| Pipeline | SpecEngine | generate/validate/approve/parse | prompt → StructuredSpec |
| Pipeline | WorkflowEngine | start/next/complete/rollback | PhaseState lifecycle |
| Pipeline | OODARuntime | execute | Task → OODAResult |
| Pipeline | KnowledgeLayer | index_all/search | Knowledge items |
| Pipeline | MemoryLayer | store/load | MemoryEntry |
| Pipeline | JudgeEngine | evaluate/route | response+context → Verdict |
| Pipeline | EventBus | publish | Event notifications |

## Known Limitations

- SpecEngine is template-based (no LLM)
- Judge FAIL does not retry — phase is marked as failed and pipeline moves on
- No phase dependency re-evaluation after rollback
- EventBus subscription is in-memory only (no persistence)
- Single-threaded execution

## Test Coverage

17 tests in `tests/integration/test_end_to_end.py`:
- 3 successful pipeline tests
- 2 judge fail/rollback tests
- 2 judge fail → OODA route tests
- 2 judge fail → Spec route tests
- 1 memory persistence test
- 3 knowledge retrieval tests
- 2 event bus notification tests
- 5 spec engine standalone tests
