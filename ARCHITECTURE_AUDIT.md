# Архитектурный аудит CodeAI

Дата: 2026-07-07
Версия проекта: 1.0.0 (MANIFEST.yaml)
Тип аудита: Структурный (без изменения кода)

---

## 1. Общая схема архитектуры

```
┌──────────────────────────────────────────────────────────────┐
│                      CodeAI Build Loop                        │
│                     Knowledge + Pipeline                      │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────────────────────────────────────┐    │
│  │               Точки входа (User/Agent)                │    │
│  │  AGENTS.md (Mode A/B/C)   start-project.sh (Mode C)  │    │
│  └──────────────────────────┬───────────────────────────┘    │
│                             │                                  │
│                             ▼                                  │
│  ┌──────────────────────────────────────────────────────┐    │
│  │              Оркестратор build-loop.sh                │    │
│  │  ┌──────────┐  ┌──────────┐  ┌───────────────────┐   │    │
│  │  │ setup.sh │  │ init.sh  │  │ decompose.sh      │   │    │
│  │  └──────────┘  └──────────┘  │ → парсит goals.md  │   │    │
│  │                              │ → F-XXX → phases   │   │    │
│  │                              │ → phases.json      │   │    │
│  │                              └─────────┬─────────┘   │    │
│  │                                        │              │    │
│  │  ┌─────────────────────────────────────▼──────────┐  │    │
│  │  │           run-loop.sh (phase manager)          │  │    │
│  │  │  status │ prompt │ judge │ mark-complete       │  │    │
│  │  └─────────────────────┬──────────────────────────┘  │    │
│  │                        │                               │    │
│  │  ┌─────────────────────▼──────────────────────────┐  │    │
│  │  │       run-task.sh (task execution engine)       │  │    │
│  │  │                                                 │  │    │
│  │  │  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │  │    │
│  │  │  │ analyst  │  │   dev    │  │   tester     │  │  │    │
│  │  │  │ @observe │  │ @decide  │  │ @decide      │  │  │    │
│  │  │  │   →      │  │   →      │  │   →          │  │  │    │
│  │  │  │ @orient  │  │ @act     │  │ @act         │  │  │    │
│  │  │  │   →      │  │   →      │  │   →          │  │  │    │
│  │  │  │  Judge   │  │  Judge   │  │  Judge       │  │  │    │
│  │  │  └──────────┘  └──────────┘  └──────────────┘  │  │    │
│  │  └─────────────────────────────────────────────────┘  │    │
│  │                                                       │    │
│  │  ┌──────────────────────────────────────────────────┐ │    │
│  │  │           next-phase.sh (dependency solver)      │ │    │
│  │  │  phases.json → dependencies → next ready phase   │ │    │
│  │  └──────────────────────────────────────────────────┘ │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐    │
│  │                   Judge System                        │    │
│  │  ┌────────────────────┐  ┌─────────────────────────┐ │    │
│  │  │ llm-judge.py       │  │ evaluate_judge.py       │ │    │
│  │  │ 3 pillars:         │  │ Hybrid: Structural + AI │ │    │
│  │  │ Relevance          │  │ IEEE 29148 критерии     │ │    │
│  │  │ Faithfulness       │  │ 3 рубрики:              │ │    │
│  │  │ Context Precision  │  │ analyst/developer/tester│ │    │
│  │  └────────────────────┘  └─────────────────────────┘ │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐    │
│  │               OODA Sub-agents (opencode)              │    │
│  │  @observe → @orient → Judge (analyst)                 │    │
│  │  @decide → @act → Judge (dev)                         │    │
│  │  @decide → @act → Judge (tester)                      │    │
│  │  Артефакты: .opencode/tasks/phase-{id}/               │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐    │
│  │          Workflow Template (для новых проектов)       │    │
│  │  scripts/build-loop/workflow-template/               │    │
│  │  ┌─────────────────────────────────────────────────┐ │    │
│  │  │ 2-terminal режим: T1 (оркестратор) + T2 (исп-ль)│ │    │
│  │  │ state.json (6 фаз):                             │ │    │
│  │  │ plan-release → implement-spec-stage →           │ │    │
│  │  │ write-tests → integrate-release → deploy-release│ │    │
│  │  │ apply-small-fix (shortcut)                      │ │    │
│  │  └─────────────────────────────────────────────────┘ │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐    │
│  │             Knowledge Base (docs/)                    │    │
│  │  scripts/build-loop/docs/   docs/opencode-docs/       │    │
│  │  docs/skills/               docs/opencode-guide/      │    │
│  │  Obsidian vault (OHS search)                          │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐    │
│  │          State Machines (ДВЕ независимые)            │    │
│  │                                                       │    │
│  │  Mode C (scripts/transition.py):                     │    │
│  │    setup → spec → human_gate → decompose →           │    │
│  │    task_cycle → complete                              │    │
│  │    state: .workflow/state.json                       │    │
│  │                                                       │    │
│  │  Template (workflow-template/scripts/transition.py): │    │
│  │    plan-release → implement-spec-stage →             │    │
│  │    write-tests → integrate-release → deploy-release  │    │
│  │    state: .workflow/state.json (другой формат)       │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

---

## 2. Описание всех основных модулей

### 2.1 Корень проекта

| Файл | Назначение | Зависимости | Зависимые |
|------|-----------|-------------|-----------|
| `AGENTS.md` | Инструкция для AI-агента (точка входа) | Нет | Все скрипты (ссылается на них) |
| `README.md` | Описание проекта | Нет | Внешние пользователи |
| `OODA_DESIGN.md` | Дизайн интеграции OODA-агентов | AGENTS.md | run-task.sh |
| `.mcp.json` | MCP-сервер Obsidian Hybrid Search | obsidian-hybrid-search | AI-агенты |

### 2.2 Pipeline (scripts/)

| Модуль | Файл | Назначение |
|--------|------|------------|
| **Оркестратор** | `build-loop.sh` | Точка входа в пайплайн. Режимы: full, setup, decompose, run, status, judge |
| **Декомпозитор** | `decompose.sh` | Парсит `docs/specs/goals.md`, вытаскивает F-XXX и AC, генерирует `.build-loop/phases.json` |
| **Фазовый менеджер** | `run-loop.sh` | Управляет статусами фаз (status/prompt/judge/mark-complete). Хранит состояние в phases.json |
| **Исполнитель задач** | `run-task.sh` | Выполняет аналитик → dev → tester цикл. Режимы: --print-prompt (deprecated), --run (OODA), --judge, --complete |
| **Планировщик** | `next-phase.sh` | Определяет следующую готовую фазу с учётом зависимостей |
| **State Machine C** | `transition.py` (корень) | Управляет Mode C: setup → spec → human_gate → decompose → task_cycle → complete |
| **LLM Judge** | `llm-judge.py` | Оценивает ответы LLM по 3 столпам: Relevance, Faithfulness, Context Precision |
| **Старт проекта** | `start-project.sh` | Точка входа Mode C: клонирует workflow, инициализирует проект, создаёт state.json |

### 2.3 Workflow Template (scripts/build-loop/workflow-template/)

| Модуль | Файл | Назначение |
|--------|------|------------|
| **State Machine B** | `scripts/transition.py` | Управляет 6 фазами: plan-release → implement-spec-stage → write-tests → integrate-release → deploy-release + apply-small-fix |
| **Гибридный судья** | `scripts/evaluate_judge.py` | Структурная проверка + AI-промпт для semantic evaluation по IEEE 29148 |
| **Валидатор** | `scripts/validate_state.py` | Schema validation + invariant checks + entry/exit gates |
| **Инициализатор** | `scripts/init_workflow.py` | Деплоит шаблон workflow в новый проект |
| **Рубрики** | `judge-rubrics/analyst.json` | 8 критериев: requirements_coverage, acceptance_criteria, developer_readiness, implementation_free, atomicity, contracts_consistent, adr_recorded, no_open_questions |
| **Рубрики** | `judge-rubrics/developer.json` | 8 критериев: adr_compliance, tests_pass, implementation_free, unambiguous_implementation, ac_satisfied, code_style, no_side_effects, coverage |
| **Рубрики** | `judge-rubrics/tester.json` | 7 критериев: ac_coverage, verifiable_tests, negative_scenarios, boundary_cases, complete_coverage, integration_tests, regression |
| **Схемы** | `schemas/state.schema.json` | JSON Schema для state.json |
| **Схемы** | `schemas/phase.schema.json` | JSON Schema для phases.json |
| **Состояние** | `states/initial.json` | Начальное состояние workflow (6 фаз со статусами) |
| **Состояние** | `states/phase-template.json` | Шаблон phases.json для Andon-метрик |

### 2.4 Knowledge Base (docs/)

| Директория | Назначение | Размер |
|-----------|-----------|--------|
| `scripts/build-loop/docs/` | Основное дерево знаний: 01-frameworks, 02-mcp, 03-opencode-config, 04-best-practices, 05-architecture, 06-tools, 07-articles, 08-build-loop | ~80+ файлов |
| `docs/opencode-docs/` | Полная документация OpenCode (49+ разделов) | ~50+ файлов |
| `docs/opencode-guide/` | Гайд по настройке OpenCode-проекта | ~5+ файлов |
| `docs/skills/` | Azure SDK skills (Python, TS, Java, .NET, Rust, Foundry) | ~100+ файлов |

### 2.5 OODA Sub-agents

| Агент | Инструменты | Вывод | Роль |
|-------|------------|-------|------|
| `@observe` | grep, glob, cat | `observe-summary.md` | Сбор фактов (read-only) |
| `@orient` | cat, grep | `architecture.md` | Анализ архитектуры (read-only) |
| `@decide` | write (.md) | `plan.md` | Планирование реализации |
| `@act` | write, edit, bash | код + `dev-summary.md` | Реализация кода |

---

## 3. Сильные стороны текущей архитектуры

1. **Чёткое разделение pipeline и знаний** — `scripts/` содержит только исполняемый код, `docs/` — только знания.

2. **Три режима работы (A/B/C)** — покрывают разные сценарии: от быстрого однотерминального запуска до полного пайплайна с human gate.

3. **Мощная система судей** — двойная проверка: структурная (автоматическая) + семантическая (AI), основанная на IEEE 29148. Рубрики настраиваемы.

4. **OODA-интеграция** — 4 специализированных агента с разными инструментами и правами, контекстная изоляция между шагами.

5. **Декомпозиция из goals.md** — автоматическое создание phases.json из F-XXX требований и acceptance criteria.

6. **Управление зависимостями фаз** — `next-phase.sh` корректно обрабатывает depends_on, resume после crash, ожидание зависимостей.

7. **Atomic state transitions** — file locking + atomic writes в transition.py предотвращают race conditions.

8. **Knowledge Graph** — wikilinks, MOC-файлы, OHS-индекс, frontmatter с тегами — всё для навигации агента.

9. **Obsidian Integration** — MCP-сервер, OHS-поиск, вулт готов для человека.

---

## 4. Слабые стороны и архитектурные проблемы

### 4.1 Две независимые state machine (CRITICAL)

```
Mode C (scripts/transition.py):           Template (workflow-template/scripts/transition.py):
setup → spec → human_gate →               plan-release → implement-spec-stage →
decompose → task_cycle → complete          write-tests → integrate-release → deploy-release

