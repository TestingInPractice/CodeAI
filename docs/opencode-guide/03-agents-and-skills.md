# Агенты и skills

**Глава 03**

---

## Что дают встроенные агенты, а что нужно добавить самому

| Тип | Когда подходит | Примеры |
|-----|---------------|---------|
| Встроенные primary agents | Нужен основной режим работы с кодом или безопасным планированием | `build`, `plan` |
| Встроенные subagents | Нужен read-only explore или general-purpose подзадача | `explore`, `general` |
| Проектные subagents | Есть четкие роли, связанные именно с вашим проектом | `data-engineer`, `system-analyst` |

## Когда создание project-specific subagent оправдано

Новый агент нужен, когда у роли появляется устойчивый operational boundary:

- Роль решает повторяемый тип задач
- У роли есть своя инженерная логика и свои критерии хорошего результата
- Есть смысл ограничить доступ к части инструментов или команд
- Роль должна мыслить на языке конкретной предметной области проекта

### Антипаттерн

Если subagent отличается от других только названием, но не областью ответственности — он лишний. Знание лучше оставить в `AGENTS.md` или вынести в skill.

## Как выглядит сильный project subagent

```
---
description: Builds FastAPI and asyncio backend services that expose analytical data, filters, and realtime market updates over HH-based datasets.
mode: subagent
temperature: 0.1
steps: 12
permission:
  bash:
    "*": allow
    "git push*": ask
---
```

## Для чего нужны skills

Skills в OpenCode — это on-demand playbooks. Знания и инструкции, которые не должны занимать базовый контекст всегда, но очень полезны в определенных типах задач.

Например, skill по `requirements-spec` полезен не в каждой сессии, а только когда идет проработка требований.

## Как отличать rules, skills и commands

| Если сущность... | Куда класть | Почему |
|-----------------|------------|--------|
| Всегда относится к репозиторию | `AGENTS.md` или `instructions` | Должна быть доступна постоянно |
| Нужна для определенного класса задач | `.opencode/skills/` | Не стоит грузить в каждую сессию |
| Повторяемый prompt-шаблон | `.opencode/commands/` | Это shortcut для запуска сценария |

## Как выглядит сильный skill

```
---
name: docker-compose-local
description: Design a reproducible local Docker Compose setup for Airflow, PostgreSQL, and related developer workflows.
compatibility: opencode
metadata:
  audience: infrastructure-engineers
  domain: local-runtime
---
## What I do
- Define service topology and startup order.
- Recommend env vars and volume mounts.
- Keep optional services behind Compose profiles.
```

## Каталог skills в проекте-примере

**Data / platform skills:** `python-etl`, `postgres-sql`, `dbt-modeling`, `airflow-dag-design`, `metric-design`

**Delivery / product skills:** `requirements-spec`, `delivery-planning`, `fastapi-async-api`, `realtime-analytics-api`

---

## Практическое правило

Если вы не можете в одном-двух предложениях объяснить, когда subagent или skill нужен, значит он пока слишком размыт.
