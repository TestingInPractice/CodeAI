---
tags: [gsd, openspec]
aliases: [GSD vs OpenSpec тезисы]
date: 2025-07-26
version: 1.0
source: 2025-07-26_GSD-vs-OpenSpec
---

> **Дата:** 2025-07-26
> **Версия:** 1.0
> **Источник:** [[2025-07-26_GSD-vs-OpenSpec]] — YouTube, "GSD vs OpenSpec — I rebuilt the same app twice"
> **Библиография:** [[../bibliography|Библиография]]


# GSD vs OpenSpec: Структурированные тезисы для работы с агентом


## 1. Сетап теста

- Одно и то же приложение (**NewWriter** — писательское комьюнити: auth, профили, истории, комментарии, DM, лидерборд)
- Один и тот же бриф (PRD)
- Одна модель: **GPT-5.5** с medium reasoning effort
- Один инструмент: **Codex CLI**
- Цель: честное сравнение spec-driven фреймворков

---

## 2. Результаты (цифры)

| Метрика | GSD | OpenSpec |
|---------|-----|----------|
| Время (elapsed) | **5ч 25м** (без учёта прерванного Claude Code старта) | **1ч 52м** |
| Токенов | **126 млн** (38 threads) | **35.3 млн** (6 threads) |
| API-эквивалент | **$104** | **$28** |
| Разница | В 3.57x больше токенов | — |

---

## 3. Философия: GSD хочет владеть проектом, OpenSpec — изменением

### GSD
- Тяжёлый lifecycle framework
- Pipeline: New Project → Discuss → Plan → Execute → Verify → Ship
- Создаёт `.planning/` с project.md, requirements.md, roadmap.md, research, phase folders, state
- Sub-agents в отдельных context windows
- Может работать в auto mode (часами)
- "GSD — это то, чем BMAD *должен был быть*"

### OpenSpec
- Лёгкий change-oriented framework
- Pipeline: Propose → Apply → Check → Archive
- Создаёт change folder с proposal.md, design.md, tasks.md, delta specs
- Нет встроенного roadmap — ты сам управляешь фазами
- "OpenSpec хочет владеть изменением, а не проектом"
- Команды: `$openspec-propose`, `$openspec-apply-change`, `$openspec-archive-change`, `$openspec-explore`

---

## 4. Сравнение по категориям (оценки автора)

| Категория | GSD | OpenSpec | Комментарий |
|-----------|-----|----------|-------------|
| Spec quality | **Выше** | Ниже | GSD создаёт более детальные артефакты |
| Plan quality | **Выше** | Ниже | Roadmap, декомпозиция на фазы |
| Implementation quality | **Выше** | Ниже | Лучше helper separation, конфигурация |
| First result | Ниже | **Выше** | OpenSpec показал работающее приложение раньше |
| Polish cost | Ниже | **Выше** | Быстрее итерации, легче править |
| Developer experience | Ниже | **Выше** | Fast loop, меньше waiting |
| Adaptability | **Выше** | Ниже | GSD лучше подстраивается под изменения |
| Verification discipline | **Выше** | Ниже | Тесты, typecheck, lint — встроены |
| **ИТОГО** | **7.5/10** | **8/10** | — |

---

## 5. Что оставил после себя каждый фреймворк

### GSD (сильнее repo baseline)
- ✅ Скрипты: test, typecheck, lint, build, prisma:generate
- ✅ 4 тестовых файла
- ✅ `DATABASE_URL` вместо hard-coded SQLite path
- ✅ Чистое разделение helpers
- ✅ Лучшая стратегия имён для avatar upload
- ✅ Planning artifacts (requirements, roadmap, state)

### OpenSpec (быстрее, но слабее scaffolding)
- ❌ Нет test script
- ❌ Нет typecheck script
- ❌ Prisma с hard-coded SQLite path (несмотря на .env.example)
- ❌ Логика живёт прямо в routes/actions
- ✅ Но: приложение работает, UI почти неотличим от GSD

