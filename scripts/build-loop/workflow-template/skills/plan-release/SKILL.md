---
name: plan-release
description: >
  Фаза 1 workflow: версионирование ТЗ, создание release-ветки,
  декомпозиция F-XXX на задачи, GitHub Issues, судья.
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
- `docs/specs/v*/` (предыдущие версии)
- `templates/tasks/task.md`

## Алгоритм

### Шаг 1: Определить версию

```bash
# последняя существующая версия specs
LAST_SPEC=$(ls -d docs/specs/v* 2>/dev/null | sort -V | tail -1)
if [ -z "$LAST_SPEC" ]; then
  SPEC_VERSION="v1.0.0"
else
  # сравнить requirements.md с последней версией
  if diff -q docs/specs/requirements.md "$LAST_SPEC/requirements.md" >/dev/null 2>&1; then
    echo "ТЗ не изменилось"
    SPEC_VERSION=$(basename "$LAST_SPEC")
  else
    # auto minor bump
    SPEC_VERSION=$(echo "$LAST_SPEC" | sed 's/.*v//' | awk -F. '{print "v"$1"."$2+1".0"}')
  fi
fi
```

Правила:
- Если `docs/specs/` пуст → `v1.0.0`
- Если `requirements.md` совпадает с последней версией → версия не меняется
- Если отличается → minor bump (v1.0.0 → v1.1.0)

### Шаг 2: Версионировать spec

```bash
mkdir -p "docs/specs/$SPEC_VERSION"
cp docs/specs/requirements.md "docs/specs/$SPEC_VERSION/requirements.md"
# копировать contracts/ если есть
if [ -d docs/specs/contracts ]; then
  cp -r docs/specs/contracts "docs/specs/$SPEC_VERSION/contracts"
fi
```

### Шаг 3: Создать release-ветку

```bash
# проверить, есть ли уже такая ветка
if git rev-parse --verify "release/$SPEC_VERSION" 2>/dev/null; then
  echo "Ветка release/$SPEC_VERSION уже существует"
else
  git checkout main && git pull
  git checkout -b "release/$SPEC_VERSION"
  git push origin "release/$SPEC_VERSION"
fi
```

### Шаг 4: Создать подфайлы спецификации

- `docs/specs/goals.md` — цель, scope, метрики
- `docs/specs/architecture.md` — стек, паттерны, компоненты, data flow
- `docs/specs/data-model.md` — ER-схема, поля
- `docs/specs/contracts/{name}.md` — по файлу на API-эндпоинт (если не были скопированы)

### Шаг 5: Декомпозиция F-XXX → задачи

1 F-XXX → 1+ задача. Файлы `.workflow/tasks/{uuid}.md` по шаблону.

### Шаг 6: GitHub Issues

```bash
gh issue create --title "{title}" --label "plan-release" --body "$(cat .workflow/tasks/{uuid}.md)"
```

### Шаг 7: Open Questions

Если не хватает данных → `STATUS: NEEDS_CONTEXT`.

### Шаг 8: Запустить судью

```bash
python3 scripts/evaluate_judge.py prepare --project . --rubric judge-rubrics/analyst.json
```

Если FAILED → исправь замечания, запусти снова.

### Шаг 9: Записать результат

```json
{
  "phase": "plan-release",
  "spec_version": "v1.0.0",
  "release_branch": "release/v1.0.0",
  "status": "DONE",
  "summary": "v1.0.0: spec зафиксирован, ветка создана, N задач",
  "judge_verdict": "passed",
  "judge_score": 85,
  "created_tasks": [{"uuid": "...", "title": "...", "issue_url": "..."}],
  "evidence": [
    "docs/specs/v1.0.0/requirements.md",
    "release/v1.0.0"
  ]
}
```

Статусы: `DONE`, `NEEDS_CONTEXT`.
