---
name: implement-spec-stage
description: >
  Фаза 2 workflow: реализация задач из plan-release.
  Для каждой задачи: git branch → имплементация → unit-тесты →
  commit + push → issue comment. После всех задач — judge developer.
  Triggers: "implement tasks", "develop features", "code the spec",
  "start implementation".
type: workflow
step: 2
---

# Implement Spec Stage — Разработка

## Workflow Contract

entry:
  artifacts:
    - .workflow/state.json
    - .workflow/tasks/{uuid}.md (от plan-release)
    - docs/specs/requirements.md
    - docs/specs/architecture.md
    - docs/specs/data-model.md
    - docs/specs/contracts/
  condition: >
    state.phase == "implement-spec-stage" AND
    state.status == "in_progress" AND
    state.plan_release.judge_verdict == "passed"

exit:
  condition: Все задачи выполнены, каждая с judge PASSED
  artifacts:
    - реализованный код (в ветках feat/{uuid})
    - коммиты в GitHub

next_skill: write-tests (если judge PASSED)

---

## Алгоритм

### Шаг 1: Получить список задач

Прочитай `state.implement_spec_stage.tasks[]`.

Каждая задача имеет:
- `id` — порядковый номер
- `uuid` — уникальный идентификатор
- `title` — заголовок
- `status` — `pending | in_progress | completed | blocked | failed`
- `spec_ref` — ссылка на F-XXX
- `issue.url` — GitHub Issue (если создан)

Если `tasks[]` пуст — скопируй `state.plan_release.tasks[]` в `implement_spec_stage.tasks[]`,
установив каждой `status: pending`. Сообщи оркестратору.

### Шаг 2: Взять следующую pending задачу

Найди первую задачу с `status: pending`.

Установи `state.implement_spec_stage.current_task = task.uuid`.
Установи `task.status = in_progress`.

### Шаг 3: Git branch

```bash
git checkout main && git pull
git checkout -b feat/{task.uuid}
```

Установи `task.branch = feat/{task.uuid}`.

### Шаг 4: Реализация

Прочитай файл задачи `.workflow/tasks/{task.uuid}.md`. Определи:
- Acceptance Criteria (AC-1, AC-2...)
- Technical Notes
- spec_ref → открой соответствующий F-XXX в ТЗ

Прочитай `docs/specs/architecture.md` — убедись, что следуешь ADR.

Реализуй код, удовлетворяющий всем AC задачи.

Правила:
- **Ничего лишнего.** Только то, что в AC задачи
- Следуй ADR (архитектурные решения из `docs/specs/architecture.md`)
- Следуй стилю кода проекта (lint + typecheck)
- Не меняй файлы вне scope задачи

### Шаг 5: Unit-тесты

Напиши unit-тесты для реализованного кода:
- Покрытие ≥ 80% для нового кода
- Тесты на позитивные сценарии (каждый AC)
- Тесты на негативные сценарии (ошибки, граничные случаи)
- Тесты проходят: `pytest tests/` или `npm test` (по проекту)

### Шаг 6: Проверка

```bash
# Lint
npm run lint  # или ruff, flake8 и т.д.
# Typecheck
npm run typecheck  # или mypy, pyright
# Tests
npm test  # или pytest
```

Если что-то не прошло → исправь.

### Шаг 7: Commit + Push

```bash
git add -A
git commit -m "feat({task.uuid}): {task.title}

AC-1: done
AC-2: done
..."
git push origin feat/{task.uuid}
```

### Шаг 8: GitHub Issue comment

Напиши комментарий в GitHub Issue задачи со ссылкой на коммит:

```bash
gh issue comment {task.issue.number} \
  --body "Implemented in $(git rev-parse HEAD)"
```

Установи `task.issue_comment` = URL комментария.

### Шаг 9: Отметить завершение

Установи `task.status = completed`.
Установи `state.implement_spec_stage.current_task = null`.

### Шаг 10: Повторить

Вернись к шагу 2, пока все задачи не будут `completed`.

### Если задача не может быть выполнена

Если внешняя зависимость не готова → `STATUS: BLOCKED`.
Если не хватает информации → `STATUS: NEEDS_CONTEXT` (см. subagent-protocol.md).

### Формат вывода (после всех задач)

```
STATUS: DONE | DONE_WITH_CONCERNS | BLOCKED
SUMMARY: Реализовано N/M задач
EVIDENCE:
  - feat/{uuid1} (commit abc1234)
  - feat/{uuid2} (commit def5678)
  - https://github.com/.../issues/N (comment)
```
