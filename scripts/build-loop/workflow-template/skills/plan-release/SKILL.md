---
name: plan-release
description: >
  Фаза 1 workflow: чтение ТЗ (docs/specs/requirements.md),
  декомпозиция F-XXX на задачи, создание документов задач,
  GitHub Issues, open questions.
  Triggers: "create tasks from spec", "decompose requirements",
  "plan release".
type: workflow
step: 1
---

# Plan Release — Аналитика и декомпозиция

## Workflow Contract

entry:
  artifacts:
    - docs/specs/requirements.md
    - .workflow/state.json
  condition: state.phase == "plan-release" AND state.status == "in_progress"

exit:
  condition: Все задачи созданы, judge PASSED
  artifacts:
    - .workflow/tasks/{uuid}.md (для каждой задачи)
    - docs/specs/goals.md
    - docs/specs/architecture.md
    - docs/specs/data-model.md
    - docs/specs/contracts/ (по файлу на эндпоинт)
    - GitHub Issues (для каждой задачи)

next_skill: implement-spec-stage (если judge PASSED)

---

## Алгоритм

### Шаг 1: Прочитать ТЗ

Прочитай `docs/specs/requirements.md`. Определи:

- **Секция 2 (Цель):** для чего проект, ключевые сценарии
- **Секция 3 (Архитектура):** стек, паттерны, компоненты, data flow
- **Секция 4 (Scope):** что делаем, что нет
- **Секция 5 (Требования):** таблица F-XXX с приоритетами
- **Секция 6 (Data Models):** сущности, поля, типы, FK
- **Секция 7 (API Contracts):** эндпоинты, методы, схемы
- **Секция 9 (Acceptance Criteria):** AC с привязкой к F-XXX
- **Секция 12 (Open Questions):** вопросы аналитика

### Шаг 2: Создать подфайлы спецификации

В `docs/specs/` создай:

- **goals.md** — выжимка цели, scope, ключевые метрики успеха
- **architecture.md** — стек, паттерны, компоненты, data flow (из секции 3)
- **data-model.md** — итоговая ER-схема, описание полей (из секции 6)
- **contracts/` — по файлу на API-эндпоинт (из секции 7):
  ```
  contracts/
  ├── auth.md           # POST /api/auth/telegram
  ├── children.md       # CRUD /api/children
  ├── games.md          # GET/POST /api/games
  └── ...
  ```
  Формат: `## {method} {path}`, request body, response body, статусы

### Шаг 3: Декомпозировать F-XXX → задачи

Правила декомпозиции:
- **1 F-XXX → минимум 1 задача**
- Если F-XXX большой → разбить на подзадачи: F-001/1, F-001/2
- У каждой задачи: title, acceptance criteria (из секции 9), spec_ref (F-XXX)

Для каждой задачи создай файл `.workflow/tasks/{uuid}.md` по шаблону `templates/tasks/task.md`.

### Шаг 4: Создать GitHub Issues

Для каждой задачи:
```
gh issue create \
  --title "{title}" \
  --label "plan-release" \
  --body "$(cat .workflow/tasks/{uuid}.md)"
```

Если `gh` недоступен, сохрани локально с `local_ref`.

Запиши issue URL / local_ref в `plan_release.issues_created` и `plan_release.tasks[].issue`.

### Шаг 5: Open Questions

После первого прохода заполни **секцию 12 (Open Questions)** в ТЗ, если:

- Не хватает информации для декомпозиции
- Архитектура неясна (не указан стек, БД)
- Противоречия в требованиях
- Непонятен scope

Формат вопроса:
```
- [ ] # OQ-{uuid}: {конкретный вопрос} | ref: {F-XXX или секция}
```

Если есть open questions → верни `STATUS: NEEDS_CONTEXT`.
Оркестратор поставит `status: waiting_human` и дождётся ответа.

После получения ответов — обнови ТЗ и пересоздай задачи.

### Формат вывода

```
STATUS: DONE | NEEDS_CONTEXT
SUMMARY: Создано N задач, M issues, O open questions
EVIDENCE:
  - .workflow/tasks/{uuid1}.md
  - .workflow/tasks/{uuid2}.md
  - https://github.com/.../issues/N
```
