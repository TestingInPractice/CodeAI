---
tags: [gsd, paul]
aliases: [GSD vs Paul тезисы]
date: 2025-06-07
version: 1.0
source: 2025-06-07_GSD-vs-Paul
---

> **Дата:** 2025-06-07
> **Версия:** 1.0
> **Источник:** [[2025-06-07_GSD-vs-Paul]] — YouTube, "GSD vs Paul — 7 Critical Problems with GSD and How Paul Solves Them"
> **Библиография:** [[../bibliography|Библиография]]


# GSD vs Paul: Структурированные тезисы для работы с агентом


## 1. Что такое Paul?

- Новый Claude Code плагин — альтернатива GSD
- Создатель: Chris (также создатель Carl)
- Режим: "марафон" (sequential) vs GSD "эстафета" (parallel phases)
- Фокус: quality, continuity, verifiable proofs
- Установка: `npx ...` (команда в репозитории)
- Инициализация: `/paul init`
- Интегрируется с **Carl** — создание custom knowledge domains
- Цель: production-ready SaaS продукты

---

## 2. 7 проблем GSD, которые решает Paul

### Проблема 1: Knowledge Transfer (потеря контекста)
- **GSD:** теряет ~70% контекста при переходе между фазами/сессиями. Каждая новая фаза → полное перечитывание всех заметок = высокий token cost.
- **Paul:** теряет ~0% контекста. Единая непрерывная сессия (марафон).

### Проблема 2: Broken Loop (сломанный цикл при возобновлении)
- **GSD:** любое прерывание (human interruption, feedback) → полный рестарт. Текущий worker исчезает. Контекст заново.
- **Paul:** worker остаётся активным. Принимает input и продолжает без потери continuity.

### Проблема 3: Fake Verification (фальшивая верификация)
- **GSD:** проверяет только файловую структуру (статически). Нет guard rail, что приложение реально работает.
- **Paul:** **UAT (User Acceptance Test)** — guided пользовательское тестирование. Проверяет, что API работают, tech stack функционирует, функциональность подтверждена.

### Проблема 4: Messy Room / Drift Accumulation (накопление дрейфа)
- **GSD:** plan → build → check (опционально). Check не обязателен → накапливается drift, галлюцинации ИИ.
- **Paul:** plan → build → close (mandatory каждый раз). Обязательная уборка перед завершением задачи. Документация всегда соответствует реальности.

### Проблема 5: Token Cost (цена фиксов)
- **GSD:** любой мелкий фикс → полный цикл (индустриальный инструмент для мухи). Тратит огромное количество токенов.
- **Paul:** response масштабируется пропорционально размеру фикса. Экономит токены.

### Проблема 6: Parallel Processing Conflicts (конфликты параллельной разработки)
- **GSD:** фазы идут параллельно (1A, 1B, 1C одновременно). Если файлы связаны → integration failure.
- **Paul:** sequential processing (1 → 2 → 3). Медленнее, но fully informed. + UAT = качество гарантировано.

### Проблема 7: Silent Drift (тихий дрейф)
- **GSD:** предполагает успех сборки (assume success). Молча уходит в сторону от требований.
- **Paul:** UAT на каждом шагу — валидирует состояние проекта, заставляет проверять.

---

## 3. Сравнение: GSD vs Paul

| Критерий | GSD | Paul |
|----------|-----|------|
| Метафора | Эстафета (relay race) | Марафон (marathon) |
| Контекст | Теряет ~70% между фазами | Теряет ~0% |
| Обработка | Parallel phases | Sequential (1 by 1) |
| Верификация | Static (file structure) | Dynamic (UAT, guided testing) |
| Cleanup | Опционально | Mandatory (plan → build → close) |
| Token cost | Высокий (полный цикл на любой фикс) | Масштабируется под задачу |
| Прерывания | Полный рестарт | Worker stays active |
| Скорость | Высокая (raw velocity) | Ниже (но quality) |
| Quality | Трейдит качество за скорость | Трейдит скорость за continuity |
| Drift | Накапливается | Предотвращается UAT |
| Когда использовать | Independent tasks, massive scale, 20+ phases | Production reliability, client delivery |

---

## 4. Когда что выбирать

### Выбирай GSD когда:
- Нужна скорость и parallelization
- Independent work streams (фазы не связаны)
- Massive scale (20+ phases, большой проект)
- Нужен доступ к множеству команд и инструментов (tooling maturity)

### Выбирай Paul когда:
- Нужно production-ready качество
- Client delivery (агенство, high ticket)
- Важна verifiable proof работы
- Предпочитаешь scalpel approach (гранулярность)
- Готов пожертвовать скоростью ради надёжности

---

## 5. Как начать с Paul

```bash
# Установка
npx [command from repo]

# Инициализация проекта в Claude Code
/paul init

# Рекомендация: использовать plan mode сначала
# Обсудить проект, создать структуру
# Принять план → Paul создаст roadmap + phases + state.md
# Начнёт sequential build с UAT на каждом шаге
```

- Можно комбинировать с **Carl** для custom knowledge domains
- `paul init` создаёт папку `paul/` с project.md, roadmap.md, state.md
- Kanban board создаётся автоматически

---

## 6. Ключевые термины

| Термин | Значение |
|--------|----------|
| UAT | User Acceptance Test — guided тестирование функциональности |
| Sequential processing | Пошаговая обработка (1 → 2 → 3, не параллельно) |
| Continuity | Непрерывность контекста между сессиями |
| Silent drift | Тихое отклонение от требований без уведомления |
| Paul | Claude Code плагин для sequential quality-first разработки |
| Carl | Сопутствующий плагин для custom knowledge domains |

---

**↪️ 2025-06-07_GSD-vs-Paul:** [[2025-06-07_GSD-vs-Paul]]

**↪️ Категория:** [[README]]
