# CodeAI Build Loop

> Структурированная база знаний по AI-assisted разработке: фреймворки, MCP, контекст-инжиниринг, best practices, архитектура и инструменты.

## Что это

Исследовательский проект по построению **CodeAI Build Loop** — методологии AI-assisted разработки, объединяющей:

- **Фреймворки** — GSD, DOTI, OpenSpec, Superpowers, Paul и др.
- **Контекст-инжиниринг** — как давать агенту правильный контекст, RAG, Source of Truth для знаний
- **MCP** — Model Context Protocol, инструменты и серверы
- **OpenCode & Agent Configuration** — AGENTS.md, System.md, настройка агентов
- **Best Practices** — Hermes, eval-driven development, coding agent harness
- **Архитектура AI-агентов** — multi-agent системы, пайплайны, оркестрация

## Структура

```
scripts/build-loop/docs/
├── INDEX.md                  — мастер-индекс всех материалов
├── 01-frameworks/            — GSD, DOTI, OpenSpec, Superpowers, Paul, AI news
├── 02-mcp/                   — MCP-серверы и протоколы
├── 03-opencode-config/       — OpenCode, AGENTS.md, Cursor rules
├── 04-best-practices/        — Hermes, eval-driven, context engineering
├── 05-architecture/          — Архитектурные паттерны
├── 06-tools/                 — browse.sh, Obsidian, microsoft/skills, TGS
├── 07-articles/              — Статьи и референсы
└── 08-build-loop/            — Shell-скрипты Build Loop

docs/
├── opencode-docs/            — Полная документация OpenCode (29 разделов)
├── opencode-guide/           — Гайд по настройке OpenCode-проекта
└── skills/                   — Azure SDK skills
```

## Формат материалов

Каждый источник (видео, статья, репозиторий) представлен в двух форматах:

- `*.md` — полная **стенограмма** или конспект
- `*-thesis.md` — **структурированные тезисы** для быстрого использования агентом

Ведётся на русском (с приоритетом русскоязычных источников) и английском.

## Obsidian

Проект настроен как Obsidian-ваулт. Для работы:

1. Установить Obsidian: `brew install --cask obsidian`
2. Открыть `/Users/halapinvv/Documents/Agents/CodeAI/` как ваулт
3. Использовать `INDEX.md` как точку входа

### Obsidian Hybrid Search (OHS)

Гибридный поиск по ваулту для AI-агентов и CLI: BM25 + fuzzy title + векторные эмбеддинги (Xenova/multilingual-e5-small), слияние через RRF.

**Установка:**

```bash
npm install -g obsidian-hybrid-search
```

**Использование в CLI:**

```bash
# Поиск из папки ваулта
obsidian-hybrid-search search "запрос"

# С JSON-выводом (для скриптов и агентов)
obsidian-hybrid-search search "GSD" --json --limit 5

# Режимы
obsidian-hybrid-search search --mode semantic "запрос"
obsidian-hybrid-search search --mode fulltext "запрос"
obsidian-hybrid-search search --mode title "запрос"

# Переиндексация
obsidian-hybrid-search reindex
```

**MCP-сервер** (для Claude Code / OpenCode):

Автоматически подхватывается из `.mcp.json` в корне проекта. Предоставляет 4 инструмента:
- `search` — гибридный поиск (hybrid/semantic/fulltext/title)
- `read` — чтение заметок с метаданными, ссылками и backlinks
- `reindex` — переиндексация
- `status` — статус индекса

Не требует запущенного Obsidian — индексирует файлы напрямую. Работает офлайн, без API-ключа.

**Obsidian-плагин** (для GUI):

Установить через Community Plugins → "Hybrid Search" (требует установленного CLI).

## Как использовать AGENTS.md

В корне проекта лежит `AGENTS.md` — инструкция для AI-агентов (Claude Code, OpenCode, Codex). При запуске агента в этом репозитории он будет:

- Знать структуру проекта
- Понимать, какие фреймворки и методологии доступны
- Уметь находить стенограммы и тезисы по запросу
- Использовать контекст-инжиниринг из нашей базы знаний

## Pushed to

`https://github.com/TestingInPractice/CodeAI`
