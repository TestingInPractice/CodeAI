# agents-best-practices — Agent Skill по построению агентных систем

> **Репозиторий:** https://github.com/DenisSergeevitch/agents-best-practices  
> **Локальный путь:** `~/.claude/skills/agents-best-practices/`  
> **SKILL.md:** `~/.claude/skills/agents-best-practices/SKILL.md`

Provider-neutral Agent Skill для проектирования, аудита и рефакторинга агентных harness'ов. Уже установлен — OpenCode подхватывает из `~/.claude/skills/`.

---

## Структура

```
~/.claude/skills/agents-best-practices/
├── SKILL.md           ← точка входа, правила срабатывания
├── icon.jpeg
└── references/
    ├── mvp-agent-blueprint.md
    ├── architecture.md
    ├── agentic-loop.md
    ├── tools-and-permissions.md
    ├── planning-and-goals.md
    ├── workflow-orchestration.md
    ├── context-memory-compaction.md
    ├── prompt-caching-and-cost.md
    ├── skills-and-connectors.md
    ├── system-prompts-instructions.md
    ├── provider-api-patterns.md
    ├── security-evals-observability.md
    ├── agent-legibility-feedback-loops.md
    ├── checklists.md
    ├── coverage-audit.md
    └── source-links.md
```

---

## Как использовать в OpenCode

Skill срабатывает автоматически, когда разговор касается архитектуры агентов, tool permissions, планирования, контекста/памяти, MCP, evals и т.д.

Можно вызвать явно:

```
Use the agents-best-practices skill to audit this agent harness.
```

Или запросить конкретный reference:

```
Read ~/.claude/skills/agents-best-practices/references/mvp-agent-blueprint.md
and generate a blueprint for a code-review agent.
```

---

## Ключевые reference'ы

| Файл | О чём |
|---|---|
| `mvp-agent-blueprint.md` | Пошаговый шаблон MVP агента: loop, tools, launch gate |
| `agentic-loop.md` | Loop invariants, retries, budgets, termination |
| `tools-and-permissions.md` | Typed tools, risk classes, approvals |
| `planning-and-goals.md` | Planning mode и long-running goals |
| `workflow-orchestration.md` | Декомпозиция задач, пакеты, верификация |
| `context-memory-compaction.md` | Контекст, память, retrieval, compaction |
| `prompt-caching-and-cost.md` | Stable prefixes, cost-aware context |
| `skills-and-connectors.md` | Agent Skills, MCP, connectors |
| `security-evals-observability.md` | Guardrails, tracing, evals, launch gates |
| `checklists.md` | Чеклисты имплементации и аудита |

---

## Пример: MVP blueprint

Запрос:

```
Build an agent for account renewal risk.
```

Skill отвечает blueprint'ом с конкретным loop, набором tools и launch gate:

```
Core loop:
  user/task → context builder → model call → typed tool call
  → schema validation → permission check → execution or pause
  → structured observation → next step or final brief

Launch gate:
  20 historical accounts, trace review, no unapproved external sends,
  human acceptance on ≥80% of draft actions.
```

---

## Философия

1. **Harness действует, не модель** — модель предлагает; код валидирует, авторизует, выполняет, записывает
2. **Риск меняет loop** — read, draft, write, destructive — разные пути permissions
3. **Draft и commit разделены** — высокорисковые действия требуют запись approval вне промпта
4. **Контекст строится, не сбрасывается** — retrieve только нужное, preserve active state через compaction
5. **Долгая работа требует budgets** — step, time, token, cost, tool-call
6. **Повторные ошибки → фичи harness'а** — валидаторы, инструменты, evals, политики
