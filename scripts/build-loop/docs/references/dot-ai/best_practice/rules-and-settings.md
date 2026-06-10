# Rules и Settings — условные инструкции и конфигурация

> **Дата:** 2026-05-07
> **Версия:** 1.0
> **Источник:** [rules.md](rules.md) (эффективность инструкций), [hooks.md](hooks.md) (детерминированный enforcement)
> **Библиография:** [summary.md](summary.md#54-библиография)

---

Rules (`.claude/rules/`) — условные инструкции, загружаемые при совпадении glob-паттерна с текущим файлом. Settings (`settings.json`, `settings.local.json`) — детерминированная конфигурация: env-переменные, модель, разрешения. Вместе с CLAUDE.md они образуют трёхуровневую иерархию: общие принципы → контекстные инструкции → детерминированные настройки.

## 1.1 Rules с paths-gating

Path-gated rules — доминирующий подход к условной загрузке инструкций. Правило активируется только при работе с файлами, совпадающими с glob-паттерном `[L2]`.

**Frontmatter правила:**

```yaml
---
paths:
  - "src/**/*.py"
  - "tests/**/*.py"
---

Тело правила: инструкции, которые модель получит
при работе с совпадающими файлами.
```

**Naming конвенции:**

| Паттерн | Пример | Когда использовать |
|---------|--------|-------------------|
| `{область}-{тип}.md` | `python-style.md` | Языко-специфичные правила |
| `{область}-{тип}.md` | `frontend-react.md` | Фреймворк-специфичные |
| `{действие}.md` | `testing-rules.md` | Задача-специфичные |
| `{платформа}.md` | `docker-rules.md` | Инфраструктурные |

**Scope правил:**

| Scope | Расположение | Применение |
|-------|-------------|-----------|
| **Project** | `.claude/rules/*.md` | Правила конкретного проекта |
| **User** | `~/.claude/rules/*.md` | Персональные правила для всех проектов |
| **Enterprise** | Managed policy | Корпоративные ограничения, нельзя переопределить |

**Приоритизация:** Enterprise > CLI args > project > user `[L2]`.

**Glob-паттерны — практические примеры:**

```yaml
# Python-правила для всего Python-кода
paths:
  - "**/*.py"

# Frontend-правила только для React-компонентов
paths:
  - "src/components/**/*.tsx"
  - "src/pages/**/*.tsx"

# Infrastructure-правила для Docker и CI
paths:
  - "Dockerfile"
  - "docker-compose*.yml"
  - ".github/workflows/*.yml"

# Тестовые правила
paths:
  - "tests/**/*.py"
  - "test_*.py"
```

## 1.2 Содержимое правила

**Структура тела правила:**
1. Контекст — что это за правило и когда применяется (1–2 строки)
2. Инструкции — конкретные правила поведения (5–7 пунктов)
3. Исключения — когда правило НЕ применяется (если есть)

**Лимит размера:** правило ≈ sweet spot 500–2,000 токенов, ≤200 строк. Слишком длинное правило снижает compliance `[L1]` `[L2]`.

**Пример 1: Python-style правило**

```yaml
---
paths:
  - "**/*.py"
---

## Python конвенции

- Типизация: все функции с type hints, возвращаемый тип обязателен
- Импорты: `from package.module import Class`, не `from package import *`
- Docstrings: только для public API, одно предложение
- Тесты: `pytest` с `@pytest.fixture` для setup
- Название файлов: `snake_case.py`
```

**Пример 2: Frontend-React правило**

```yaml
---
paths:
  - "src/components/**/*.tsx"
---

## React конвенции

- Компоненты: functional components с TypeScript, не class components
- Props: отдельный `type Props = { ... }` перед компонентом
- State: `useState` для локального, external store для глобального
- Стили: CSS Modules, не inline styles
- Название файлов: `PascalCase.tsx`
```

**Пример 3: Infrastructure правило**

```yaml
---
paths:
  - "Dockerfile"
  - "docker-compose*.yml"
---

## Docker конвенции

- Базовый образ: официальные с pin-версией (`python:3.12-slim`, не `python:latest`)
- Layers: минимизировать количество, grouping по частоте изменений
- .dockerignore: всегда включать `.git`, `__pycache__`, `.env`
- Compose: `depends_on` с `condition: service_healthy`
```

**Приоритизация правил:**
- Правила без `paths:` загружаются **всегда** (аналог CLAUDE.md) — использовать только для критичных ограничений
- Правила с `paths:` загружаются **условно** — основной механизм для контекстных инструкций
- Не дублировать: правило, уже представленное в CLAUDE.md, не нужно повторять в rules `[L2]`

## 1.3 settings.json — конфигурация окружения

`settings.json` — детерминированная конфигурация, не зависящая от compliance модели `[L2]`.

**Расположение и scope:**

| Файл | Расположение | Scope | Что хранить |
|------|-------------|-------|-------------|
| Project settings | `.claude/settings.json` | Текущий проект | env, модель, permissions |
| User settings | `~/.claude/settings.json` | Все проекты пользователя | Персональные defaults |
| Enterprise settings | Managed policy | Организация | Корпоративные ограничения |

**Структура settings.json:**

```json
{
  "env": {
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "glm-4.5-air",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "glm-5-turbo",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "glm-5.1"
  }
}
```

**env-переменные:**

| Переменная | Назначение | Пример |
|-----------|-----------|--------|
| `ANTHROPIC_DEFAULT_HAIKU_MODEL` | Модель для субагентов | `glm-4.5-air` |
| `ANTHROPIC_DEFAULT_SONNET_MODEL` | Модель по умолчанию | `glm-5-turbo` |
| `ANTHROPIC_DEFAULT_OPUS_MODEL` | Модель для сложных задач | `glm-5.1` |

**Правило:** env-переменные в project settings, не в CLAUDE.md. Модель может не прочитать инструкцию «используй модель X», но env-переменная гарантирует конфигурацию `[L2]`.

## 1.4 settings.local.json — разрешения

`settings.local.json` — локальные разрешения, **не коммитятся** в git (должны быть в `.gitignore`). Содержат allowlist инструментов `[L2]`.

**Структура settings.local.json:**

```json
{
  "permissions": {
    "allow": [
      "Bash(git commit:*)",
      "Bash(git status:*)",
      "Bash(uv run:*)",
      "Bash(docker:*)",
      "WebSearch"
    ]
  }
}
```

**Формат разрешений:**

| Шаблон | Значение | Пример |
|--------|---------|--------|
| `Bash(command:*)` | Все вариации команды | `Bash(git commit:*)` |
| `Bash(command)` | Точное совпадение | `Bash(ls)` |
| `ToolName` | Разрешить инструмент целиком | `WebSearch` |
| `McpServer__tool` | MCP-инструмент | `mcp__web-search-prime__web_search_prime` |

**Permission tiers:**

| Tier | Файл | Коммитится? | Применение |
|------|------|------------|-----------|
| **Enterprise** | Managed policy | — | Корпоративные ограничения (deny) |
| **Policy** | `.claude/settings.json` | Да | Project-wide permissions (allow) |
| **Local** | `.claude/settings.local.json` | Нет | Личные permissions разработчика |

**Рекомендации:**
- Минимальный allowlist: git-команды, package manager, docker
- Опасные команды (`rm -rf`, `push --force`) — не включать в allowlist
- MCP-инструменты добавлять по мере необходимости
- `settings.local.json` в `.gitignore` — каждый разработчик настраивает свой allowlist

## 1.5 Разделение ответственности

Ключевой вопрос: какие инструкции в CLAUDE.md, какие в rules, какие в settings? Иерархия определяется механизмом enforcement `[L1]` `[L2]`.

```
┌─────────────────────────────────────────────────────────────────┐
│                    ИЕРАРХИЯ КОНФИГУРАЦИИ                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  CLAUDE.md          Общие принципы, workflow, структура         │
│  (вероятностный)    Загружается всегда, переживает compaction   │
│                     ≤200 строк, 5–7 ключевых правил             │
│                                                                 │
│  .claude/rules/     Контекстные инструкции                      │
│  (вероятностный)    Загружаются при совпадении paths/glob       │
│                     Python-правила, frontend-правила, etc.      │
│                                                                 │
│  settings.json      Детерминированная конфигурация              │
│  (детерминированный) Модель, env-переменные, permissions        │
│                     Не зависит от compliance модели             │
│                                                                 │
│  Hooks              Детерминированный enforcement               │
│  (детерминированный) Блокировка операций, линтинг, валидация    │
│                     PreToolUse, PostToolUse, Stop               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Правило выбора механизма:**

| Что настраиваем | Где | Почему |
|----------------|-----|--------|
| Workflow проекта | CLAUDE.md | Критично, загружается всегда |
| Структура файлов | CLAUDE.md | Справочный контекст для каждой сессии |
| Python-конвенции | `.claude/rules/python.md` | Только при работе с .py |
| React-конвенции | `.claude/rules/frontend.md` | Только при работе с .tsx |
| Модель по умолчанию | `settings.json` | Детерминированная конфигурация |
| Разрешения на команды | `settings.local.json` | Локальные, не коммитятся |
| Блокировка rm -rf | Hook (PreToolUse) | Enforcement, не инструкция |

## 1.6 Кросс-инструментальное сравнение

| Механизм | Claude Code | Cursor | Copilot | Windsurf |
|----------|------------|--------|---------|----------|
| **Условные инструкции** | `.claude/rules/` с `paths:` frontmatter | `.cursor/rules/*.mdc` с `globs:` frontmatter | `.github/instructions/*.instructions.md` с `applyTo:` | `.windsurf/rules/` с glob matching |
| **Типы загрузки** | Always (no paths) / Conditional (paths) | Always / Auto (glob) / Agent-Requested / Manual | Всегда (repo-wide) / При совпадении glob | Всегда / Conditional |
| **Settings** | `settings.json` (env, model) + `settings.local.json` (permissions) | `settings.json` (модель, API key) | `settings.json` (модель) | `settings.json` (модель, API) |
| **Permissions** | allowlist в `settings.local.json` | IDE-level permissions | GitHub permissions | IDE-level permissions |
| **Контекстный лимит** | ≤200 строк (рекомендация) | <500 строк (рекомендация) | Нет формального лимита | 6,000 символов/файл |

**Ключевые различия:**
- **Claude Code**: `paths:` в YAML frontmatter, чёткое разделение settings/settings.local
- **Cursor**: `globs:` + `alwaysApply` + `description` в frontmatter, трёхуровневая модель загрузки
- **Copilot**: `applyTo:` в frontmatter, non-deterministic conflict resolution
- **Windsurf**: жёсткий лимит 6,000 символов/файл, cascade-интеграция

## 1.7 Чеклист

1. **Rules с `paths:` frontmatter** — контекстные инструкции загружаются только при совпадении glob
2. **≤7 правил на файл** — Curse of Instructions compliance `[L1]`
3. **Naming по области** — `python-style.md`, `frontend-react.md`, `testing-rules.md`
4. **Нет дублирования с CLAUDE.md** — общее в CLAUDE.md, контекстное в rules
5. **Нет правил без `paths:`** — кроме критичных ограничений (better → CLAUDE.md или hooks)
6. **settings.json для env и модели** — детерминированная конфигурация, не инструкции
7. **settings.local.json для permissions** — allowlist, не коммитится
8. **`.gitignore` включает `settings.local.json`** — каждый разработчик настраивает свой allowlist
9. **Минимальный allowlist** — git, package manager, docker, WebSearch
10. **Опасные команды не в allowlist** — `rm -rf`, `push --force` — только с подтверждения
11. **Иерархия соблюдена** — CLAUDE.md (общее) → rules (контекстное) → settings (детерминированное) → hooks (enforcement)
