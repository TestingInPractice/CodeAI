---
name: deploy-release
description: >
  Фаза 5 workflow: локальная проверка, smoke-тесты, отчёт.
  Запускается в Терминале 2.
  Triggers: "deploy-release", "verify deployment"
type: workflow
step: 5
---

# Deploy Release — Локальная проверка (терминал 2)

## Запуск

Запускается в Терминале 2 по инструкции оркестратора.
Входная точка: прочитай `.workflow/subagent-handoff.json`.

## Контекст

Читать **только**:
- CHANGELOG.md — последняя секция
- .infra/ — конфиги для запуска

Context budget: ≤2K токенов.

## Алгоритм

### Шаг 1: Health check

```bash
git checkout main && git pull --ff-only
```

Проверь:
- Ветка `main` существует
- Нет незакоммиченных изменений
- Последний коммит совпадает с тегом (если есть)

### Шаг 2: Финальная верификация

```bash
npm run lint 2>&1 || ruff check .
npm run typecheck 2>&1 || mypy .
npm test 2>&1 || pytest .
```

Все три должны пройти.

### Шаг 3: Smoke-тесты

Если есть `.infra/docker-compose.yml`:
```bash
cd .infra && docker-compose up -d && sleep 3 && docker-compose ps
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health
pytest tests/smoke/ -v 2>&1 || echo "no smoke tests dir"
```

Если проблема → запиши в `bugs[]`.

### Шаг 4: Отчёт

Создай `RELEASE_REPORT.md`:

```markdown
# Release {version}

- **Дата:** {YYYY-MM-DD}
- **Ветка:** main
- **Changelog:** CHANGELOG.md

## Верификация
| Проверка | Статус |
|----------|--------|
| lint     | passed |
| typecheck| passed |
| tests    | X passed / Y failed |
| coverage | X% |
| smoke    | passed / skipped |

## Баги
...
```

## Формат вывода

```json
{
  "phase": "deploy-release",
  "status": "DONE",
  "summary": "Release vX.Y.Z: smoke passed, отчёт создан",
  "evidence": [
    "RELEASE_REPORT.md",
    "CHANGELOG.md"
  ],
  "release_version": "vX.Y.Z",
  "bugs": []
}
```

Возможные статусы: `DONE`, `DONE_WITH_CONCERNS`.
