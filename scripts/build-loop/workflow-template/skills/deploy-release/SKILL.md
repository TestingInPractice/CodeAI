---
name: deploy-release
description: >
  Фаза 5 workflow: локальная проверка, smoke-тесты, отчёт.
  Выполняется в локальном окружении (не на сервере).
  Triggers: "deploy locally", "verify release", "run smoke tests",
  "generate report".
type: workflow
step: 5
---

# Deploy Release — Локальная проверка релиза

## Workflow Contract

entry:
  artifacts:
    - .workflow/state.json
    - CHANGELOG.md
    - .infra/ (конфиги)
    - main branch
  condition: >
    state.phase == "deploy-release" AND
    state.status == "in_progress" AND
    state.integrate_release.release_version != null

exit:
  condition: Health check пройден, smoke-тесты зелёные, отчёт сгенерирован
  artifacts:
    - RELEASE_REPORT.md
    - state.deploy_release.bugs (если есть)

next_skill: null (конечная фаза)

---

## Контекст

Subagent читает **только**:
- `state.deploy_release` (target_env, config_path, report_path, bugs)
- `state.integrate_release` (release_version, changelog_path)
- `CHANGELOG.md` — только последняя секция (~10 строк)
- `.infra/` — конфиги для запуска

Не читает:
- `docs/specs/` (весь)
- `contracts/` (весь)
- `task.md` (весь)
- `state.plan_release`, `state.implement_spec_stage`, `state.write_tests`

Context budget: ≤2K токенов. Если превышает — остановись и сообщи оркестратору.

---

## Алгоритм

### Шаг 1: Health check

```bash
git checkout main && git pull --ff-only
```

Проверь:
- Ветка `main` существует
- Нет незакоммиченных изменений
- Последний коммит совпадает с созданным тегом

Если что-то не так → верни `BLOCKED` с деталями.

### Шаг 2: Финальная верификация

```bash
# lint
npm run lint 2>&1 || ruff check . 2>&1

# typecheck
npm run typecheck 2>&1 || mypy . 2>&1

# tests
npm test 2>&1 || pytest . 2>&1
```

Все три должны пройти.
Если нет → верни `BLOCKED` с выводом ошибок.

### Шаг 3: Локальный запуск и smoke-тесты

Если в `.infra/` есть `docker-compose.yml`:

```bash
cd .infra && docker-compose up -d && sleep 3 && docker-compose ps
```

Выполни smoke-тесты:

```bash
# health endpoint
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health

# любой доступный smoke
pytest tests/smoke/ -v 2>&1 || echo "no smoke tests dir"
```

Если smoke-тест выявил проблему → запиши в `deploy_release.bugs[]`:

```json
{
  "id": "BUG-001",
  "description": "POST /api/login returns 500",
  "status": "open"
}
```

Если docker-compose нет — пропусти шаг, в отчёте укажи `smoke: skipped`.

### Шаг 4: Отчёт

Создай `RELEASE_REPORT.md` в корне проекта:

```markdown
# Release {release_version}

- **Дата:** {YYYY-MM-DD}
- **Ветка:** main
- **Изменения:** {N} задач
- **Changelog:** CHANGELOG.md

## Верификация

| Проверка | Статус |
|----------|--------|
| lint     | passed / failed |
| typecheck| passed / failed |
| tests    | {M} passed / {F} failed |
| coverage | {X}% |
| smoke    | passed / skipped / failed |

## Баги

{bugs[] если есть, иначе "Нет"}
```

Запиши `state.deploy_release.report_path = "RELEASE_REPORT.md"`.
Установи `state.deploy_release.target_env = "local"`.

### Формат вывода

```
STATUS: DONE | DONE_WITH_CONCERNS
SUMMARY: Release {release_version}: smoke {status}, {N} bugs
EVIDENCE:
  - RELEASE_REPORT.md
  - CHANGELOG.md
  - tag {release_version}
```
