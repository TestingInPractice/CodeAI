# AGENTS.md — Knowledge Repository (Read-Only)

This is a **reference collection** of frameworks, tools, and workflows for spec-driven AI development.
Do NOT modify files here. Do NOT execute projects in this repo.
Use this as a knowledge source when working on external projects.

---

## 📂 Полный INDEX

Главная навигация: `scripts/build-loop/docs/INDEX.md` — база знаний с категориями, описаниями и ссылками на все файлы.

---

## Категории документации

### 01. Фреймворки AI-разработки
- `scripts/build-loop/docs/01-frameworks/` — GSD, GSD vs Paul, GSD for OpenCode, GSD vs OpenSpec, GSD & Superpowers, DOTI, AI News Digest
- `docs/opencode-docs/gsd/` — GSD методология
- `docs/opencode-docs/gstack/` — GStack
- `docs/opencode-docs/superpowers/` — Superpowers

### 02. MCP (Model Context Protocol)
- `scripts/build-loop/docs/02-mcp/` — MCP Tools (Telegram Watcher), Obsidian Hybrid Search
- `docs/opencode-docs/astronomer-agents/` — Astronomer MCP
- `docs/opencode-docs/22-mcp.md` — OpenCode MCP

### 03. OpenCode & Agent Configuration
- `scripts/build-loop/docs/03-opencode-config/` — AGENTS.md/CLAUDE.md howto, примеры, гайды
- `docs/opencode-docs/` — полная OpenCode документация (01-29)
- `docs/opencode-docs/30-agentsmd.md` — AGENTS.md формат
- `docs/opencode-docs/31-agents-ecosystem-comparison.md` — сравнение AGENTS.md/CLAUDE.md/GEMINI.md
- `docs/opencode-docs/37-agentsmd-opencode.md` — AGENTS.md в OpenCode
- `docs/opencode-docs/38-claudemd-best-practices.md` — CLAUDE.md best practices
- `docs/opencode-docs/39-cursor-rules.md` — Cursor Rules
- `docs/opencode-docs/examples/AGENTS.md/` — 10 примеров AGENTS.md
- `docs/opencode-guide/` — OpenCode setup guide

### 04. Best Practices
- `scripts/build-loop/docs/04-best-practices/` — Hermes, AI Products, Coding Agent Harness
- `docs/opencode-docs/40-skillopt.md` — SkillOpt
- `docs/opencode-docs/41-modern-web-guidance.md` — Chrome Modern Web
- `docs/opencode-docs/42-codex-maxxing-patterns.md` — Codex Maxxing
- `docs/opencode-docs/43-agents-best-practices-skill.md` — agents-best-practices
- `docs/opencode-docs/44-creating-agent-skills-video.md` — создание Agent Skills

### 05. Архитектура
- `docs/opencode-docs/microservices-patterns/` — 11-step microservices evolution
- `docs/opencode-docs/obsidian/` — Obsidian Hybrid Search
- `docs/opencode-docs/coding-agent-harness/` — 6 компонентов coding agent
- `docs/opencode-docs/test-generator-suite/` — TGS

### 06. Инструменты
- `scripts/build-loop/docs/06-tools/` — browse.sh, microsoft/skills, TGS
- `docs/skills/` — Azure SDK skills (Python, TS, Java, .NET, Rust, Foundry)

### 07. Статьи и референсы
- `scripts/build-loop/docs/01-frameworks/2025-06-07_AI-news-digest.md` — AI дайджест
- `scripts/build-loop/docs/02-mcp/obsidian-hybrid-search-ohs.md` — OHS MCP
- `scripts/build-loop/docs/03-opencode-config/AGENTS-md-examples-gist.md` — AGENTS.md examples
- `scripts/build-loop/docs/03-opencode-config/opencode-project-guide-datatalks.md` — datatalks гайд
- `scripts/build-loop/docs/06-tools/microsoft-skills.md` — microsoft/skills
- `scripts/build-loop/docs/06-tools/tgs-test-generator-suite.md` — TGS Habr

### 08. Внешние референсы (dot_ai)
- `scripts/build-loop/docs/references/dot-ai/` — docs from davjdk/dot_ai (best_practice/ + researches/, 14 files)
- `scripts/build-loop/docs/references/dot-ai/README.md` — MOC with wikilinks

### 09. Build Loop (наш проект)
- `scripts/build-loop/docs/INDEX.md` — главный INDEX
- `scripts/build-loop/` — shell-скрипты Build Loop
- `docs/opencode-docs/build-loop/49-build-loop-reference.md` — Build Loop reference

---

## Build Loop — запуск пет-проекта

Скрипты в `scripts/build-loop/` — для запуска на **внешнем проекте**. Не запускать в этом репозитории.

```bash
# 1. Установить инструменты и инициализировать проект
bash scripts/build-loop/build-loop.sh --project /path/to/your-project

# 2. Заполнить docs/specs/ в своём проекте (1 файл или структуру)

# 3. Декомпозировать spec на фазы
bash scripts/build-loop/build-loop.sh --project /path/to/your-project --decompose-only

# 4a. Ralph Loop (Claude Code — автоматически)
bash scripts/build-loop/build-loop.sh --project /path/to/your-project --run-only

# 4b. Ralph Loop (OpenCode — фаза за фазой в диалоге)
bash scripts/build-loop/decompose.sh --project /path/to/your-project
# AI читает spec, имплементирует фазу, помечает "completed" в phases.json,
# повторяет для следующей фазы.
# Команды для AI:
#   bash scripts/build-loop/next-phase.sh --project .      — узнать следующую фазу
#   bash scripts/build-loop/run-loop.sh --project . --phase <id> --print-prompt  — получить промпт фазы
# Никакого Claude CLI не нужно.
```
