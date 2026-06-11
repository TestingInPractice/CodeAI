---
name: implement-spec-stage
description: >
  Фаза 2 workflow: реализация задач в release-ветке + судья.
  Каждая задача — коммит в release/v{version}.
  Запускается в Терминале 2. Одна задача — один запуск.
  Triggers: "implement {task_uuid}"
type: workflow
step: 2
---

# Implement Spec Stage — Разработка (терминал 2)

## Запуск

Прочитай `.workflow/subagent-handoff.json`. Оттуда `task_uuid` и `release_branch`.

Читать:
- `.workflow/tasks/{task_uuid}.md`
- `docs/specs/requirements.md` (F-XXX из spec_ref)
- `docs/specs/architecture.md`
- `docs/specs/contracts/`

## Алгоритм

### Шаг 1: Переключиться на release-ветку

```bash
git checkout main && git pull
git checkout "release/{spec_version}" && git pull
```

### Шаг 2: Прочитать задачу

AC, Technical Notes, spec_ref → F-XXX в requirements.md.

### Шаг 3: Реализация

Только то, что в AC задачи. Следуй ADR. Ничего лишнего.

### Шаг 4: Unit-тесты

≥ 80% coverage. Позитивные + негативные сценарии.

### Шаг 5: Проверка

```bash
npm run lint 2>&1 || ruff check .
npm run typecheck 2>&1 || mypy .
npm test 2>&1 || pytest .
```

Всё должно проходить.

### Шаг 6: Commit + Push

```bash
git add -A && git commit -m "feat({task_uuid}): {title}"
git push origin "release/{spec_version}"
```

### Шаг 7: Issue comment

```bash
gh issue comment {number} --body "Implemented in $(git rev-parse HEAD)"
```

### Шаг 8: Запустить судью

```bash
python3 scripts/evaluate_judge.py prepare --project . --rubric judge-rubrics/developer.json
```

Если FAILED → исправь → перезапусти судью.

### Шаг 9: Записать результат

```json
{
  "phase": "implement-spec-stage",
  "task_uuid": "{uuid}",
  "status": "DONE",
  "summary": "Реализована задача {title}, commit abc1234",
  "judge_verdict": "passed",
  "judge_score": 90,
  "evidence": [
    "release/v1.0.0 (commit abc1234)",
    "https://github.com/.../issues/N"
  ]
}
```

Статусы: `DONE`, `DONE_WITH_CONCERNS`, `BLOCKED`, `NEEDS_CONTEXT`.
