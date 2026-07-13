# API Contract Audit

**Date:** 2026-07-13
**Scope:** All test files in tests/
**Baseline:** CORE_RUNTIME.md public API

---

## Public API (CORE_RUNTIME.md)

### WorkflowEngine
```python
def start(phase: str) -> None
def next() -> Phase | None
def complete(phase: str, judge_passed: bool) -> None
def rollback(phase: str, reason: str) -> None
```

### JudgeEngine
```python
def evaluate(response: str, context: str, spec: str) -> Verdict
def score(response: str, rubric: Rubric) -> Score
def route(verdict: Verdict) -> RouteAction
```

---

## Violations Found

### Private API Violations

**test_workflow_engine.py:**

| Line | Violation |
|------|-----------|
| 52 | `engine._snapshot.status` |
| 53 | `engine._snapshot.iteration` |
| 187 | `engine._snapshot.status` |
| 207 | `engine._snapshot.rollback_stack` |
| 218 | `engine._snapshot.status` |
| 255 | `engine._snapshot.rollback_stack` |
| 256 | `engine._snapshot.rollback_stack[0].reason` |
| 257 | `engine._snapshot.rollback_stack[1].reason` |
| 281 | `engine._snapshot.status` |
| 297 | `engine._snapshot.rollback_stack` |

**test_judge_engine.py:**

| Line | Violation |
|------|-----------|
| 236 | `from judge_engine import _tokenize` |
| 241 | `from judge_engine import _score_relevance` |
| 249 | `from judge_engine import _score_relevance` |
| 257 | `from judge_engine import _score_faithfulness` |
| 262 | `from judge_engine import _score_faithfulness` |
| 270 | `from judge_engine import _score_context_precision` |
| 276 | `from judge_engine import _score_context_precision` |
| 282 | `from judge_engine import _score_ac` |
| 287 | `from judge_engine import _score_ac` |

### Legacy API Violations

**test_judge_engine.py:**

| Line | Violation |
|------|-----------|
| 40 | `engine.evaluate(response, context, spec, ac)` — 4 args, expects 3 |
| 55 | `engine.evaluate(response, context, spec, ac)` — 4 args, expects 3 |
| 74 | `engine.evaluate(response, context, spec, ac)` — 4 args, expects 3 |

---

## Summary

| Metric | Count |
|--------|-------|
| Public API violations | 0 |
| Private API violations | 19 |
| Legacy API usages | 3 |

---

## Verdict

# FAIL

**Root cause:** Tests access private `engine._snapshot` and import private `_` helpers.
