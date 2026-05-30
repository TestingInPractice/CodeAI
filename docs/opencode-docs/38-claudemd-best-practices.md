# Как писать эффективный CLAUDE.md / AGENTS.md — для OpenCode

> **Источники:**
> - https://code.claude.com/docs/ru/best-practices — раздел «Напишите эффективный CLAUDE.md»
> - https://code.claude.com/docs/ru/memory — разделы «Файлы CLAUDE.md» и «Организуйте правила с помощью .claude/rules/»
> - https://opencode.ai/docs/rules — официальная документация OpenCode

---

OpenCode использует `AGENTS.md` как основной файл инструкций, с поддержкой `CLAUDE.md` как fallback. Рекомендации из документации Claude Code по наполнению CLAUDE.md **применимы** и к AGENTS.md в OpenCode.

---

## `/init` — быстрый старт

Команда `/init` сканирует кодовую базу, определяет систему сборки, тестовый фреймворк, паттерны кода и генерирует стартовый `AGENTS.md` (или улучшает существующий). Повторный `/init` дополняет файл, не перезаписывая.

---

## Что писать

Включайте только то, что агент **не может вывести из кода сам**.

| ✅ Включать | ❌ Исключать |
|---|---|
| Команды сборки/тестов | Всё, что агент поймёт из кода |
| Стиль кода (если нестандартный) | Стандартные конвенции языка |
| Инструкции по тестированию | Документацию API (ссылайтесь на файлы) |
| Архитектурные решения | Информацию, которая часто меняется |
| Особенности окружения (env vars) | Длинные объяснения и туториалы |
| Нюансы и неочевидные подводные камни | Самоочевидное вроде «пиши чистый код» |

---

## Где размещать

OpenCode загружает правила в порядке (первое совпадение побеждает):

1. **`AGENTS.md` или `CLAUDE.md`** — walk up от текущей директории до корня
2. **`~/.config/opencode/AGENTS.md`** — глобальные правила пользователя
3. **`~/.claude/CLAUDE.md`** — fallback, если нет AGENTS.md на шагах 1-2

Отключить Claude Code fallback: `export OPENCODE_DISABLE_CLAUDE_CODE=1`

---

## Референс внешних файлов

OpenCode **не парсит `@file` автоматически** (в отличие от Claude Code). Но можно указать агенту читать файлы по запросу через явные инструкции:

```markdown
# AGENTS.md
Когда встретишь @filename.md — прочитай через Read tool, только если релевантно.
Не грузи всё заранее.

## Guidelines
- Стиль кода: @docs/typescript-guidelines.md
- Паттерны React: @docs/react-patterns.md
```

**Рекомендуемый способ** — `instructions` в `opencode.json` (файлы грузятся в контекст автоматически):

```json
{
  "instructions": ["CONTRIBUTING.md", "docs/guidelines.md", "packages/*/AGENTS.md"]
}
```

---

## `instructions` в opencode.json

Киллер-фича OpenCode, которой нет в Claude Code или Codex:

- **Локальные файлы:** `"instructions": ["docs/rules/*.md"]`
- **Glob-паттерны для монорепозиториев:** `"packages/*/AGENTS.md"`
- **Remote URLs:** `"https://raw.githubusercontent.com/.../rules.md"` (таймаут 5с)
- Всё это комбинируется с AGENTS.md в один промпт

---

## Преимущества OpenCode перед Claude Code

| Аспект | OpenCode | Claude Code |
|---|---|---|
| Основной формат | AGENTS.md | CLAUDE.md |
| Fallback | CLAUDE.md | ❌ (читает только CLAUDE.md, не AGENTS.md) |
| Path-scoped rules | `instructions` массив с glob | `.claude/rules/*.md` с YAML frontmatter |
| Remote URLs | ✅ | ❌ |
| Walk up cwd | ✅ (first-match) | ✅ (merge) |
| Auto memory | ❌ (через OHS) | ✅ |
| Hooks | ❌ | ✅ |
