# Анатомия проекта

**Глава 02**

Чтобы понять, как должен выглядеть хороший OpenCode setup, полезно смотреть не на искусственные примеры, а на реальный репозиторий. В этой главе разбирается [github.com/ivanshamaev/ai-agent-codex](https://github.com/ivanshamaev/ai-agent-codex) и объясняется роль каждого OpenCode-слоя.

---

## OpenCode-слой в репозитории-примере

```
ai-agent-codex/
├─ AGENTS.md
├─ opencode.json
├─ docs/
│  └─ specs/
│     ├─ hh-market-interfaces.md
│     └─ hh-vacancies-pipeline.md
└─ .opencode/
   ├─ agents/
   │  ├─ backend-engineer.md
   │  ├─ data-analyst.md
   │  ├─ data-engineer.md
   │  ├─ frontend-engineer.md
   │  ├─ infrastructure-engineer.md
   │  ├─ project-manager.md
   │  └─ system-analyst.md
   └─ skills/
      ├─ airflow-dag-design/SKILL.md
      ├─ dbt-modeling/SKILL.md
      ├─ docker-compose-local/SKILL.md
      ├─ fastapi-async-api/SKILL.md
      ├─ metric-design/SKILL.md
      ├─ python-etl/SKILL.md
      ├─ realtime-analytics-api/SKILL.md
      └─ requirements-spec/SKILL.md
```

---

## Слой 1. `AGENTS.md`

В репозитории-примере он объясняет агенту, что это за система, какие слои считаются правильными, как организован код и какую роль играют `docs/specs`, `.opencode/agents` и `.opencode/skills`.

```
## Expected Repository Structure
- `dags/` Airflow DAG definitions only.
- `src/` Shared Python code used by DAGs and data pipelines.
- `docs/specs/` short functional and technical specs.
- `.opencode/agents/` role-based subagents.
- `.opencode/skills/` reusable domain skills.
```

## Слой 2. `opencode.json`

```
{
  "$schema": "https://opencode.ai/config.json",
  "instructions": [
    "AGENTS.md",
    "docs/specs/*.md"
  ],
  "permission": {
    "skill": {
      "*": "deny",
      "requirements-spec": "allow",
      "dbt-modeling": "allow"
    }
  }
}
```

## Слой 3. `docs/specs/`

| Файл | Что описывает | Чем помогает агенту |
|------|--------------|-------------------|
| `hh-vacancies-pipeline.md` | Source scope, pipeline flow, deduplication, raw fields, acceptance criteria | Помогает data-oriented агентам понимать ingestion и контракты |
| `hh-market-interfaces.md` | Product intent, interface surfaces, realtime semantics | Даёт API и frontend-агентам понимание продуктовой цели |

## Слой 4. `.opencode/agents/`

```
---
description: Implements ingestion, SQL, Airflow DAGs, dbt models, and Python ETL components for the data platform.
mode: subagent
temperature: 0.1
steps: 12
permission:
  bash:
    "*": allow
    "git push*": ask
---
```

## Слой 5. `.opencode/skills/`

```
---
name: requirements-spec
description: Produce concise implementation-ready requirements, assumptions, field mappings, and acceptance criteria.
compatibility: opencode
---
## What I do
- Capture business goal and scope.
- Define inputs, outputs, and grain.
- Document source-to-target mapping.
```

---

## Как эти слои работают вместе

| Слой | Роль |
|------|------|
| **AGENTS.md** | Объясняет, как мыслить о проекте |
| **opencode.json** | Определяет инструкции, permissions, инструменты |
| **docs/specs** | Хранит контракты и acceptance criteria |
| **.opencode/agents** | Раскладывает работу по ролям |
| **.opencode/skills** | Даёт domain playbooks по запросу |
