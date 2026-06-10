---
tags: [gsd, superpowers]
aliases: [GSD Superpowers тезисы]
date: 2025-07-26
version: 1.0
source: 2025-07-26_GSD-Superpowers
---

> **Дата:** 2025-07-26
> **Версия:** 1.0
> **Источник:** [[2025-07-26_GSD-Superpowers]] — Владилен Минин, "Vibe coding мёртв. Что пришло на замену в 2026. GSD & Superpowers"
> **Библиография:** [[../bibliography|Библиография]]


# GSD & Superpowers: Структурированные тезисы для работы с агентом


## 1. Эволюция: Vibe Coding → Agent Orchestration

### Vibe Coding (2025)
- Заменил только `implementation` фазу SDLC
- Requirements, design, deployment, maintenance — делал человек
- Не подходит для больших проектов: потеря контекста, "каша" в коде
- Хорош для прототипов и маленьких приложений

### Agent Orchestration (2026)
- ИИ закрывает **все 6 фаз** SDLC
- Человек → оператор/архитектор, который направляет агентов
- Долгосрочная память через файловый контекст (Markdown-документы)
- Чёткий pipeline = минимум галлюцинаций

### SDLC (6 фаз)
1. **Requirements** — сбор требований (Product Manager / Business Analyst)
2. **Design** — системный дизайн, архитектура, выбор стека
3. **Implementation** — написание кода
4. **Testing** — QA, верификация
5. **Deployment** — DevOps, выкладка
6. **Maintenance** — поддержка, правки

---

## 2. GSD (Get Shit Done) — для enterprise

**Суть:** Open-source metaprompting + context engineering + spec-driven development для Claude Code.

**Установка:** `npx get-shit-done`

**Базовые команды (6 основных хуков):**
1. `GSD New Project` — инициализация: research, requirements, roadmap, architecture
2. `GSD Discuss Phase` — обсуждение конкретной фазы, уточнение серых зон
3. `GSD Plan Phase` — детальное планирование фазы → waves → tasks
4. `GSD Execute Phase` — реализация кода (автономно пишет файлы)
5. `GSD Verify` / Code Review — самопроверка, верификация требований
6. `GSD Quick` — быстрые фиксы без полного цикла

**Pipeline:**
```
New Project → Research (4+ agentов параллельно) → 
Requirements Spec → Architecture Document → Roadmap → 
  Phase 1: Discuss → Plan → Execute (3 waves) → Code Review → Verify →
  Phase 2: Discuss → Plan → Execute (3 waves) → Code Review → Verify →
  ...
```

**Продвинутые хуки (73 всего):**
- `GSD Milestone` — большая фича (группа фаз)
- `GSD Split Phase` — дробление фазы
- `GSD Spike` — проверка гипотез
- `GSD Sketch` — визуальные варианты UI (HTML)
- `GSD Map Codebase` — картирование существующего кода
- `GSD Workstreams` — параллельная работа
- `GSD Analyze & Capture` — аудит кода
- `GSD Security` — security review
- `GSD Graphy` — обновление knowledge graph проекта

**Важные нюансы:**
- **Research before planning** — подключает web fetch, проверяет актуальную документацию, версии SDK
- **Human verification** — после каждой фазы требует утверждения
- **Git tracking** — автоматические коммиты, история изменений
- **Long-term memory** — вся документация в Markdown (project.md, requirements.md, roadmap.md, architecture.md, state.md, etc.)
- **Phase ≠ Wave** — фаза делится на 3+ waves (волны реализации)
- **Auto mode** (`bypass permissions`) — агент сам переходит Discuss → Plan → Execute без запроса
- **GSD Quick** — для мелких баг-фиксов (не требует полного цикла документирования)
- **Enterprise vs MVP** — GSD избыточен для маленьких проектов, используйте Claude Code напрямую или Superpowers

**Модели:**
- Планирование: Opus 4.7 (сильный, дорогой)
- Реализация: Sonnet (достаточно)
- Мелкие правки: Haiku

---

## 3. Superpowers — для中小 проектов

**Суть:** Система на скиллах (навыках). Легче GSD, меньше токенов.

**Установка:** В Claude Code/Cursor/Codex: `Plugins Install Superpowers`

**Основные скиллы (7 шт.):**

| Фаза SDLC | Скилл | Что делает |
|-----------|-------|------------|
| Инициация | `Using Superpowers` | Личный ассистент: определяет, какой скилл применить |
| Спецификация | `Brainstorming` | Помогает оцифровать идею → spec.md |
| Планирование | `Writing Plans` | Дробит на шаги, файлы, порядок реализации |
| Сборка | `Test Driven Development` | Сначала тесты, потом код |
| Проверка | `Verification` | Запускает приложение, проверяет в браузере |
| Финиш | `Finish Development` | Фиксирует этап, планирует下一步 |

**Артефакты:**
- `docs/superpowers/spec.md` — спецификация
- `docs/superpowers/plan.md` — implementation plan
- Git-коммиты на каждом этапе

