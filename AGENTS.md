# AGENTS.md — Project Contract for CodeAI

## Purpose
This repository collects knowledge, references, and frameworks around spec-driven AI development: GStack, GSD, Superpowers, Ralph Loop, and OpenCode project setup.

## Quick reference — OpenCode setup guide

For a comprehensive walkthrough on setting up an OpenCode-powered project, see:
- @docs/opencode-guide/00-overview.md — Introduction and goals
- @docs/opencode-guide/01-quick-start.md — Installation and first config
- @docs/opencode-guide/02-project-anatomy.md — Reference repo structure
- @docs/opencode-guide/03-agents-and-skills.md — Subagents and playbooks
- @docs/opencode-guide/04-config-and-permissions.md — opencode.json and permissions
- @docs/opencode-guide/05-team-workflows.md — Plan/Build cycle, specs-first
- @docs/opencode-guide/06-mcp-and-integrations.md — MCP servers, OAuth
- @docs/opencode-guide/07-best-practices.md — Model strategy, cost, onboarding
- @docs/opencode-guide/08-development-process.md — Delivery cycles, quality gates, review
- @docs/opencode-guide/09-project-example-step-1.md — AGENTS.md template, stage-based delivery, prompts
- @docs/opencode-guide/09-project-example-step-2.md — /docs structure for online shop

## Build Loop — запуск пет-проекта

Скрипты в `scripts/build-loop/` автоматизируют полный пайплайн:

```bash
# 1. Установить инструменты и инициализировать проект
bash scripts/build-loop/build-loop.sh --project /path/to/your-project

# 2. Заполнить docs/specs/ в своём проекте (1 файл или структуру)

# 3. Декомпозировать spec на фазы
bash scripts/build-loop/build-loop.sh --project /path/to/your-project --decompose-only

# 4. Запустить Ralph Loop
bash scripts/build-loop/build-loop.sh --project /path/to/your-project --run-only
```