Формат state.json разный!                  Формат state.json разный!
```

Оба используют `.workflow/state.json`, но с разной структурой и разными фазами. Это приводит к:
- Невозможности понять, какая state machine активна
- Путанице при запуске: `scripts/transition.py --project . --action transition` не знает о workflow-template
- Дублировании кода: две реализации `transition.py` с разными API

**Риск**: При использовании Mode C и Build Loop вместе возникает конфликт состояний.

### 4.2 Два judge-скрипта (HIGH)

| `scripts/llm-judge.py` | `scripts/build-loop/workflow-template/scripts/evaluate_judge.py` |
|------------------------|---------------------------------------------------------------|
| 3 pillars (token overlap) | Structural check + AI prompt |
| Используется run-loop.sh и run-task.sh | Используется workflow-template |
| Нет структурной проверки | Нет 3 pillars |

Оба делают похожее, но с разными API, разными рубриками и разными режимами вызова. `run-loop.sh` ожидает `scripts/judge/llm-judge.py`, а `workflow-template/AGENTS.md` ожидает `scripts/evaluate_judge.py`.

### 4.3 Дублирование transition.py (MEDIUM)

| `scripts/transition.py` | `scripts/build-loop/workflow-template/scripts/transition.py` |
|------------------------|-------------------------------------------------------------|
| Mode C: 6 фаз | Mode B: 6 фаз |
| Простая: start/transition/approve/fail/judge/set/status/human-gate | Сложная: file locking, YAML config, entry/exit gates, invariants |
| `scripts/judge-check.sh` не найдено в проекте | Есть `scripts/validate_state.py` |

### 4.4 Hardcoded paths (MEDIUM)

```bash
# run-task.sh: hardcoded /tmp paths
summary_file="/tmp/p${PHASE_ID}-analyst-summary.txt"
TASKS_DIR="$PROJECT/.opencode/tasks/phase-$PHASE_ID"
JUDGE_SCRIPT="$PROJECT/scripts/judge/llm-judge.py"  # может не существовать

