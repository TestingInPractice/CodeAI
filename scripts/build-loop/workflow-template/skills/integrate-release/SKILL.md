---
name: integrate-release
description: >
  Фаза 4 workflow: слияние веток, версионирование, changelog,
  закрытие Issues, подготовка к деплою.
  Triggers: "prepare release", "merge branches", "create release",
  "integrate changes".
type: workflow
step: 4
---

# Integrate Release — Подготовка релиза

## Workflow Contract

entry:
  artifacts:
    - .workflow/state.json
    - main branch
    - feat/{uuid} ветки (из implement-spec-stage)
  condition: >
    state.phase == "integrate-release" AND
    state.status == "in_progress" AND
    state.write_tests.judge_verdict == "passed"

exit:
  condition: Все ветки слиты, CHANGELOG обновлён, tag создан, issues закрыты
  artifacts:
    - CHANGELOG.md (обновлён)
    - git tag vX.Y.Z
    - .infra/ (конфиги для деплоя)

next_skill: deploy-release (если —)

---

## Алгоритм

### Шаг 1: Определить версию

```bash
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")
echo "Последний тег: $LAST_TAG"
```

Парсинг семвера:
- По умолчанию — **minor** bump (v0.1.0 → v0.2.0)
- Если фаза пришла из `apply-small-fix` — **patch** bump (v0.1.0 → v0.1.1)
- Если в changelog есть `### Breaking` — **major** bump

```bash
# Пример: v0.1.0 → v0.2.0
NEW_VERSION=$(echo "$LAST_TAG" | awk -F. '{
  if ($3 ~ /-/) { split($3,a,"-"); print $1"."$2"."a[1]+1 }
  else { print $1"."$2+1".0" }
}')
echo "Новая версия: $NEW_VERSION"
```

Запиши `state.integrate_release.release_version = NEW_VERSION`.

### Шаг 2: Merge веток в main

Для каждой завершённой задачи из `state.implement_spec_stage.tasks[]` с `status: completed`:

```bash
git checkout main && git pull --ff-only origin main
git merge --no-ff feat/{task.uuid} -m "feat({task.uuid}): {task.title}"
```

Правила:
- `--no-ff` — regular merge, сохраняется вся история коммитов
- Если merge conflict:
  ```bash
  echo "CONFLICT в feat/{uuid}"
  ```
  → `STATUS: BLOCKED`, укажи конфликтующие файлы
  → пользователь чинит конфликт вручную
  → после фикса: `git commit && git push`

После успешного merge запиши `state.integrate_release.merge_branch = "main"`.

### Шаг 3: Обновить CHANGELOG.md

Формат [keepachangelog](https://keepachangelog.com/).

Если `CHANGELOG.md` не существует — создай.

Добавь секцию для новой версии в начало файла:

```markdown
## [{NEW_VERSION}] - {YYYY-MM-DD}

### Added
- feat({uuid}): {task.title} (#{issue.number})
- feat({uuid}): {task.title} (#{issue.number})

### Changed
- ...

### Fixed
- ...
```

Для каждой задачи из `implement_spec_stage.tasks[]`:
- `status: completed` → добавить строку в `### Added`
- Если в задаче есть ref на bug → `### Fixed`

Запиши `state.integrate_release.changelog_path = "CHANGELOG.md"`.

### Шаг 4: Закрыть GitHub Issues

Для каждой задачи с `issue.number`:

```bash
gh issue close {number} --comment "released in {NEW_VERSION}"
```

Обнови `task.issue.state = closed` в `state.implement_spec_stage.tasks[]`.

Если `gh` недоступен — запиши намерение в SUMMARY.

### Шаг 5: Git tag

```bash
git tag -a "{NEW_VERSION}" -m "Release {NEW_VERSION}"
git push origin main --tags
```

### Шаг 6: Подготовить конфиги для deploy-release

Проверь, что `.infra/` существует. Если нет — создай:

```bash
mkdir -p .infra
```

Скопируй `.env.example` в `.infra/env.template` (если существует).

Убедись, что в `.infra/` есть:
- `config.json` или `config.yaml` — параметры окружения
- `env.template` — переменные окружения (без секретов)

### Формат вывода

```
STATUS: DONE | BLOCKED
SUMMARY: Release {NEW_VERSION}: N задач смержено, changelog обновлён, tag создан
EVIDENCE:
  - CHANGELOG.md
  - git tag {NEW_VERSION}
  - https://github.com/.../issues/N (closed)
```
