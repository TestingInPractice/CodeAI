---
name: integrate-release
description: >
  Фаза 4 workflow: merge release-ветки в main, changelog,
  тегирование, закрытие Issues, подготовка к деплою.
  Запускается в Терминале 2.
  Triggers: "integrate-release"
type: workflow
step: 4
---

# Integrate Release — Подготовка релиза (терминал 2)

## Запуск

Прочитай `.workflow/subagent-handoff.json`. Оттуда `release_branch`.

## Алгоритм

### Шаг 1: Определить версию

```bash
SPEC_VERSION=$(basename "$(ls -d docs/specs/v* 2>/dev/null | sort -V | tail -1)")
```

Версия релиза = версия spec (например, v1.0.0).
Без auto bump — версия уже определена на plan-release.

### Шаг 2: Merge release-ветки в main

```bash
git checkout main && git pull --ff-only origin main
git merge --no-ff "release/$SPEC_VERSION" -m "release: $SPEC_VERSION"
```

Если conflict → `BLOCKED`, пользователь чинит вручную.

### Шаг 3: Обновить CHANGELOG.md

Формат keepachangelog. Добавить секцию для версии.

### Шаг 4: Закрыть Issues

```bash
gh issue close {number} --comment "released in $SPEC_VERSION"
```

### Шаг 5: Git tag

```bash
git tag -a "$SPEC_VERSION" -m "Release $SPEC_VERSION"
git push origin main --tags
```

### Шаг 6: Конфиги деплоя

Проверить/создать `.infra/` с `config.json` и `env.template`.

### Шаг 7: Записать результат

```json
{
  "phase": "integrate-release",
  "release_version": "v1.0.0",
  "status": "DONE",
  "summary": "Release v1.0.0: release/v1.0.0 смержена в main, tag создан",
  "evidence": ["CHANGELOG.md", "git tag v1.0.0"]
}
```

Статусы: `DONE`, `BLOCKED`.