# build-loop.sh: hardcoded /tmp
summary_file="/tmp/p${next}-summary.txt"
```

Если JUDGE_SCRIPT не существует, пайплайн падает. В run-task.sh есть fallback на opencode, но не для judge.

### 4.5 Смешение pipeline и знаний (MEDIUM)

Несмотря на декларацию "read-only", `scripts/build-loop/docs/` содержит и pipeline-скрипты, и знания. Это создаёт:
- Сложности с версионированием знаний отдельно от pipeline
- Риск случайного изменения знаний при работе с пайплайном
- Затруднённый merge при обновлении opencode-docs из upstream

### 4.6 OODA-агенты не привязаны к проекту (MEDIUM)

OODA-агенты определены в `~/.config/opencode/agents/`, а не в репозитории:
- Другой разработчик не может просто склонировать репозиторий и запустить — нужно настраивать агентов вручную
- Нет версионирования конфигурации агентов
- `OODA_DESIGN.md` описывает то, что может не существовать на диске

### 4.7 Циклическая зависимость run-task → run-loop (LOW)

```
run-task.sh --complete
  → run-loop.sh --mark-complete
    → (в run-loop.sh нет вызова run-task.sh, но run-loop.sh управляется build-loop.sh)
      → build-loop.sh → run-loop.sh → run-task.sh → ...
