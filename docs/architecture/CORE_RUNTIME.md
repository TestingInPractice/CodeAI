# CodeAI Platform — Core Runtime Architecture

**Status:** Fixed  
**Date:** 2026-07-11  
**Rule:** Архитектура заморожена. Изменения только через ADR.

---

## 1. Overview

CodeAI Platform состоит из 6 подсистем + Event Bus (extension point).

```mermaid
graph TB
    U[User] --> SE[Spec Engine]

    SE -->|structured spec| WE[Workflow Engine]

    WE -->|phase, task| OR[OODA Runtime]

    OR <-->|context| KL[Knowledge Layer]
    OR <-->|history| ML[Memory Layer]

    KL --> JE[Judge Engine]
    ML --> JE

    JE -->|PASS| WE
    JE -->|FAIL: repeat| OR
    JE -->|FAIL: revise| SE
    JE -->|FAIL: retask| WE

    subgraph "Event Bus (extension)"
        EB[Event Bus]
    end

    SE -.->|events| EB
    WE -.->|events| EB
    OR -.->|events| EB
    KL -.->|events| EB
    ML -.->|events| EB
    JE -.->|events| EB

    style SE fill:#2196F3,color:#fff
    style WE fill:#4CAF50,color:#fff
    style OR fill:#9C27B0,color:#fff
    style KL fill:#FF9800,color:#fff
    style ML fill:#FF5722,color:#fff
    style JE fill:#f44336,color:#fff
    style EB fill:#9E9E9E,color:#fff,stroke-dasharray: 5 5
```

### Принципы

1. **Архитектура отделена от технологий.** Подсистемы определяются ответственностью, а не библиотеками.
2. **API между подсистемами стабильны.** Реализацию можно менять, не ломая контракты.
3. **Event Bus — extension point.** Не обязательно реализовывать сразу, но архитектура его предусматривает.
4. **Memory Layer отделена от Knowledge Layer.** Память — это не только знания, но и история, паттерны, контекст.

---

## 2. Subsystems

### 2.1 Spec Engine

**Ответственность:** Жизненный цикл спецификации — от промта пользователя до структурированного spec.

**API:**

```python
class SpecEngine:
    def generate(prompt: str) -> str:
        """Сгенерировать goals.md из промта пользователя."""

    def validate(goals_path: str) -> ValidationResult:
        """Валидировать структуру goals.md (F-XXX, AC-XXX, Data Models, API Contracts)."""

    def approve(goals_path: str) -> None:
        """Human gate: постановить spec на согласование."""

    def parse(goals_path: str) -> StructuredSpec:
        """Парсить goals.md в структурированный spec (F-XXX → requirements, AC-XXX → criteria)."""
```

**Input:** `prompt: str`  
**Output:** `StructuredSpec`

---

### 2.2 Workflow Engine

**Ответственность:** Управление состоянием пайплайна — фазы, задачи, transitions, invariants.

**API:**

```python
class WorkflowEngine:
    def start(phase: str) -> None:
        """Начать фазу."""

    def next() -> Phase | None:
        """Найти следующую готовую фазу (pending, deps completed)."""

    def complete(phase: str, judge_passed: bool) -> None:
        """Завершить фазу (требует judge_passed=true)."""

    def rollback(phase: str, reason: str) -> None:
        """Откатить фазу (по решению Judge Engine)."""
```

**Invariants:**

| ID | Правило |
|----|---------|
| INV1 | implement-spec-stage не может быть active без tasks |
| INV2 | write-tests не может начаться пока implement не completed |
| INV3 | completed phase требует все tasks completed |
| INV4 | pending phase не может иметь completed tasks |
| INV5 | task_cycle не может начаться пока decompose не completed |
| INV6 | complete не может наступить пока все phases не completed |

---

### 2.3 OODA Runtime

**Ответственность:** Выполнение observe/orient/decide/act cycle для каждой задачи.

**API:**

```python
class OODARuntime:
    def execute(task: Task) -> OODAResult:
        """Запустить OODA cycle для задачи."""

    def resume(task_id: str) -> OODAResult:
        """Возобновить прерванную задачу."""

    def interrupt(task_id: str) -> None:
        """Прервать выполняющуюся задачу."""
```

**Step Mappings:**

| Step | Agents | Output |
|------|--------|--------|
| analyst | @observe → @orient | architecture.md |
| dev | @decide → validate → @act | dev-summary.md |
| tester | @decide → validate → @act | tester-summary.md |

---

### 2.4 Knowledge Layer

**Ответственность:** Предоставление контекста для OODA agents. Пассивный слой — ничего не решает и не управляет.

**API:**

