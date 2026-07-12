# ERROR_MODEL.md — Unified Error Model

**Date:** 2026-07-11  
**Status:** Frozen

---

## 1. Design Principles

1. **Every error is structured.** No bare strings — always `message` + `code` + `recoverable`.
2. **Every error carries context.** What was the system doing when it failed.
3. **Every error can chain.** `cause` wraps the original exception.
4. **Recoverability is explicit.** Callers can decide retry vs abort.
5. **Error codes are stable.** Refactoring internals doesn't change codes.

---

## 2. Base Class

```python
class CodeAIError(Exception):
    """Base exception for all CodeAI errors."""

    def __init__(
        self,
        message: str,
        code: str,
        recoverable: bool = False,
        context: dict[str, Any] | None = None,
        cause: Exception | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.recoverable = recoverable
        self.context = context or {}
        self.cause = cause
```

| Field | Type | Description |
|-------|------|-------------|
| `message` | `str` | Human-readable error description |
| `code` | `str` | Stable error code (e.g., `"SPEC_001"`) |
| `recoverable` | `bool` | Can the caller retry safely? |
| `context` | `dict[str, Any]` | Execution context at failure point |
| `cause` | `Exception \| None` | Wrapped original exception |

---

## 3. Error Hierarchy

```
CodeAIError
├── SpecError
├── WorkflowError
├── OODAError
├── KnowledgeError
├── MemoryError
├── JudgeError
├── ValidationError
├── ConfigurationError
└── InfrastructureError
```

---

## 4. Error Codes

Format: `{DOMAIN}_{NNN}`

### SpecError

| Code | Message | Recoverable | Context |
|------|---------|-------------|---------|
| `SPEC_001` | Goals.md not found | false | `{path}` |
| `SPEC_002` | Goals.md has invalid structure | true | `{errors: []}` |
| `SPEC_003` | Missing required section | true | `{section}` |
| `SPEC_004` | No requirements found (F-XXX) | true | `{path}` |
| `SPEC_005` | Parse error in goals.md | true | `{line, column}` |
| `SPEC_006` | Spec not approved (human gate) | false | `{path}` |

### WorkflowError

| Code | Message | Recoverable | Context |
|------|---------|-------------|---------|
| `WF_001` | Phase not found | false | `{phase_id}` |
| `WF_002` | Phase already completed | false | `{phase_id}` |
| `WF_003` | Invariant violation | false | `{invariant, phase_id}` |
| `WF_004` | Dependencies not met | true | `{phase_id, missing: []}` |
| `WF_005` | Invalid transition | false | `{from_status, to_status}` |
| `WF_006` | No pending phases | false | `{}` |

### OODAError

| Code | Message | Recoverable | Context |
|------|---------|-------------|---------|
| `OODA_001` | Agent execution failed | true | `{agent, task_id}` |
| `OODA_002` | Agent timeout | true | `{agent, task_id, timeout_s}` |
| `OODA_003` | Task not found | false | `{task_id}` |
| `OODA_004` | Max retries exceeded | false | `{task_id, retries}` |
| `OODA_005` | Invalid plan structure | true | `{task_id, missing: []}` |
| `OODA_006` | Agent output invalid | true | `{agent, task_id, reason}` |

### KnowledgeError

| Code | Message | Recoverable | Context |
|------|---------|-------------|---------|
| `KL_001` | Search failed | true | `{query, scope}` |
| `KL_002` | MCP connection error | true | `{server}` |
| `KL_003` | Context type not found | false | `{context_type}` |
| `KL_004` | Knowledge base empty | false | `{scope}` |
| `KL_005` | Vector DB unavailable | true | `{}` |

### MemoryError

| Code | Message | Recoverable | Context |
|------|---------|-------------|---------|
| `MEM_001` | Storage write failed | true | `{entry_id, backend}` |
| `MEM_002` | Storage read failed | true | `{query, scope}` |
| `MEM_003` | Entry not found | false | `{entry_id}` |
| `MEM_004` | Memory corruption detected | false | `{entry_id}` |
| `MEM_005` | Summarization failed | true | `{scope, depth}` |

