# AGENTS.md — Knowledge Repository (Read-Only)

This is a **reference collection** of frameworks, tools, and workflows for spec-driven AI development.
Do NOT modify files here. Do NOT execute projects in this repo.
Use this as a knowledge source when working on external projects.

---

## Документация (все разделы)

| Раздел | Описание |
|--------|----------|
| `docs/gstack/` | GStack — role-based brainstorming, голосование CEO/Eng/Designer, browser daemon |
| `docs/superpowers/` | Superpowers — subagent-driven development, TDD, 2-stage review |
| `docs/gsd/` | GSD — борьба с context rot, декомпозиция spec на фазы |
| `docs/build-loop/` | Build Loop — оркестратор GStack → GSD → Superpower → Ralph Loop |
| `docs/obsidian/` | Obsidian Hybrid Search MCP — cross-session memory |
| `docs/astronomer-agents/` | Astronomer/agents — MCP для Airflow |
| `docs/microservices-patterns/` | 11-step microservices evolution |
| `docs/coding-agent-harness/` | 6 компонентов coding agent harness |
| `docs/test-generator-suite/` | TGS — LLM-генератор API-тестов |
| `docs/opencode-guide/` | OpenCode setup guide (9 файлов) |
| `docs/transcripts/` | Стенограммы видео |
| `docs/examples/AGENTS.md/` | 10 примеров AGENTS.md под разные сценарии |
| `scripts/build-loop/` | Скрипты для запуска Build Loop |

## AGENTS.md / CLAUDE.md и ecosystem

- @docs/opencode-docs/30-agentsmd.md — общий формат AGENTS.md
- @docs/opencode-docs/37-agentsmd-opencode.md — AGENTS.md для OpenCode
- @docs/opencode-docs/38-claudemd-best-practices.md — Claude Code / OpenCode best practices
- @docs/opencode-docs/39-cursor-rules.md — портативность AGENTS.md между инструментами
- @docs/opencode-docs/40-skillopt.md — Microsoft SkillOpt: оптимизация AGENTS.md
- @docs/opencode-docs/41-modern-web-guidance.md — Chrome Modern Web Guidance
- @docs/opencode-docs/42-codex-maxxing-patterns.md — Jason Liu patterns
- @docs/opencode-docs/43-agents-best-practices-skill.md — agents-best-practices skill
- @docs/opencode-docs/44-creating-agent-skills-video.md — создание SKILL.md

## Build Loop — запуск пет-проекта

Скрипты в `scripts/build-loop/` — для запуска на **внешнем проекте**. Не запускать в этом репозитории.

```bash
# 1. Установить инструменты и инициализировать проект
bash scripts/build-loop/build-loop.sh --project /path/to/your-project

# 2. Заполнить docs/specs/ в своём проекте (1 файл или структуру)

# 3. Декомпозировать spec на фазы
bash scripts/build-loop/build-loop.sh --project /path/to/your-project --decompose-only

# 4. Запустить Ralph Loop (требуется Claude Code)
bash scripts/build-loop/build-loop.sh --project /path/to/your-project --run-only
```
