---
name: deploy-release
description: >
  Фаза 5 workflow: локальная проверка, smoke-тесты, отчёт + судья.
  Запускается в Терминале 2.
  Triggers: "deploy-release", "verify deployment"
type: workflow
step: 5
---

# Deploy Release — Локальная проверка (терминал 2)

## Алгоритм

### Шаг 1: Health check

```bash
git checkout main && git pull --ff-only
```

### Шаг 2: Финальная верификация

```bash
npm run lint 2>&1 || ruff check .
npm run typecheck 2>&1 || mypy .
npm test 2>&1 || pytest .
```

### Шаг 3: Smoke-тесты

Если есть `.infra/docker-compose.yml`:
```bash
cd .infra && docker-compose up -d
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health
pytest tests/smoke/ -v
```

### Шаг 4: Отчёт

Создай `RELEASE_REPORT.md` — верификация, smoke, баги.

### Шаг 5: Запустить судью (если есть rubric)

```bash
if [ -f judge-rubrics/deploy.json ]; then
  python3 scripts/evaluate_judge.py prepare --project . --rubric judge-rubrics/deploy.json
fi
```

### Шаг 6: Записать результат

```json
{
  "phase": "deploy-release",
  "status": "DONE",
  "summary": "Release vX.Y.Z: smoke passed, отчёт создан",
  "release_version": "vX.Y.Z",
  "bugs": [],
  "evidence": ["RELEASE_REPORT.md", "CHANGELOG.md"]
}
```

Статусы: `DONE`, `DONE_WITH_CONCERNS`.