```

Прямой цикл отсутствует, но есть косвенная: `run-loop.sh` управляет фазами, а `run-task.sh` вызывает `run-loop.sh` при complete.

### 4.8 deprecated --print-prompt живёт рядом с --run (LOW)

`run-task.sh` поддерживает два режима работы: старый `--print-prompt` (ручное копирование) и новый `--run` (OODA). Это увеличивает поддерживаемый поверхность кода.

---

## 5. Потенциальные риски

| Риск | Вероятность | Влияние | Описание |
|------|------------|---------|----------|
| Конфликт state.json | Средняя | Высокое | Обе state machines пишут в `.workflow/state.json` |
| Judge не найден | Средняя | Высокое | `JUDGE_SCRIPT` в run-task.sh не проверяет существование |
| Агенты не установлены | Высокая | Среднее | `opencode run --agent` требует предварительной настройки агентов |
| Версионирование знаний | Средняя | Среднее | opencode-docs обновляются отдельно от pipeline |
| Нарушение read-only | Низкая | Среднее | AGENTS.md предупреждает не изменять файлы, но нет технической защиты |
| Совместимость opencode CLI | Средняя | Среднее | `opencode run --agent` API может измениться |

---

## 6. Расширяемость проекта

### Можно добавить без серьёзного рефакторинга:

| Изменение | Сложность | Почему |
|-----------|-----------|--------|
| **Новые типы проектов** (Web, Godot, Backend) | Низкая | Добавить новые рубрики judge и spec-template |
| **Новые AI-агенты** | Средняя | Создать агента в opencode config + добавить шаг в run-task.sh |
| **Новые источники знаний** | Низкая | Добавить директорию в docs/ и прописать в INDEX.md |
| **Новые инструменты** (MCP-серверы) | Низкая | Добавить запись в .mcp.json |
| **Новые способы поиска контекста** | Средняя | Добавить новый сервис поиска + адаптер для run-task.sh |

### Требует рефакторинга:

| Изменение | Сложность | Причина |
|-----------|-----------|---------|
| **Унификация state machine** | Высокая | Две независимые реализации с разными форматами |
| **Вынос агентов в репозиторий** | Средняя | Сейчас они в `~/.config/opencode/agents/` |
| **Унификация judge-системы** | Средняя | Два скрипта с разными API и рубриками |
| **Изоляция pipeline от знаний** | Средняя | Нужно разделить на два git-репозитория или submodules |
| **Плагинная система для инструментов** | Высокая | Сейчас всё захардкожено в shell-скриптах |

---

## 7. План развития проекта

План состоит из независимых этапов, каждый можно реализовать отдельно и протестировать без изменения всей архитектуры.

### Этап 1: Унификация judge-системы
**Цель**: Один judge-скрипт вместо двух.
- Создать `scripts/judge/` с единым API
- Объединить `llm-judge.py` (3 pillars) + `evaluate_judge.py` (structural + AI)
- Добавить поддержку обоих режимов через флаг `--mode`
- Обновить `run-task.sh` и `run-loop.sh` на единый judge
- Перенести рубрики в `scripts/judge/rubrics/`

### Этап 2: Унификация state machine
**Цель**: Одна state machine для всех режимов.
- Создать общий протокол State Machine с единым форматом state.json
- Добавить поддержку разных phase lists (Mode C vs Mode B) через конфиг
- Удалить дублирующий `transition.py`, сохранить функциональность через параметры
- Добавить миграцию существующего state.json

### Этап 3: Изоляция pipeline от знаний
**Цель**: Чистое разделение скриптов и знаний.
- Переместить `scripts/build-loop/docs/` в `docs/knowledge/`
- Создать git submodule или отдельный репозиторий для opencode-docs
- Обновить INDEX.md и AGENTS.md
- Оставить `scripts/build-loop/` только как pipeline engine

### Этап 4: Агенты в репозитории
**Цель**: Воспроизводимая настройка агентов из репозитория.
- Создать `agents/` в корне проекта
- Определить агентов как AGENTS.md-файлы
- Добавить `scripts/setup-agents.sh` для деплоя в `~/.config/opencode/agents/`
- Добавить проверку наличия агентов в `run-task.sh`

### Этап 5: Улучшение judge-системы
**Цель**: Более надёжная и гибкая оценка.
- Добавить интеграционные тесты для judge
- Поддержка кастомных рубрик через CLI
- Кэширование результатов judge
- Экспорт метрик в JSON для анализа

### Этап 6: Документация и тесты
**Цель**: Покрытие pipeline тестами.
- Unit-тесты для `transition.py` (обеих версий)
- Интеграционные тесты для `run-task.sh --run` (Mock opencode CLI)
- Тесты для `decompose.sh` (парсинг goals.md)
- Smoke-тест полного цикла Mode C

---

## 8. Заключение

CodeAI — хорошо спроектированная система с мощной философией spec-driven AI-разработки. Сильные стороны: OODA-интеграция, гибридный судья с IEEE 29148, три режима работы, управление зависимостями.

**Главные проблемы** (требуют решения перед добавлением новых возможностей):
1. Две state machine → конфликт состояний
2. Два judge-скрипта → дублирование и путаница
3. Агенты вне репозитория → невоспроизводимость

**Рекомендация**: Начать с Этапа 1 (унификация judge), затем Этап 2 (state machine). Это даст максимальный эффект при минимальных изменениях.
