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
- `docs/opencode-docs/` — полная OpenCode документация (01-44)
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

## OODA Subagents (встроенные opencode-агенты)

Проект использует 4 OODA-агента, определённых в `~/.config/opencode/agents/`:

| Агент | Роль | Инструменты | Вывод |
|-------|------|-------------|-------|
| `@observe` | Сбор фактов (read-only) | grep, glob, cat | observe-summary.md |
| `@orient` | Анализ архитектуры (read-only) | cat, grep | architecture.md |
| `@decide` | Планирование реализации | write (.md) | plan.md |
| `@act` | Реализация кода | write, edit, bash | код + dev-summary.md |

Внутри build-loop оркестрацию выполняет `run-task.sh --run`.
Вне build-loop можно вызывать напрямую:

- `@observe "найди все вызовы API в модуле auth"`
- `@orient "проанализируй архитектуру платежного модуля"`
- `@decide "составь план рефакторинга"`
- `@act "реализуй по плану"`

---

# Mode C — Full Pipeline (для новых проектов)

Когда пользователь говорит "сделай проект X" и даёт ссылку на этот репозиторий — следуй этому workflow.

## Фаза 0: Setup
```
bash scripts/start-project.sh \
  --project . \
  --prompt "описание проекта от пользователя" \
  --workflow-repo "https://github.com/TestingInPractice/CodeAI"
```
Что делает:
- Клонирует CodeAI в `/tmp/codeai-workflow`
- Запускает setup.sh (GStack, GSD, Superpowers)
- Запускает init.sh (docs/specs/, judge, AGENTS.md)
- Создаёт `.workflow/state.json`

## Фаза 1: Spec
Прочитай промт пользователя из `.workflow/state.json` (поле `prompt`).

Заполни `docs/specs/goals.md` по шаблону:
- Мета (версия, приоритет, статус)
- Цель (что делаем, зачем, для кого)
- Архитектура (стек, паттерны, компоненты, data flow)
- Scope / Out of Scope
- Функциональные требования (F-001, F-002, ...)
- Data Models
- API Contracts
- UI / UX
- Acceptance Criteria (AC-001 привязанные к F-XXX)
- Non-functional Requirements
- Dependencies
- Open Questions

Если GStack установлен:
```
gstack /spec
```
Иначе — заполни вручную на основе анализа промта.

После заполнения:
```
python3 scripts/build-loop/workflow-template/scripts/evaluate_judge.py prepare \
  --rubric scripts/build-loop/workflow-template/judge-rubrics/analyst.json \
  --spec docs/specs/goals.md \
  --tasks-dir "" \
  --state ""
```
Если FAIL → доработай spec.
Если PASS:
```
python3 scripts/transition.py --project . human-gate \
  --questions '["Все ли требования учтены?", "Стек технологий верный?"]'
```
Скажи пользователю: "Spec готов. Посмотри docs/specs/goals.md, задай вопросы или скажи 'утверждаю'".

Жди ответа. Когда пользователь скажет "утверждаю" или "ок":
```
python3 scripts/transition.py --project . approve
python3 scripts/transition.py --project . transition
```

## Фаза 2: Decompose
```
bash scripts/build-loop/decompose.sh --project .
```

Запусти судью над декомпозицией:
```
python3 scripts/build-loop/workflow-template/scripts/evaluate_judge.py prepare \
  --rubric scripts/build-loop/workflow-template/judge-rubrics/analyst.json \
  --spec docs/specs/goals.md
```
Если FAIL → передекомпозируй.
Если PASS:
```
python3 scripts/transition.py --project . transition
```

## Фаза 3: Task Cycle (для каждой задачи p1..pN)

Для каждой pending фазы из `.build-loop/phases.json`:

### Шаг A. Аналитик (через OODA)
```
bash scripts/workflow/run-task.sh --project . --phase <id> --step analyst --run
```
Автоматически выполняет:
1. `@observe` — ищет факты → `.opencode/tasks/phase-<id>/observe-summary.md`
2. `@orient` — анализирует архитектуру → `.opencode/tasks/phase-<id>/architecture.md`
3. Judge — проверяет результат

FAIL → исправь orient или перезапусти.
PASS → переход к разработчику.

> Если `--run` недоступен (нет opencode CLI), используй fallback:
> ```
> bash scripts/workflow/run-task.sh --project . --phase <id> --step analyst --print-prompt
> ```
> Скопируй вывод, вызови `task()`, затем judge.

### Шаг B. Разработчик (через OODA)
```
bash scripts/workflow/run-task.sh --project . --phase <id> --step dev --run
```
Автоматически выполняет:
1. `@decide` — пишет план → `.opencode/tasks/phase-<id>/plan.md`
2. Validate plan — проверка структуры
3. `@act` — реализует по плану
4. Judge — проверяет реализацию

FAIL → исправь план или перезапусти.
PASS → переход к тестировщику.

### Шаг C. Тестировщик (через OODA)
```
bash scripts/workflow/run-task.sh --project . --phase <id> --step tester --run
```
Автоматически выполняет:
1. `@decide` — пишет тест-план → `.opencode/tasks/phase-<id>/test-plan.md`
2. Validate plan — проверка структуры
3. `@act` — пишет тесты и запускает их
4. Judge — проверяет покрытие

FAIL → исправь тест-план или перезапусти.
PASS → коммит.

### Финал задачи
```
git add -A && git commit -m "p<id>: <phase name>"
git push
bash scripts/build-loop/run-loop.sh --project . --mark-complete <id>
bash scripts/build-loop/next-phase.sh --project .
```
Переход к следующей задаче.

## Фаза 4: Complete
Когда все фазы завершены — покажи итоговый отчёт.

---

## Build Loop — запуск пет-проекта (режимы A и B)

Скрипты в `scripts/build-loop/` — для запуска на **внешнем проекте**. Не запускать в этом репозитории.

### Режим A: Ralph Loop (1 терминал, task() sub-agents)
```bash
bash scripts/build-loop/build-loop.sh --project /path/to/your-project
bash scripts/build-loop/build-loop.sh --project /path/to/your-project --decompose-only
bash scripts/build-loop/build-loop.sh --project /path/to/your-project --run-only
```

### Режим B: 2-Terminal (T1+T2, state.json handoff)
См. `scripts/build-loop/workflow-template/AGENTS.md`
