# Step 2: Project Example — Структура `/docs`

**Глава 09 — Step 2**

---

## Готовая структура `/docs` для online shop

```
/docs
  /stages
    README.md
    stage-00-foundation.md
    stage-01-catalog-mvp.md
    stage-02-auth-and-user-identity.md
    stage-03-cart-mvp.md
    stage-04-checkout-draft.md
    stage-05-payment-flow.md
    stage-06-order-history.md
    stage-07-admin-product-management.md
    stage-08-admin-order-management.md
    stage-09-search-and-ux-maturity.md
    stage-10-production-readiness.md

  /reports
    README.md
    2026-04-05-stage-00-foundation-report.md
    2026-04-08-stage-01-catalog-mvp-report.md
    2026-04-12-stage-02-auth-report.md

  /adr
    README.md
    0001-monorepo-structure.md
    0002-backend-architecture.md
    0003-frontend-data-fetching.md
    0004-auth-strategy.md
    0005-order-state-machine.md
    0006-payments-abstraction.md

  /runbooks
    README.md
    local-development.md
    release-process.md
    database-migration.md
    rollback.md
    seed-data.md
    incident-checkout-failure.md
    incident-payment-webhook-delay.md
```

**Stage file** = «что собираемся делать»
**Report** = «что реально сделали»
**ADR** = «почему выбрали такой дизайн»
**Runbook** = «как это запускать, менять и чинить»

---

## `/docs/stages/README.md`

```
# Stages

Эта папка содержит stage definitions для проекта.

Каждый файл должен описывать:
- цель этапа
- business value
- scope / out of scope
- backend/frontend/db/infra work
- acceptance criteria
- required tests
- риски
- зависимости
- deliverables

Workflow:
1. Создать или обновить stage file
2. Отдать stage агенту в режиме plan
3. После согласования — в build
4. После завершения — создать report в /docs/reports
```

---

## `/docs/reports/README.md`

```
# Stage Reports

Эта папка содержит отчеты по завершенным stages.

Принцип:
- stage file = план и рамка этапа
- report file = фактически реализованный результат

Каждый report должен содержать:
- objective
- implemented changes
- verification performed
- what was not verified
- acceptance criteria status
- known issues / tech debt
- manual QA checklist
- release notes
- recommended next stage
```

---

## `/docs/adr/README.md`

```
# Architecture Decision Records

ADR нужен, когда решение:
- влияет на несколько модулей
- может быть пересмотрено в будущем
- важно для AI-агента и разработчиков
- несет компромиссы

Формат: статус, контекст, решение, последствия, альтернативы
```

### Примеры ADR

**ADR 0001 — Monorepo Structure**
- Решение: monorepo с frontend/, backend/, db/, docs/, infra/
- Плюсы: единая точка входа, проще синхронизировать контракты
- Минусы: CI усложняется, требуется дисциплина границ

**ADR 0002 — Backend Architecture**
- Решение: модульная структура (transport → application → domain → persistence)
- Плюсы: легче тестировать, меньше смешивания concerns

**ADR 0003 — Frontend Data Fetching**
- Решение: единый слой API client + query/hooks abstraction

**ADR 0004 — Auth Strategy**
- Решение: email/password + session/refresh-token, role-based authorization

**ADR 0005 — Order State Machine**
- Явные статусы: draft → pending_payment → paid → shipped → delivered → cancelled

**ADR 0006 — Payments Abstraction**
- Payment service abstraction для смены провайдера без изменения order lifecycle

---

## `/docs/runbooks/README.md`

```
# Runbooks

Типы runbooks:
- local development
- release process
- DB migration
- rollback
- seed data refresh
- incident response
```

### local-development.md
1. Скопировать `.env.example` → `.env`
2. `docker compose up -d`
3. Применить миграции
4. Загрузить seed data
5. Запустить backend + frontend

### release-process.md
1. Stage report заполнен
2. Review pass закрыт
3. CI прогнан
4. Release notes готовы
5. Staging → manual QA → production → post-release smoke

### database-migration.md
1. Просмотреть migration diff
2. Проверить impact
3. Проверить rollback strategy
4. Local/staging → integration tests → release → health check

### rollback.md
1. Определить blast radius
2. Остановить rollout
3. Откатить application
4. Проверить critical smoke paths
5. Зафиксировать incident notes

---

## Рекомендуемая файловая дисциплина

| Когда | Что создать |
|-------|------------|
| Новый значимый этап | Stage file |
| Stage завершён | Report |
| Долгоживущее решение с альтернативами | ADR |
| Повторяемая операция | Runbook |

## Рекомендуемый порядок первых коммитов

1. `/docs/stages/README.md`
2. `/docs/stages/stage-00-foundation.md`
3. `/docs/runbooks/local-development.md`
4. `/docs/adr/0001-monorepo-structure.md`
5. `/docs/adr/0002-backend-architecture.md`
6. Stage 00 report
7. `/docs/stages/stage-01-catalog-mvp.md`

## Как использовать это в OpenCode

1. Открываете stage-01-catalog-mvp.md
2. Plan agent изучает stage file → implementation plan
3. Build agent реализует stage строго по file
4. Review agent делает критический review
5. Docs/report pass заполняет report

### Непрерывная цепочка

**Stage Definition → Build → Review → Report → Next Stage**