---

## 6. Общие проблемы (оба фреймворка)

- Form preservation: при ошибке логина/регистрации значения не сохраняются
- Comment behavior: после публикации комментарий не показывается сразу
- Unread message badge: потребовался follow-up (не было в spec)
- Avatar upload validation: не production-safe
- Нет captcha / abuse protection (выходит за рамки теста)
- **Вывод:** UI-баги в обоих случаях были очень похожи, что указывает на общие ограничения модели/брифа, а не фреймворка

---

## 7. Рекомендация автора

> "Мой личный выбор — OpenSpec. Но это не делает OpenSpec лучше во всех смыслах."

### Выбирай GSD когда:
- Хочешь, чтобы фреймворк управлял процессом
- Готов ждать и тратить больше токенов ради quality gates
- Хочешь автономные chunks работы (set it running, come back later)
- Важен strong repo baseline (тесты, typecheck, чистый код)
- Меньше технический бэкграунд (framework помогает с planning)

### Выбирай OpenSpec когда:
- Хочешь быстрые итерации (propose → apply → check → archive)
- Готов сам управлять roadmap'ом
- Хочешь минимальный overhead на мелкие правки
- Token cost имеет значение (в 3.5x дешевле)
- Нравится stay engaged с работой, а не уходить на час

---

## 8. Ключевые инсайты

### Context management
- GSD: sub-agents в отдельных context windows. Основной контекст — только оркестрация.
- OpenSpec: change-based, контекст очищается между changes.

### Token consumption
- GSD: 126M токенов. Sub-agent-heavy архитектура сжигает токены.
- OpenSpec: 35.3M токенов. Проще loop = меньше токенов.

### Когда framework — не главное
- UI-качество и баги больше зависят от brief + model + product complexity
- Оба фреймворка сделали одинаковые ошибки (form preservation, comments)

### GSD vs BMAD
- "GSD — это то, чем BMAD должен был быть": structured, autonomous, capable of doing work instead of asking to approve more documents

### Важно: стек меняет tradeoff
- Тест на Codex + GPT-5.5. С Composer 2 Fast или другой моделью баланс может сместиться.

---

## 9. Шпаргалка: команды

### GSD (в Codex CLI)
```
$gsd-new-project --auto --spec=prd.md
$gsd-discuss-phase <number>
$gsd-plan-phase <number>
$gsd-execute-phase <number>
$gsd-verify-work
$gsd-ship
$gsd-next
$gsd-autonomous
$gsd-quick
```

### OpenSpec (в Codex CLI)
```
$openspec-propose     # Создать change folder с proposal/design/tasks/delta specs
$openspec-apply-change # Применить change
$openspec-archive-change # Заархивировать change, смержить delta specs в canonical specs
$openspec-explore      # Исследовать код
```

---

## 10. Ключевые термины

| Термин | Значение |
|--------|----------|
| NewWriter | Тестовое приложение — писательское комьюнити (auth, stories, comments, DM, leaderboard) |
| Spec-driven development | Разработка на основе спецификации |
| Delta specs | Изменения к canonical spec в OpenSpec |
| Canonical specs | Основная спецификация проекта (OpenSpec) |
| Change folder | Папка с proposal/design/tasks/delta для одного изменения |
| Sub-agent | Отдельный LLM-агент в своём context window (GSD) |
| Planning artifacts | project.md, requirements.md, roadmap.md, state.md (GSD) |
| Repo baseline | Инженерный scaffolding: тесты, typecheck, lint, скрипты |
| BMAD | Предыдущий фреймворк — то, чем GSD *должен был быть* |
| Acceptance pass | Ручное тестирование UI после генерации |

---

**↪️ 2025-07-26_GSD-vs-OpenSpec:** [[2025-07-26_GSD-vs-OpenSpec]]

**↪️ Категория:** [[README]]
