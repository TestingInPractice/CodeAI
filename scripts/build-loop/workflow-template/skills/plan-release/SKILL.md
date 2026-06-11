---
name: plan-release
description: >
  Фаза 1 workflow: чтение ТЗ, декомпозиция F-XXX на задачи,
  создание документов, GitHub Issues, open questions + судья.
  Запускается в Терминале 2.
  Triggers: "plan-release"
type: workflow
step: 1
---

# Plan Release — Аналитика (терминал 2)

## Запуск

Прочитай `.workflow/subagent-handoff.json`.

Читать:
- `docs/specs/requirements.md`
- `templates/tasks/task.md`

## Алгоритм

### Шаг 1: Прочитать ТЗ

Прочитай `docs/specs/requirements.md`. Определи секции 2-7, 9, 12.

### Шаг 2: Создать подфайлы спецификации

- `docs/specs/goals.md` — цель, scope, метрики
- `docs/specs/architecture.md` — стек, паттерны, компоненты, data flow
- `docs/specs/data-model.md` — ER-схема, поля
- `docs/specs/contracts/{name}.md` — по файлу на API-эндпоинт

### Шаг 3: Декомпозиция F-XXX → задачи

1 F-XXX → 1+ задача. Файлы `.workflow/tasks/{uuid}.md` по шаблону.

### Шаг 4: GitHub Issues

```bash
gh issue create --title "{title}" --label "plan-release" --body "$(cat .workflow/tasks/{uuid}.md)"
```

### Шаг 5: Open Questions

Если не хватает данных → заполни секцию 12 в requirements.md.

### Шаг 6: Запустить судью

```bash
python3 scripts/evaluate_judge.py prepare --project . --rubric judge-rubrics/analyst.json
```

Если FAILED → исправь замечания, запусти снова.

### Шаг 7: Записать результат

В `.workflow/subagent-handoff.json`:

```json
{
  "phase": "plan-release",
  "status": "DONE",
  "summary": "Создано N задач, M issues",
  "judge_verdict": "passed",
  "judge_score": 85,
  "open_questions": [],
  "created_tasks": [{"uuid": "...", "title": "...", "issue_url": "..."}],
  "evidence": ["docs/specs/goals.md", ".workflow/tasks/..."]
}
```

Статусы: `DONE`, `NEEDS_CONTEXT`.
