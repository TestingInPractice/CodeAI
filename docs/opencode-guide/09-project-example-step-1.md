# Step 1: Project Example

**Глава 09 — Step 1**

---

## Как должен выглядеть управляемый OpenCode-проект

Не «попросить агента сделать большой проект», а «вести проект короткими управляемыми циклами».

### Главный сдвиг мышления

Не давайте агенту сразу весь проект. Давайте ему следующий контролируемый этап с четкой целью, ограниченным scope, проверкой, review и понятным следующим шагом.

### Четыре рабочих режима

| Режим | Зачем нужен |
|-------|-------------|
| **Plan** | Понять, что и как делать, зафиксировать scope, риски |
| **Build** | Сделать минимальный рабочий инкремент |
| **Review** | Проверить correctness, contract drift, missing tests |
| **Docs / Report** | Зафиксировать, что сделано и что проверено |

---

## Готовый шаблон `AGENTS.md`

```
# AGENTS.md

## Purpose
This repository is developed with AI-assisted workflows in OpenCode.
Agents working in this repo must prioritize:
- correctness
- maintainability
- explicit architecture
- testability
- safe incremental delivery
- business value per stage

Do not treat this repo as a one-shot generation task.
Work in small, reviewable increments.
```

### Working model

```
## Working model

### Default execution model
For any non-trivial task:
1. Start with a plan.
2. Limit scope to the current stage only.
3. Implement the minimum viable increment.
4. Run relevant verification.
5. Produce a concise change report.

### Stage discipline
Work must be organized into stages.
Each stage should:
- produce demonstrable value
- be testable
- be reviewable
- have clear acceptance criteria
- have clear out-of-scope boundaries

### End-to-end preference
Prefer vertical slices over layer-by-layer delivery.
For product features, prefer backend + frontend + DB + integration + tests
within the same stage.
```

### Planning rules

```
## Planning rules

Before making large or risky changes, produce a plan that includes:
- objective
- scope
- out of scope
- impacted modules
- data model changes
- API changes
- frontend changes
- risks
- verification strategy
- rollout / migration notes if applicable
```

### Code quality rules

```
## Code quality rules

### General
- Prefer simple, explicit code over clever abstractions.
- Keep functions and modules cohesive.
- Avoid hidden side effects.
- Avoid premature generalization.

### Architecture
- Respect module boundaries.
- Do not introduce circular dependencies.
- Keep business logic out of UI glue code.
- Keep transport concerns separate from domain logic.

### Change safety
- Minimize blast radius.
- Avoid unnecessary rewrites.
- Preserve backward compatibility unless explicitly allowed.
```

### Testing rules

```
## Testing rules

### Minimum expectations
For each completed stage, add or update:
- unit tests for isolated logic
- integration tests for contracts and boundaries
- end-to-end or smoke tests for critical user flows
- migration verification for DB changes

### Required mindset
Do not say "done" if code was written but not verified.
```

### DB, API, Frontend, Infra rules

```
## Database and migrations
- prefer explicit migrations
- make schema changes reversible when practical
- avoid destructive changes without explicit warning

## API and contracts
- keep contracts explicit
- preserve backward compatibility where possible
- document breaking changes clearly

## Frontend rules
- clarity, predictable state flow
- loading/error/empty states
- accessibility basics

## Infrastructure and operations
- never hardcode secrets
- prefer configuration as code
- show intended changes explicitly
```

### Verification commands

```
## Verification commands
- install deps: `pnpm install && pip install -r requirements.txt`
- backend lint: `make lint-backend`
- frontend lint: `make lint-frontend`
- typecheck: `make typecheck`
- tests: `make test-backend`, `make test-frontend`
- full check: `make check`
```

### Final response format

```
## Expected final response format
1. Summary of changes
2. Files/modules affected
3. Verification performed
4. Known risks / tech debt / assumptions
5. Manual QA steps
6. Recommended next step
```

---

## Stage Report и Stage Definition

### Полный шаблон `STAGE_REPORT.md`

```
# Stage Report

## Stage
[Stage name]

## Objective
[What this stage was supposed to achieve]

## Scope / Out of scope

## Implemented
### Backend / Frontend / Database / Infrastructure
- [change]

## Verification performed
### Automated checks run
- [command] — [result]
### Not verified
- [what could not be verified]

## Acceptance criteria status
- [criterion] — Done / Partial / Not done

## Known issues / Tech debt / Risks

## Manual QA checklist

## Release notes
### Added / Changed / Fixed / Deferred

## Recommended next stage
```

### Короткая форма

```
# Stage Summary

## Done
- ...
## Verified
- ...
## Not verified
- ...
## Risks / debt
- ...
## QA steps
- ...
## Next
- ...
```

### Шаблон Stage Definition

```
# Stage Definition

## Name / Goal / Business value

## Scope / Out of scope

## Backend / Frontend / Database / Infra work

## Acceptance criteria

## Required tests

## Risks / Dependencies

## Deliverables
```

---

## Набор промптов для OpenCode

### Prompt для `plan`

```
You are working in a controlled stage-based delivery workflow.

Task: [describe the task]

Your job now is PLAN ONLY. Do not modify files yet.

Produce a structured implementation plan with:
1. Objective, Scope, Out of scope
2. Business value
3. Impacted modules/files
4. Backend/Frontend/DB/API changes
5. Risks, Assumptions
6. Verification plan
7. Recommended implementation order
At the end: Acceptance criteria, Stage name, Blast radius
```

### Prompt для `build`

```
Implement the approved plan for the current stage.

Rules:
- stay within scope
- do not expand the task unless necessary
- prefer minimal viable implementation
- keep frontend/backend/db aligned
- update tests relevant to the change
- preserve project conventions

Required final output:
1. Summary of changes
2. Files/modules affected
3. Verification performed / Not verified
4. Known risks / tech debt / assumptions
5. Manual QA checklist
6. Recommended next step
```

### Prompt для `review`

```
Review the current changes as a strict senior engineer.

Focus on:
- correctness, maintainability, architecture drift
- missing tests, contract drift
- migration risk, edge cases
- security / auth / data integrity

Output: Critical issues / Important follow-ups / Nice-to-have / Testing gaps
```

---

## Большой пример: online shop с нуля

### Stage 0. Foundation / Bootstrap
Создать минимальный каркас: backend skeleton, frontend skeleton, DB, Docker Compose, CI.

### Stage 1. Catalog MVP
Пользователь открывает каталог и карточку товара. Product/Category schema, API, frontend.

### Stage 2. Auth & User Identity
Регистрация, вход, профиль. Signup/signin, session, protected routes.

### Stage 3. Cart MVP
Добавление в корзину, изменение количества, удаление. Cart items, subtotal.

### Stage 4. Checkout Draft
Оформление заказа: адрес, черновик заказа, серверный пересчёт.

### Stage 5. Payment Integration
Payment intent, статусы оплаты, success/failure.

### Stage 6. Order History & Account
Список заказов пользователя, детали.

### Stage 7. Admin Product Management
CRUD товаров, цены, остатка. Админка.

### Stage 8. Admin Order Management
Управление заказами: список, статусы.

### Stage 9. Search / Filters / UX Maturity
Поиск, сортировки, пагинация, улучшение состояний.

### Stage 10. Production Readiness
Observability, structured logging, metrics, release hardening.
