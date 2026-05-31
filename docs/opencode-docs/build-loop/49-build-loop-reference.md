# Build Loop — Полностью автономная сборка приложений через GStack → GSD → Superpower → Ralph Loop

> **Источник:** Видео «GStack + GSD + Superpowers Workflow» (https://www.youtube.com/watch?v=BlTpG51x94w)  
> **Автор:** Spectrum Development  
> **Статус:** Build Loop — это skill, построенный поверх Ralph Loop. Не опубликован как отдельный репозиторий.

---

Build Loop — это оркестратор, который объединяет три фреймворка (GStack, GSD, Superpower) в единый автономный пайплайн. Вместо того чтобы просить Claude сделать всё в одной сессии, Build Loop разбивает проект на фазы, каждую выполняет в **свежей headless-сессии с нулевым контекстом** и итерирует до полного завершения.

**Ключевой результат:** 16 фаз / 100+ headless-сессий / 10% контекста в оркестраторе / полностью автономная сборка overnight.

---

## Проблема: одна сессия → context rot

```
Одна сессия:
┌─────────────────────────────────────────────────────┐
│ Prompt: сделай CRM                                   │
│ → Claude пишет auth, customers, reports в одном      │
│   гигантском файле                                   │
│ → после 50% контекста — точность падает              │
│   (context rot)                                      │
│ → после 70% — импровизирует, пропускает edge cases   │
│ → после 90% — дублирует код, противоречит себе       │
│ → результат: работает, но хрупко, баги на edge cases │
└─────────────────────────────────────────────────────┘
```

Build Loop решает это радикально: **ни одна фаза не занимает > 50% контекста**, потому что каждая исполняется в отдельной сессии.

---

## Архитектура

```
                     ┌──────────────────────────┐
                     │     GStack (Spec + Vote)   │
                     │  Brainstorming, уточнение  │
                     │  Role-based голосование    │
                     │  CEO / Eng / Designer      │
                     └──────────┬───────────────┘
                                │ docs/specs/
                     ┌──────────▼───────────────┐
                     │  GSD (Phase Decomp)       │
                     │  Анализ docs/specs/       │
                     │  Декомпозиция на фазы     │
                     │  Каждая < 50% контекста   │
                     │  Запись в phases.json     │
                     └──────────┬───────────────┘
                                │ phases.json
                     ┌──────────▼───────────────┐
                     │  Ralph Loop (Orchestrator)│
                     │  Читает phases.json       │
                     │  Находит первую pending   │
                     │  Генерирует prompt на лету │
                     │  из docs/specs/           │
                     │  Делегирует в headless     │
                     │  Ждёт результат            │
                     │  Обновляет статус         │
                     └──────────┬───────────────┘
                                │
               ┌────────────────┼────────────────┐
               │                │                │
      ┌────────▼───┐  ┌────────▼───┐  ┌────────▼───┐
      │ Headless #1 │  │ Headless #2 │  │ Headless #N │
      │  Superpower │  │  Superpower │  │  Superpower │
      │  TDD cycle  │  │  TDD cycle  │  │  TDD cycle  │
      │              │  │              │  │              │
      │  Вопросы?    │  │  Вопросы?    │  │  Вопросы?    │
      │  → GStack    │  │  → GStack    │  │  → GStack    │
      └──────────────┘  └──────────────┘  └──────────────┘
```

### Три уровня архитектуры

| Уровень | Компонент | Роль |
|---------|-----------|------|
| **Верхний** | GStack | Уточнение требований, голосование ролями, наполнение `docs/specs/` |
| **Средний** | GSD | Декомпозиция `docs/specs/` на фазы (< 50% контекста каждая) |
| **Нижний** | Superpower | Исполнение каждой фазы: TDD → реализация → verify |
| **Оркестратор** | Ralph Loop (Build Loop) | Читает phases.json, делегирует фазы в headless-сессии, обновляет статус |

---

## Build Loop: Как это работает

Build Loop — это skill, который:

1. Принимает `docs/specs/` (созданный GStack или написанный вручную)
2. Использует GSD для анализа `docs/specs/` и декомпозиции на фазы
3. Записывает фазы в `phases.json`
4. Запускает Ralph Loop: итеративно находит первую `pending` фазу, генерирует для неё промпт из `docs/specs/`, отправляет в `claude -p` (или `task()` в OpenCode)
5. Каждая headless-сессия исполняет фазу через Superpower (TDD → код → verify)
6. Если в процессе возникают архитектурные вопросы — сессия делегирует их в GStack для role-based голосования
7. После завершения фазы — обновляет `phases.json` и переходит к следующей

```
Ralph Loop (псевдокод):

phases = read("phases.json")
for phase in phases where phase.status == "pending":
    context = read_results_of_dependencies(phase)
    prompt = generate_prompt("docs/specs/", phase, context)
    result = run_headless(prompt)
    phase.status = "completed"
    phase.result = result
    write("phases.json", phases)
```

---

## Условная логика: Greenfield vs Brownfield

Build Loop определяет режим работы по первому запросу пользователя:

```
IF запрос начинается с "создай / сделай / напиши с нуля / новый проект"
  → GREENFIELD MODE:
    1. GStack brainstorming + role voting → стек + архитектура
    2. GSD phase decomposition → phases.json
    3. Ralph Loop (полный цикл, все фазы)
    4. Финальный отчёт

IF запрос начинается с "добавь / измени / почини / дополни"
  → BROWNFIELD MODE:
    1. Прочитать код, понять существующую архитектуру
    2. Спросить: "нужен ли GStack для решений?" (опционально)
    3. 1-2 фазы через Superpower (TDD)
    4. Verify + regression check
```

### Greenfield

Проект с нуля. Нет кода, нет БД, нет архитектуры. Build Loop проектирует всё сам: от структуры папок до выбора стека.

**Пример:** «Сделай CRM с авторизацией, управлением клиентами и отчётами»

```
1. GStack → brainstorming: какой стек? какая БД? какие роли?
   → голосование: Next.js + PostgreSQL + Prisma
2. GSD → 5 фаз (project-setup, auth, customers, orders, reports)
3. Build Loop → все 5 фаз. На выходе — готовое приложение.
```

| Аспект | Greenfield |
|--------|------------|
| Spec | `docs/specs/` создаётся с нуля через GStack |
| Фазы | Весь проект, от 5 до 16+ фаз |
| Архитектура | Build Loop решает |
| Риск | Низкий (ничего не сломать) |

### Brownfield

Существующий проект. Build Loop не переписывает стек, не реструктурирует папки, не трогает legacy — только добавляет запрошенную фичу.

**Пример:** «Добавь отчёты в существующую CRM»

```
Build Loop НЕ делает:
✗ Не предлагает перейти на FastAPI
✗ Не переписывает auth
✗ Не реструктурирует папки

Build Loop делает:
1. Читает код (структура, schema.prisma, API routes)
2. GStack-голосование: "куда вписать reports?"
3. Одна фаза: реализация reports через Superpower
4. Verify: не сломались ли существующие тесты
```

| Аспект | Brownfield |
|--------|------------|
| Spec | Извлекается из существующего кода в `docs/specs/` |
| Фазы | Только добавляемая фича, 1-2 фазы |
| Архитектура | Build Loop подстраивается |
| Риск | Высокий (не сломать existing) |

---

## State-файл: `docs/specs/` как единый source of truth

В Build Loop **только одна точка ответственности** — директория `docs/specs/`. Никакого плоского `spec.md`.

### Структура `docs/specs/`

```
docs/specs/
├── goals.md                # бизнес-цели, пользовательские потребности
├── contracts/
│   ├── api.md              # эндпоинты, реквесты/респонсы
│   └── data-models.md      # схемы БД, интерфейсы, типы
└── acceptance-criteria.md  # проверяемые условия для done
```

**`goals.md`:**
```markdown
# CRM System — Goals
- Авторизация: только зарегистрированные пользователи
- Управление клиентами: CRUD, поиск, импорт из CSV
- Заказы: создание, смена статусов, история
- Отчёты: дашборд с графиками, экспорт PDF/Excel
- Tech stack: Next.js 15, PostgreSQL, Prisma, Tailwind
```

**`contracts/api.md`:**
```markdown
# API Contracts
## Auth
POST /api/auth/register { email, password } → { token, user }
POST /api/auth/login    { email, password } → { token, user }
POST /api/auth/refresh  { refreshToken }    → { token }

## Customers
GET    /api/customers           ?page&search → { items, total }
POST   /api/customers           { name, email, phone } → Customer
GET    /api/customers/:id                       → Customer
PUT    /api/customers/:id       { name, email } → Customer
DELETE /api/customers/:id                       → { ok }
POST   /api/customers/import    { csv }         → { imported, errors }
```

**`contracts/data-models.md`:**
```markdown
# Data Models
User:     id, email, passwordHash, role (admin|manager|user), createdAt
Customer: id, name, email, phone, createdBy, createdAt
Order:    id, customerId, status, total, items[], createdAt
Report:   id, type, period, config, generatedAt, fileUrl
```

**`acceptance-criteria.md`:**
```markdown
# Acceptance Criteria
## Auth
- [ ] Регистрация с email+password создаёт пользователя
- [ ] Логин возвращает JWT + refresh token
- [ ] Невалидные credentials → 401
- [ ] Refresh-token возвращает новый JWT

## Customers
- [ ] CRUD для customers работает
- [ ] Поиск по name/email возвращает релевантные результаты
- [ ] Импорт CSV обрабатывает 10 000 записей < 30s
```

### phases.json (генерируется GSD-агентом)

Фазы ссылаются на конкретные секции `docs/specs/`:

```json
{
  "phases": [
    {
      "id": 1,
      "name": "project-setup",
      "acceptance_criteria": ["docs/specs/acceptance-criteria.md#project-setup"],
      "depends_on": [],
      "status": "pending"
    },
    {
      "id": 2,
      "name": "auth-module",
      "acceptance_criteria": ["docs/specs/acceptance-criteria.md#auth"],
      "contracts": ["docs/specs/contracts/api.md#auth"],
      "models": ["docs/specs/contracts/data-models.md#User"],
      "depends_on": [1],
      "status": "pending"
    },
    {
      "id": 3,
      "name": "customers",
      "acceptance_criteria": ["docs/specs/acceptance-criteria.md#customers"],
      "contracts": ["docs/specs/contracts/api.md#customers"],
      "models": ["docs/specs/contracts/data-models.md#Customer"],
      "depends_on": [1, 2],
      "status": "pending"
    },
    {
      "id": 4,
      "name": "orders",
      "acceptance_criteria": ["docs/specs/acceptance-criteria.md#orders"],
      "contracts": ["docs/specs/contracts/api.md#orders"],
      "models": ["docs/specs/contracts/data-models.md#Order"],
      "depends_on": [1, 2, 3],
      "status": "pending"
    },
    {
      "id": 5,
      "name": "reports",
      "acceptance_criteria": ["docs/specs/acceptance-criteria.md#reports"],
      "contracts": ["docs/specs/contracts/api.md#reports"],
      "models": ["docs/specs/contracts/data-models.md#Report"],
      "depends_on": [1, 2],
      "status": "pending"
    }
  ]
}
```

### Генерация промпта на лету из `docs/specs/`

Перед каждой фазой агент-оркестратор:

1. Читает `goals.md` — контекст "зачем"
2. Читает `contracts/` — какие контракты относятся к этой фазе
3. Читает `acceptance-criteria.md` — какие критерии для этой фазы
4. Читает результаты предыдущих фаз
5. Собирает промпт динамически

```
function generate_prompt(specs_dir, phase, previous_results):
    goals       = read(specs_dir + "/goals.md")
    contracts   = read_sections(specs_dir + "/contracts/", phase.contracts)
    criteria    = read_sections(specs_dir + "/acceptance-criteria.md", phase.acceptance_criteria)

    context = ""
    for dep in phase.depends_on:
        result = previous_results[dep]
        context += f"### {result.phase_name} завершена\n{result.summary}\n\n"

    prompt = f"""
    Ты выполняешь фазу "{phase.name}" проекта.

    ### Goals проекта:
    {goals}

    ### Контракты для этой фазы:
    {contracts}

    ### Acceptance Criteria:
    {criteria}

    ### Что уже сделано:
    {context}

    ### Задача:
    1. Прими acceptance criteria как тесты — напиши их первыми (TDD)
    2. Реализуй код по контрактам
    3. Verify: все acceptance criteria проходят

    Если нужны архитектурные решения — используй GStack голосование.
    """

    return prompt
```

**Преимущества:**
- Одна точка ответственности — `docs/specs/`
- Acceptance criteria напрямую конвертируются в тесты (никакой интерпретации)
- Промпт всегда актуален под текущее состояние проекта
- Можно менять `docs/specs/` в процессе — промпты подстроятся

---

## Headless-сессии: как это работает

Build Loop использует `claude -p` (Claude Code) или `task()` (OpenCode) для запуска фаз в фоновых сессиях.

### Claude Code

```bash
# Оркестратор запускает фазу в фоне
claude -p "$(cat prompt_for_phase_1.md)"

# Результат возвращается в stdout, сессия завершается
# Контекст освобождён
```

### OpenCode

```bash
# Через task-инструмент
# Оркестратор вызывает subagent, который исполняет фазу
# По завершении — результат, контекст освобождён
```

### Почему это даёт максимальную точность

| Фактор | Одна сессия | Build Loop |
|--------|-------------|------------|
| **Context rot** | Точность падает после 50% | Каждая фаза начинает с 0%, заканчивает ~40% |
| **TDD** | «Напиши тесты потом» (забывает) | Superpower: тесты строго перед кодом |
| **Arch. decisions** | Claude гадает | GStack голосование ролей |
| **Verify** | «Работает? Ок» | После каждой фазы — verify |
| **Связанность** | Одна фаза влияет на другую | Чёткие границы, каждая самодостаточна |
| **Повторяемость** | «Чёрный ящик» | Можно перезапустить любую фазу |

---

## Оркестратор: 10% контекста

Оркестратор (основная сессия Claude/OpenCode) содержит только:
- `docs/specs/` — цели, контракты, acceptance criteria
- `phases.json` — статус фаз
- Логику цикла (Ralph Loop)

```
Контекст оркестратора (~10%):
┌──────────────────────────────────────────────┐
│ docs/specs/ (3-5% контекста)                 │
│ phases.json (1-2% контекста)                  │
│ Цикл: for phase in phases (1-2% контекста)    │
│ Текущий phase.id + status (1-2% контекста)    │
│ Итого: ~10%                                   │
└──────────────────────────────────────────────┘
      │
      │ делегирует в headless
      ▼
┌──────────────────────────────────────────────┐
│ Headless сессия (0-40% контекста)             │
│ → фаза выполняется, контекст растёт до ~40%   │
│ → завершается, контекст освобождается         │
│ → оркестратор получает summary                │
└──────────────────────────────────────────────┘
```

---

## Результаты из демо

- **16 фаз** из 16 completed
- **100+ headless-сессий** выполнено в фоне (за ночь)
- **10% контекста** использовано в оркестраторе
- Полностью автономная сборка overnight
- Каждая сессия использует Superpower (TDD) + GStack (голосование при вопросах)

---

## Интеграция с GStack

GStack устанавливается бесплатно (MIT, 105k★):

```bash
git clone --single-branch --depth 1 https://github.com/garrytan/gstack.git ~/.claude/skills/gstack
cd ~/.claude/skills/gstack && ./setup --host opencode
```

В Build Loop GStack используется через `task()`:

```
Когда headless-сессия (Superpower) упирается в архитектурный вопрос:
  1. Superpower: "Какую БД выбрать? PostgreSQL или SQLite?"
  2. → делегирует в GStack: task(GStack, roles=[CEO, Eng, Designer])
  3. GStack: голосование ролями → победитель: PostgreSQL
  4. → возвращает решение в Superpower
  5. Superpower: продолжает исполнение с выбранным решением
```

---

## Сравнение с другими подходами

| | Одна сессия | GSD | Superpower | Build Loop |
|---|---|---|---|---|
| Context rot | Есть | Нет (фазы < 50%) | Нет | Нет (100% свежий контекст) |
| TDD | Нет | Опционально | Да | Да (Superpower внутри) |
| Arch. decisions | Claude гадает | Claude гадает | Claude гадает | GStack голосование |
| Автономность | Нет | Частично | Частично | Полная (overnight) |
| Контекст оркестратора | 100% | 30-40% | 30-40% | ~10% |
| Повторяемость | Низкая | Средняя | Средняя | Высокая |

---

## Резюме

Build Loop берёт лучшее из трёх фреймворков:
- **GStack** — для уточнения требований и принятия решений (role-based голосование)
- **GSD** — для декомпозиции spec на фазы и борьбы с context rot
- **Superpower** — для TDD-исполнения каждой фазы

И добавляет оркестратор (Ralph Loop), который делает процесс полностью автономным: `docs/specs/` → фазы → headless-сессии → готовый проект.