### JudgeError

| Code | Message | Recoverable | Context |
|------|---------|-------------|---------|
| `JUDGE_001` | Evaluation failed | true | `{response_path}` |
| `JUDGE_002` | Rubric not found | false | `{rubric_name}` |
| `JUDGE_003` | Scoring timeout | true | `{response_path, timeout_s}` |
| `JUDGE_004` | Invalid verdict | false | `{verdict}` |
| `JUDGE_005` | Route decision failed | false | `{verdict}` |

### ValidationError

| Code | Message | Recoverable | Context |
|------|---------|-------------|---------|
| `VAL_001` | Type mismatch | false | `{field, expected, actual}` |
| `VAL_002` | Required field missing | false | `{field}` |
| `VAL_003` | Value out of range | false | `{field, min, max, actual}` |
| `VAL_004` | Invalid format | false | `{field, expected_format}` |
| `VAL_005` | Schema validation failed | false | `{errors: []}` |

### ConfigurationError

| Code | Message | Recoverable | Context |
|------|---------|-------------|---------|
| `CFG_001` | Missing config file | false | `{path}` |
| `CFG_002` | Invalid config format | false | `{path, reason}` |
| `CFG_003` | Missing required setting | false | `{key}` |
| `CFG_004` | Invalid setting value | false | `{key, value, reason}` |
| `CFG_005` | Config dependency missing | false | `{key, depends_on}` |

### InfrastructureError

| Code | Message | Recoverable | Context |
|------|---------|-------------|---------|
| `INFRA_001` | File system error | true | `{path, operation}` |
| `INFRA_002` | Network error | true | `{url, timeout_s}` |
| `INFRA_003` | Process execution failed | true | `{command, exit_code}` |
| `INFRA_004` | Permission denied | false | `{path, operation}` |
| `INFRA_005` | Disk space full | false | `{path, available_bytes}` |

---

## 5. Context Field Patterns

Each domain populates `context` with relevant data:

```python
# Spec
SpecError("Goals.md not found", "SPEC_001", context={"path": "docs/specs/goals.md"})

# Workflow
WorkflowError("Invariant violation", "WF_003", context={"invariant": "INV1", "phase_id": "implement"})

# OODA
OODAError("Agent timeout", "OODA_002", context={"agent": "@act", "task_id": "abc-123", "timeout_s": 300})

# Knowledge
KnowledgeError("MCP connection error", "KL_002", context={"server": "obsidian"})

# Memory
MemoryError("Storage write failed", "MEM_001", context={"entry_id": "def-456", "backend": "sqlite"})

# Judge
JudgeError("Rubric not found", "JUDGE_002", context={"rubric_name": "analyst-v2"})

# ValidationError
ValidationError("Type mismatch", "VAL_001", context={"field": "priority", "expected": "Priority", "actual": "str"})

# Configuration
ConfigurationError("Missing required setting", "CFG_003", context={"key": "llm.model"})

# Infrastructure
InfrastructureError("File system error", "INFRA_001", context={"path": "/tmp/build", "operation": "write"})
```

---

## 6. Error Chaining

Use `cause` to wrap original exceptions:

```python
try:
    result = llm_client.generate(prompt)
except TimeoutError as e:
    raise OODAError(
        "Agent timeout",
        "OODA_002",
        recoverable=True,
        context={"agent": "@act", "task_id": task_id, "timeout_s": 300},
        cause=e,
    ) from e
```

---

## 7. Recoverability Decision Tree

```
Error raised
    ↓
error.recoverable?
    ├── true → retry with backoff
    │         ├── retries < max → retry
    │         └── retries >= max → escalate to Judge
    └── false → abort or rollback
              ├── phase context → WorkflowEngine.rollback()
              ├── task context → OODARuntime.interrupt()
              └── project context → raise to user
```

---

## 8. Logging Pattern

```python
try:
    spec_engine.validate(path)
except SpecError as e:
    logger.error(
        "spec_validation_failed",
        code=e.code,
        recoverable=e.recoverable,
        context=e.context,
        cause=e.cause,
    )
    if e.recoverable:
        retry()
    else:
        abort()
```
