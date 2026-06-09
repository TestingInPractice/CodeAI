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
2. Открыть папку `scripts/build-loop/docs/` как ваулт (или всю корневую)
3. Использовать `INDEX.md` как точку входа

## Как использовать AGENTS.md

В корне проекта лежит `AGENTS.md` — инструкция для AI-агентов (Claude Code, OpenCode, Codex). При запуске агента в этом репозитории он будет:

- Знать структуру проекта
- Понимать, какие фреймворки и методологии доступны
- Уметь находить стенограммы и тезисы по запросу
- Использовать контекст-инжиниринг из нашей базы знаний

## Pushed to

`https://github.com/TestingInPractice/CodeAI`
