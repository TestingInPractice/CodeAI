---
name: implement-spec-stage
description: >
  Фаза 2 workflow: реализация одной задачи.
  Для задачи: git branch → имплементация → unit-тесты →
  commit + push → issue comment.
  Запускается в Терминале 2. Одна задача — один запуск.
  Triggers: "implement {task_uuid}", "code {task_uuid}"
type: workflow
step: 2
---

# Implement Spec Stage — Разработка (терминал 2)

## Запуск

Запускается в Терминале 2 по инструкции оркестратора.
Входная точка: прочитай `.workflow/subagent-handoff.json`.

Оттуда узнаёшь:
- `task_uuid` — какую задачу делать
- `phase` — должна быть `implement-spec-stage`
- `skill_ref` — путь к этому SKILL.md

## Workflow Contract

entry:
  condition: subagent-handoff.json.task_uuid != null
  читать:
    - .workflow/tasks/{task_uuid}.md (задача с AC)
    - docs/specs/requirements.md (F-XXX из spec_ref)
    - docs/specs/architecture.md (ADR)
    - docs/specs/contracts/ (API контракты для F-XXX)

exit:
  создать:
    - реализованный код (ветка feat/{task_uuid})
    - коммит

## Алгоритм

### Шаг 1: Git branch

```bash
git checkout main && git pull
git checkout -b feat/{task_uuid}
```

### Шаг 2: Прочитать задачу

Прочитай `.workflow/tasks/{task_uuid}.md`:
- Acceptance Criteria (AC-1, AC-2...)
- Technical Notes
- spec_ref → открой соответствующий F-XXX в requirements.md

Прочитай `docs/specs/architecture.md` — следуй ADR.

### Шаг 3: Реализация

Реализуй код по AC задачи.

Правила:
- **Ничего лишнего.** Только то, что в AC задачи
- Следуй ADR из architecture.md
- Следуй стилю кода (lint + typecheck)
- Не меняй файлы вне scope задачи

### Шаг 4: Unit-тесты

Напиши unit-тесты:
- Покрытие ≥ 80% для нового кода
- Позитивные сценарии (каждый AC)
- Негативные сценарии (ошибки, граничные случаи)

```bash
pytest tests/unit/ -v
```

### Шаг 5: Проверка

```bash
# Lint
npm run lint 2>&1 || ruff check .

# Typecheck
npm run typecheck 2>&1 || mypy .

# Tests
npm test 2>&1 || pytest .
```

Всё должно проходить.

### Шаг 6: Commit + Push

```bash
git add -A
git commit -m "feat({task_uuid}): {title}

AC-1: done
AC-2: done
..."
git push origin feat/{task_uuid}
```

### Шаг 7: GitHub Issue comment

```bash
gh issue comment {issue_number} \
  --body "Implemented in $(git rev-parse HEAD)"
```

### Шаг 8: Если не может выполнить

- Внешняя зависимость не готова → `STATUS: BLOCKED`
- Не хватает информации → `STATUS: NEEDS_CONTEXT`

## Формат вывода

Запиши результат в `.workflow/subagent-handoff.json`:

```json
{
  "phase": "implement-spec-stage",
  "task_uuid": "{uuid}",
  "status": "DONE",
  "summary": "Реализована задача {title}, коммит abc1234",
  "evidence": [
    "feat/{uuid} (commit abc1234)",
    "https://github.com/.../issues/N (comment)"
  ]
}
```

Возможные статусы: `DONE`, `DONE_WITH_CONCERNS`, `BLOCKED`, `NEEDS_CONTEXT`.