```python
class KnowledgeLayer:
    def search(query: str, scope: str = "all") -> list[Knowledge]:
        """Поиск по базе знаний (全文, semantic, title)."""

    def retrieve(context_type: str, params: dict) -> Context:
        """Получить контекст определённого типа (architecture, best_practice, reference)."""
```

**Внутренние компоненты:**

| Компонент | Ответственность |
|-----------|----------------|
| MCP | Протокол доступа к инструментам |
| Obsidian | Хранение и навигация по документам |
| OHS | Гибридный поиск (BM25 + fuzzy + vectors) |
| RAG | Retrieval Augmented Generation |
| GraphRAG | Граф связей между документами |
| Vector DB | Эмбеддинги для semantic search |
| Docs | Статьи, тезисы, стенограммы |

---

### 2.5 Memory Layer

**Ответственность:** Хранение истории, контекста и накопленных знаний. Отделена от Knowledge Layer, потому что память — это не только знания.

**API:**

```python
class MemoryLayer:
    def store(entry: MemoryEntry) -> None:
        """Сохранить запись в память."""

    def load(query: str, scope: str = "project") -> list[MemoryEntry]:
        """Загрузить записи из памяти по запросу."""

    def summarize(scope: str, depth: str = "brief") -> str:
        """Получить суммаризацию памяти (brief/detailed/full)."""
```

**Типы памяти:**

| Тип | Описание |
|-----|----------|
| project_history | История проекта (что было сделано) |
| judge_history | Предыдущие решения Judge Engine |
| iterations | Предыдущие итерации пайплайна |
| decisions | ADR и архитектурные решения |
| long_term | Long-term memory (факты, связи) |
| user_preferences | Предпочтения пользователя |
| learned_patterns | Выученные паттерны (успешные/неуспешные) |

---

### 2.6 Judge Engine

**Ответственность:** Оценка результатов и определение следующего шага.

**API:**

```python
class JudgeEngine:
    def evaluate(response: str, context: str, spec: str) -> Verdict:
        """Полная оценка: structural + semantic + rule-based."""

    def score(response: str, rubric: Rubric) -> Score:
        """Оценка по конкретному rubric."""

    def route(verdict: Verdict) -> RouteAction:
        """Определить следующий шаг: repeat / revise / retask / continue."""
```

**Внутренние judges:**

| Judge | Тип | Описание |
|-------|-----|----------|
| Structural Judge | Deterministic | F-XXX coverage, AC completeness |
| Semantic Judge | AI-based | IEEE 29148, custom rubrics |
| Rule Judge | Deterministic | Invariants, gate conditions |
| DeepEval Adapter | Optional | Интеграция с DeepEval (опционально) |
| Custom Rubrics | Configurable | Project-specific criteria |

**Verdict:**

```python
@dataclass
class Verdict:
    overall: str           # PASS | PASS_WITH_CONCERNS | FAIL
    scores: dict[str, float]  # {judge_name: score}
    failures: list[str]    # список причин FAIL
    confidence: float      # 0.0 - 1.0
```

**RouteAction:**

```python
@dataclass
class RouteAction:
    target: str            # "ooda" | "spec" | "workflow"
    reason: str            # описание причины
    task_id: str | None    # ID задачи (для retask)
    phase_id: str | None   # ID фазы (для rollback)
```

---

## 3. Event Bus (Extension Point)

**Статус:** Не реализуется сейчас. Архитектура предусматривает.

### События

| Событие | Источник | Описание |
|---------|----------|----------|
| `spec.generated` | Spec Engine | goals.md сгенерирован |
| `spec.validated` | Spec Engine | goals.md прошёл валидацию |
| `spec.approved` | Spec Engine | Human gate пройден |
| `workflow.started` | Workflow Engine | Фаза начата |
| `workflow.completed` | Workflow Engine | Фаза завершена |
| `workflow.rollback` | Workflow Engine | Фаза откачена |
| `task.started` | OODA Runtime | Задача начата |
| `task.interrupted` | OODA Runtime | Задача прервана |
| `task.completed` | OODA Runtime | Задача завершена |
| `knowledge.requested` | OODA Runtime | Запрос контекста |
| `knowledge.retrieved` | Knowledge Layer | Контекст получен |
| `memory.stored` | Memory Layer | Запись сохранена |
| `memory.loaded` | Memory Layer | Записи загружены |
| `judge.evaluated` | Judge Engine | Оценка выполнена |
| `judge.routed` | Judge Engine | Следующий шаг определён |

### Подписка (когда будет реализован)

```python
class EventBus:
    def subscribe(event: str, handler: Callable) -> None:
        """Подписаться на событие."""

    def publish(event: str, data: dict) -> None:
        """Опубликовать событие."""
```

---

## 4. Interfaces Between Subsystems

### Request/Response Types

