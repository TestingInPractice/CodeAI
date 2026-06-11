---
name: integrate-release
description: >
  Фаза 4 workflow: слияние веток, версионирование, changelog,
  закрытие Issues, подготовка к деплою + судья.
  Запускается в Терминале 2.
  Triggers: "integrate-release", "create release"
type: workflow
step: 4
---

# Integrate Release — Подготовка релиза (терминал 2)

## Алгоритм

### Шаг 1: Определить версию

```bash
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")
```

- По умолчанию — **minor** bump
- Если `apply-small-fix` — **patch**
- Если в changelog есть `### Breaking` — **major**

### Шаг 2: Merge feat/{uuid} → main

Для каждой завершённой задачи:
```bash
git checkout main && git pull --ff-only origin main
git merge --no-ff feat/{uuid} -m "feat({uuid}): {title}"
```

Если conflict → `BLOCKED`, пользователь чинит вручную.

### Шаг 3: Обновить CHANGELOG.md

Формат keepachangelog. Добавить секцию для новой версии.

### Шаг 4: Закрыть Issues

```bash
gh issue close {number} --comment "released in {NEW_VERSION}"
```

### Шаг 5: Git tag

```bash
git tag -a "{NEW_VERSION}" -m "Release {NEW_VERSION}"
git push origin main --tags
```

### Шаг 6: Конфиги деплоя

Проверить/создать `.infra/` с `config.json` и `env.template`.

### Шаг 7: Записать результат

```json
{
  "phase": "integrate-release",
  "status": "DONE",
  "summary": "Release vX.Y.Z: N задач смержено, changelog обновлён, tag создан",
  "release_version": "vX.Y.Z",
  "evidence": ["CHANGELOG.md", "git tag vX.Y.Z"]
}
```

Статусы: `DONE`, `BLOCKED`.