**Pipeline:**
```
Using Superpowers (со спекой) → 
  → Brainstorming (уточнение, UI sketch, стек) → 
  → Writing Plans (декомпозиция) → 
  → Subagent-driven Execution (параллельные воркеры) → 
  → TDD → Code Review → 
  → Verification → Finish
```

**Ключевые отличия от GSD:**
- Меньше документации (один spec.md + plan.md)
- Визуальный brainstorming (UI sketches в браузере)
- TDD по умолчанию
- Subagent-driven — создаёт саб-агентов под каждую задачу
- Параллелизация воркеров (Maxwell, Gilbert и др.)
- Лучше для SaaS/MVP без enterprise-требований

**Subagent-driven execution:**
1. Orchestrator (Using Superpowers) → создаёт саб-агентов
2. Каждый саб-агент получает свою спецификацию
3. Работают параллельно
4. Встроенный Code Review агент проверяет результат
5. Human verification на финише

---

## 4. Сравнение GSD vs Superpowers

| Критерий | GSD | Superpowers |
|----------|-----|-------------|
| Масштаб | Enterprise, B2B | SaaS, MVP,中小 проекты |
| Вес | Тяжёлый (много токенов) | Лёгкий |
| Документация | 10+ Markdown файлов | 1-2 файла |
| Скорость | 1-2 часа на фазу | Быстрее |
| Параллелизация | 4 агента research | Саб-агенты + воркеры |
| TDD | Не встроен | По умолчанию |
| UI Sketch | GSD Sketch (ручной) | Встроенный Browser Brainstorming |
| Когда использовать | Большие команды, enterprise | Solo / small team, MVP |

---

## 5. Практические инсайты

### Роль разработчика в 2026
- **Не** писать код
- **А** проектировать систему, собирать требования, направлять агентов
- Уметь декомпозировать → важнейший навык
- Понимать SDLC — все 6 фаз

### Ошибки и фиксы
- Bug fix не требует полного цикла → GSD Quick
- При ошибке API: скопировать документацию провайдера → скормить агенту
- Проблемы с форматами → обычно hotfix одной строки

### Цены
- Opus 4.7: $100/мес (2-3 проекта одновременно)
- DeepSeek V4 Pro: дёшево, хорошо для реализации
- GPT 5.5, Codex — конкуренты на май 2026

### Совмещение
- GSD для планирования и архитектуры
- Superpowers для TDD и code review
- GSD Quick для быстрых фиксов поверх любой системы

---

## 6. Шпаргалка: как начать проект

### GSD (enterprise)
1. `npx get-shit-done` — установка
2. Написать spec.md с бизнес-требованиями
3. `GSD New Project --spec=spec.md` — инициализация
4. Дождаться research (4 параллельных агента)
5. Проверить `project.md`, `requirements.md`, `architecture.md`, `roadmap.md`
6. `GSD Discuss Phase 1` — обсудить фазу
7. `GSD Execute Phase 1` — реализация (авто)
8. `GSD Verify` — проверка
9. Повторить для фазы 2...N
10. `GSD Quick` для мелких правок

### Superpowers (MVP / SaaS)
1. `Plugins Install Superpowers` — установка
2. Написать spec.md
3. `Using Superpowers` со ссылкой на spec.md
4. Пройти brainstorming (UI, стек, архитектура)
5. Дождаться Writing Plans
6. Выбрать subagent-driven execution
7. Дождаться параллельных воркеров
8. Проверить через Verification
9. `Using Superpowers` снова для下一步

---

## 📋 Утверждения

| # | Утверждение | Источник | Уровень |
|---|-------------|----------|---------|
| 1 | Research перед каждой фазой/задачей на дешёвой модели — обязателен | GSD | `[hard]` |
| 2 | Spoke GSD — это проверка гипотез (GSD Spike) | GSD | `[hard]` |
| 3 | Subagent-driven execution — параллельные воркеры под задачу | Superpowers | `[hard]` |
| 4 | Планировать → строить → завершать. Обязательно каждый раз для очистки контекста | опыт | `[heuristic]` |
| 5 | Нужен Git-трекинг всех изменений | GSD | `[hard]` |

---

## 8. Ключевые термины (глоссарий)

| Термин | Значение |
|--------|----------|
| SDLC | Software Development Life Cycle (6 фаз) |
| Spec | Specification — Markdown-файл с бизнес-требованиями |
| Phase | Крупная единица работы (product shell, AI integration...) |
| Wave | Под-фаза внутри execution (обычно 3 на фазу) |
| Milestone | Большая фича, группа фаз (GSD) |
| Skills | Навыки Superpowers для разных фаз SDLC |
| Subagent | Дочерний агент с узкой задачей (Superpowers) |
| Human verification | Ручное подтверждение после каждой фазы |
| Long-term memory | Контекст в Markdown-файлах (не в диалоге) |
| Research | Web fetch для актуализации документации |
| GSD Quick | Быстрый фикс без полного цикла |

---

**↪️ 2025-07-26_GSD-Superpowers:** [[2025-07-26_GSD-Superpowers]]

**↪️ Категория:** [[README]]