```python
from dataclasses import dataclass
from enum import Enum

# === Spec Engine ===

@dataclass
class StructuredSpec:
    requirements: list[Requirement]    # F-XXX
    acceptance_criteria: list[AC]      # AC-XXX
    data_models: list[DataModel]
    api_contracts: list[APIContract]
    scope: Scope

@dataclass
class Requirement:
    id: str               # F-001
    title: str
    description: str
    priority: str         # must | should | could | nice
    dependencies: list[str]

@dataclass
class AC:
    id: str               # AC-001
    requirement_id: str   # F-001
    description: str
    verifiable: bool

@dataclass
class ValidationResult:
    valid: bool
    errors: list[str]
    warnings: list[str]

# === Workflow Engine ===

@dataclass
class Phase:
    id: str               # plan-release
    title: str
    description: str
    status: str           # pending | in_progress | completed | failed
    depends_on: list[str]
    tasks: list[Task]

@dataclass
class Task:
    uuid: str
    title: str
    description: str
    status: str           # pending | in_progress | completed | blocked | failed
    assigned_role: str    # analyst | developer | tester
    spec_ref: str         # F-001
    branch: str | None
    dependencies: list[str]

# === OODA Runtime ===

@dataclass
class OODAResult:
    task_id: str
    step: str             # analyst | dev | tester
    success: bool
    outputs: dict[str, str]  # {artifact_name: file_path}
    summary: str

# === Knowledge Layer ===

@dataclass
class Knowledge:
    id: str
    source: str           # file path or URL
    content: str
    score: float          # relevance score
    metadata: dict

@dataclass
class Context:
    context_type: str     # architecture | best_practice | reference
    items: list[Knowledge]
    summary: str

# === Memory Layer ===

@dataclass
class MemoryEntry:
    id: str
    type: str             # project_history | judge_history | iterations | etc.
    content: str
    timestamp: str
    metadata: dict

# === Judge Engine ===

@dataclass
class Verdict:
    overall: str          # PASS | PASS_WITH_CONCERNS | FAIL
    scores: dict[str, float]
    failures: list[str]
    confidence: float

@dataclass
class Score:
    value: float          # 0.0 - 1.0
    breakdown: dict[str, float]
    judge: str

@dataclass
class RouteAction:
    target: str           # ooda | spec | workflow
    reason: str
    task_id: str | None
    phase_id: str | None

@dataclass
class Rubric:
    name: str
    criteria: list[RubricCriterion]

@dataclass
class RubricCriterion:
    id: str
    label: str
    weight: int           # 1-5
    scale: int            # 1-5
    pass_threshold: int   # 1-5
    critical: bool
```

### Error Handling

```python
class CodeAIError(Exception):
    """Base exception for all CodeAI errors."""
    pass

class SpecError(CodeAIError):
    """Spec Engine errors (validation, generation)."""
    pass

class WorkflowError(CodeAIError):
    """Workflow Engine errors (invariant violation, invalid transition)."""
    pass

class OODAError(CodeAIError):
    """OODA Runtime errors (agent failure, timeout)."""
    pass

class KnowledgeError(CodeAIError):
    """Knowledge Layer errors (search failure, MCP error)."""
    pass

class MemoryError(CodeAIError):
    """Memory Layer errors (storage failure, corruption)."""
    pass

class JudgeError(CodeAIError):
    """Judge Engine errors (evaluation failure, rubric not found)."""
    pass
```

---

## 5. Migration Notes

### Создаётся

| Файл | Содержание |
|------|------------|
| `docs/architecture/CORE_RUNTIME.md` | Этот документ |
| `docs/architecture/TECH_STACK.md` | Technology Stack |
| `scripts/core/__init__.py` | Package init |
| `scripts/core/types.py` | Все dataclasses и типы |
| `scripts/core/spec_engine.py` | Spec Engine stub |
| `scripts/core/workflow_engine.py` | Workflow Engine stub |
| `scripts/core/ooda_runtime.py` | OODA Runtime stub |
| `scripts/core/knowledge_layer.py` | Knowledge Layer stub |
| `scripts/core/memory_layer.py` | Memory Layer stub |
| `scripts/core/judge_engine.py` | Judge Engine stub |
| `scripts/core/event_bus.py` | Event Bus stub (extension) |
| `scripts/core/errors.py` | Exception hierarchy |

### Не трогается

| Файл | Причина |
|------|---------|
| `scripts/build-loop/*.sh` | Существующий pipeline |
| `scripts/workflow/*.sh` | Существующий OODA orchestration |
| `scripts/*.py` | Существующие скрипты |
| `.mcp.json` | Существующая интеграция |
| `AGENTS.md` | Существующая конфигурация |
| `scripts/build-loop/docs/` | База знаний |
| `scripts/build-loop/workflow-template/` | Существующий шаблон |
