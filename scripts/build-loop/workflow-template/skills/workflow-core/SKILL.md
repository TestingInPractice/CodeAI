---
name: workflow-core
description: >
  Master orchestrator skill for CodeAI Build Loop.
  Validates state, manages phase transitions, launches subagents,
  runs judges, and compacts orchestrator context.
  Triggers: "next phase", "run workflow", "validate state", "check workflow",
  "start project", "begin phase", "transition phase".
type: workflow
step: 0
---

# CodeAI Workflow Core

## Workflow Contract

entry:
  artifacts:
    - .workflow/state.json
    - .workflow/phases.json
  condition: state.json валиден по state.schema.json

exit:
  condition: state.json обновлён с новым phase/status
  artifacts:
    - .workflow/state.json (updated)

next_skill: null (оркестратор выбирает фазу по state.json)

uses:
  - workflow-validate (custom tool)

## Фазы workflow

| Фаза | Описание | Кто исполняет |
|------|----------|---------------|
| `plan-release` | Создание ТЗ, декомпозиция на задачи, issues, judge | Analyst subagent |
| `implement-spec-stage` | Последовательная реализация задач, unit-тесты, judge | Developer subagent |
| `write-tests` | Интеграционные/e2e/регрессионные тесты по ТЗ | Tester subagent |
| `integrate-release` | Changelog, merge, подготовка релиза | Orchestrator |
| `deploy-release` | Деплой на окружение, smoke-тесты, отчёт | DevOps subagent |

**Shortcut:** `apply-small-fix → integrate-release → deploy-release`

## Алгоритм работы

### Bootstrap (первый запуск)

Если state.json показывает `phase: plan-release, status: pending`:

1. Проверь, что `docs/specs/requirements.md` существует
2. Если нет — скажи пользователю: "Напиши requirements.md в docs/specs/"
3. Вызови custom tool `transition-phase` с параметрами:
   - action: start
   - phase: plan-release
4. Запусти subagent analyst (через task) с инструкциями skills/plan-release/SKILL.md:
   - Прочитай docs/specs/requirements.md
   - Создай docs/specs/goals.md, architecture.md, contracts/
   - Декомпозируй ТЗ на задачи
   - Создай GitHub Issues для каждой задачи
5. После получения результата:
   - Обнови state.json: plan_release.status = completed
   - Запусти judge-analyst (см. references/judge-rubric.md)
   - Если judge passed → переход к implement-spec-stage
   - Если есть open questions → создай issue, верни пользователю

### Основной цикл выполнения

Для каждой фазы (plan-release, implement-spec-stage, write-tests, integrate-release, deploy-release):

1. Прочитай state.json
2. Проверь entry conditions (см. config.yaml)
3. Вызови custom tool `transition-phase` (validate + lock + write)
4. Запусти subagent для этой фазы (см. skills/{phase}/SKILL.md)
5. Получи результат (см. references/subagent-protocol.md)
6. Проверь open questions — если есть, верни пользователю
7. Запусти судью (см. references/judge-rubric.md)
8. Если judge PASSED → перейди к следующей фазе
9. Если judge FAILED → верни в текущую фазу на доработку
10. Если context > 70% → выполни compaction (см. ниже)

### Компакшен контекста

Когда контекст приближается к 70%:

```
Current objective: {текущая цель}
Active phase: {phase} ({status})
Current task: {task.id if any}
State: .workflow/state.json
Phases: .workflow/phases.json
Key specs: docs/specs/*.md

Recent actions (summary):
{последние 3 действия, 1 строка каждое}

Pending:
{следующие шаги}

Do not redo:
{завершённые шаги}
```

### Shortcut: apply-small-fix

Если изменения тривиальны (фикс бага, опечатка, мелкий рефакторинг):

1. Установи `phase: apply-small-fix` через `transition-phase --action override`
2. Выполни фикс напрямую (без subagent)
3. Перейди в `integrate-release` (changelog + merge)
4. Перейди в `deploy-release`

## Правила и ограничения

1. **Пиши в state.json ТОЛЬКО через custom tool `transition-phase`**
2. **Никогда не редактируй state.json вручную**
3. **Проверяй config.yaml перед каждым переходом** — уважай разрешённые переходы
4. **Emergency override**: если emergency.active == true, можно перейти в любую фазу (для выхода из deadlock)
5. **Git (implement-spec-stage)**: каждая задача — отдельная ветка feat/{uuid}
6. **Open questions**: если subagent вернул NEEDS_CONTEXT → создай вопрос → жди ответа пользователя
7. **Приоритет инструкций**: opencode.json > AGENTS.md > этот SKILL.md > config.yaml

## Ссылки

- Subagent protocol: references/subagent-protocol.md
- Judge rubric: references/judge-rubric.md
- Transition rules: .workflow/config.yaml (после init)
- State schema: schemas/state.schema.json
- Phase skills: skills/{phase-name}/SKILL.md (создаются в соответствующих шагах)
