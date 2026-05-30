# AGENTS.md в OpenCode — инструкции для AI-агента

> **Документация:** https://opencode.ai/docs/rules/  
> **Сайт формата:** https://agents.md

---

AGENTS.md — это стандартный Markdown-файл с инструкциями для AI-агента: команды сборки, соглашения о коде, структура проекта, особенности тестирования. OpenCode читает его в каждом проекте.

---

## Инициализация: `/init`

Создаёт или обновляет `AGENTS.md` в корне проекта:

```
/init
```

`/init` сканирует код, задаёт 2–3 вопроса если нужно, и записывает:

- Команды сборки, линтинга, тестирования
- Архитектуру и структуру репозитория
- Соглашения и peculiarities
- Ссылки на существующие инструкции (Cursor, Copilot и т.д.)

Повторный `/init` улучшает файл на месте, а не перезаписывает.

---

## Два уровня правил

### Project — `AGENTS.md` в корне репозитория

Проектные правила. Фиксируется в Git — доступны всей команде.

```
my-project/
├── AGENTS.md          ← проектные инструкции
├── src/
└── ...
```

### Global — `~/.config/opencode/AGENTS.md`

Личные правила, которые не попадают в Git. Применяются во всех проектах.

```bash
mkdir -p ~/.config/opencode
```

```markdown
# ~/.config/opencode/AGENTS.md

## Мои соглашения
- Всегда спрашивай перед добавлением новых зависимостей
- Используй `pnpm`, не npm
- Пиши тесты для любой логики сложнее одного if
```

---

## Prioritet (precedence)

OpenCode загружает правила в порядке:

```
1. AGENTS.md в проекте (walk up от текущей директории)
2. ~/.config/opencode/AGENTS.md
3. ~/.claude/CLAUDE.md (если нет AGENTS.md)
```

Первый найденный файл побеждает в своей категории. Если есть `AGENTS.md` — `CLAUDE.md` игнорируется.

---

## `instructions` в opencode.json — киллер-фича

OpenCode умеет подгружать произвольные файлы инструкций через конфиг. Этого нет в Codex.

```json
{
  "instructions": ["CONTRIBUTING.md", "docs/guidelines.md"]
}
```

### Глоб-паттерны для монорепозиториев

```json
{
  "instructions": ["packages/*/AGENTS.md", "docs/*.md"]
}
```

Каждый пакет получает свои инструкции без ручного копирования.

### Remote URLs

```json
{
  "instructions": ["https://raw.githubusercontent.com/my-org/shared-rules/main/style.md"]
}
```

Полезно для общих стандартов через всю организацию. Таймаут — 5 секунд.

### Комбинируется с AGENTS.md

Все файлы из `instructions` + `AGENTS.md` смерживаются в один промпт.

---

## Референс внешних файлов

Если нужно, чтобы агент читал файлы по запросу, а не грузил всё сразу:

```markdown
# AGENTS.md
## External File Loading
Когда встретишь ссылку вида @rules/general.md — прочитай её через Read tool,
только если это релевантно текущей задаче. Не грузи всё заранее.

## Guidelines
- Стиль кода: @docs/typescript-guidelines.md
- Паттерны React: @docs/react-patterns.md
- API-дизайн: @docs/api-standards.md
```

Агент читает файлы лениво (lazy loading) — только когда нужно для конкретной задачи.

---

## Паттерны для spec-фреймворков

### Монорепозиторий с инструкциями на пакет

```json
{
  "instructions": ["packages/*/AGENTS.md"]
}
```

### ADR и spec-ы как инструкции

```json
{
  "instructions": ["docs/adr/*.md", "docs/specs/*.md"]
}
```

### Комбинация с OHS

Если `instructions` указывает на часто меняющиеся файлы, агент получит актуальную версию. Для глубокого семантического поиска по Obsidian — подключается OHS как MCP-сервер отдельно.

---

## Claude Code Compatibility

OpenCode поддерживает файлы Claude Code как fallback:

| Формат | Условие |
|--------|---------|
| `CLAUDE.md` в проекте | Если нет `AGENTS.md` |
| `~/.claude/CLAUDE.md` | Если нет `~/.config/opencode/AGENTS.md` |
| `~/.claude/skills/` | Всегда, если не отключено |

Отключить:

```bash
export OPENCODE_DISABLE_CLAUDE_CODE=1        # всё .claude
export OPENCODE_DISABLE_CLAUDE_CODE_PROMPT=1 # только CLAUDE.md
export OPENCODE_DISABLE_CLAUDE_CODE_SKILLS=1 # только skills
```

---

## Что OpenCode НЕ делает (в отличие от Codex)

| Фича Codex | В OpenCode |
|---|---|
| `AGENTS.override.md` (подмена файла на том же уровне) | ❌ |
| Walk от корня до cwd с merge снизу вверх | ❌ — только корень проекта |
| `project_doc_fallback_filenames` (кастомные имена) | ❌ |
| `project_doc_max_bytes` (лимит 32 KiB) | ❌ — нет жёсткого лимита |

Вместо этого OpenCode предлагает **`instructions` в opencode.json** — гибче, чем override-файлы.

---

## Быстрая проверка

```bash
# спросить агента, какие инструкции загружены
"Перечисли все файлы инструкций, которые ты сейчас используешь"
```

Если инструкции не применились — перезапустите OpenCode в корне проекта.
