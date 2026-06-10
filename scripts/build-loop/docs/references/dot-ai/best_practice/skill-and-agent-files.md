# Skill и Agent файлы — проектирование навыков и агентов

> **Дата:** 2026-05-13
> **Версия:** 1.2
> **Источник:** [skills.md](skills.md) (эффективность навыков), [sub-agents.md](sub-agents.md) (делегирование)
> **Библиография:** [summary.md](summary.md#54-библиография)

---

SKILL.md — упакованная процедура, активируемая по trigger-фразе или `/`-команде. Файлы агентов (`.claude/agents/*.md`) — изолированные инструкции для субагентов. Практическое руководство: как писать frontmatter, структурировать тело навыка, проектировать цепочки workflow и агентов.

## 1.1 SKILL.md frontmatter

Frontmatter — точка входа для автодискавери. Модель видит description всех навыков и выбирает подходящий. Качество описания напрямую определяет точность активации `[L2]`.

**Поля frontmatter:**

```yaml
---
name: plan-release                     # уникальный идентификатор (kebab-case)
description: >                         # когда использовать (≤1,536 символов)
  Шаг ① workflow: Создание ТЗ + ветка + коммит.
  Triggers: "создай ТЗ", "new feature", "новая фича".
  Использует IEEE 29148:2018 для валидации.
type: workflow                         # workflow | internal | analytical | diagnostic
step: 1                                # порядковый номер (для workflow-навыков)
---
```

**Назначение полей:**

| Поле | Обязательное? | Назначение | Лимит |
|------|-------------|-----------|-------|
| `name` | Да | Идентификатор навыка, используется для `/name` | kebab-case |
| `description` | Да | Когда использовать + trigger-фразы. Основа автодискавери | ≤1,536 символов (~300 токенов) |
| `type` | Рекомендуется | Категория: workflow, internal, analytical, diagnostic | Строка |
| `step` | Для workflow | Порядковый номер в pipeline | Число |

**Аннотации к каждому полю:**

- **`name`**: короткий, описательный. Определяет команду активации: `/plan-release`. Не использовать spaces или camelCase
- **`description`**: наиболее важное поле. Должно содержать: (1) что навык делает, (2) trigger-фразы для автодискавери, (3) ключевые детали. Конкретные триггеры → точная активация `[L2]`
- **`type`**: помогает модели понять контекст. Workflow — обязательные шаги pipeline, internal — вспомогательные (commit-helper), analytical — анализ (skill-creator), diagnostic — диагностика (server-check)
- **`step`**: определяет порядок в pipeline. Позволяет модели понимать, какой навык следующий

## 1.2 SKILL.md тело — структура и содержание

**Рекомендуемая структура** (progressive disclosure `[L2]`):

```
SKILL.md
├── Frontmatter (name, description, type, step)    ← автодискавери
├── Заголовок + краткое описание (1–2 строки)       ← позиционирование
├── Workflow Contract (entry/exit/next_skill)        ← КРИТИЧНО, в начале
├── Алгоритм работы (по шагам)                       ← основной контент
├── Правила и ограничения                            ← справочный материал
└── Примеры / ссылки                                 ← ЯКОРЬ recall, в конце
```

**Обоснование структуры:**
- Workflow Contract в начале — критичные pre/post условия в позиции высокого recall `[L1]`
- Алгоритм в середине — основной рабочий контент
- Примеры в конце — якорь recall в конечной позиции `[L1]`
- Sweet spot: 500–1,500 токенов на тело навыка `[L2]` `[L3]`

**Workflow Contract — аннотированный шаблон:**

```yaml
## Workflow Contract

entry:                              # ПРЕДУСЛОВИЯ — когда навык можно запустить
  branch: NOT main | master         # ограничение по ветке
  artifacts:                        # необходимые файлы
    - .ai/specs/{branch-name}.md
  condition:                        # дополнительные условия
    - есть этапы со статусом ⬜ или 🔄

exit:                               # ПОСТУСЛОВИЯ — когда навык завершён
  condition: все этапы ✅
  artifacts:                        # созданные/изменённые файлы
    - docs/best_practice/*.md

next_skill: integrate-release       # СЛЕДУЮЩИЙ ОБЯЗАТЕЛЬНЫЙ ШАГ

uses:                               # внутренние зависимости
  - commit-helper
```

**Алгоритм работы — паттерн:**

```
## Алгоритм работы

### Фаза 1: Инициализация
1. Проверить ветку: git branch --show-current
2. Найти spec: .ai/specs/{branch-name}.md
3. Загрузить контекст: ARCHITECTURE.md, ...

### Фаза 2: Сбор информации
Запустить субагентов параллельно (тип Explore):
- Code Mapper — читает файлы этапа
- Data Flow Tracer — трассирует зависимости

### Фаза 3: Реализация
1. Реализовать только текущий этап
2. Коммит через commit-helper

### Фаза 4: Тесты и коммит
1. Тесты GREEN
2. Обновить статус в spec: ⬜ → ✅
```

**Continuous Improvement — опциональный блок для эволюции навыка:**

```markdown
## Continuous Improvement

At the end of each run, perform Improvement Triage:

1. If the task succeeded without ambiguity, output `no_change`.
2. If a reusable lesson was discovered, append a concise entry to `LEARNINGS.md`.
3. If the skill instructions caused a failure or ambiguity, create an eval case first.
4. Propose a `SKILL.md` patch only when the same issue is likely to recur.
5. Prefer replacing or deleting stale guidance over appending new rules.
6. Do not update `SKILL.md` unless the relevant eval passes.
```

**Supporting files для самоэволюции:**

| Файл | Назначение | Автообновление |
|------|------------|----------------|
| `LEARNINGS.md` | Наблюдения после запусков, reusable lessons | Да |
| `EVALS.md` | Regression cases и критерии успеха | Да |
| `CHANGELOG.md` | История изменений навыка | Да |
| `SKILL.md` | Стабильный контракт и алгоритм | Только через eval gate |

Правило обслуживания: эволюция должна идти через `LEARNINGS.md` и `EVALS.md`; прямое добавление новых правил в `SKILL.md` после каждого запуска запрещено. Каждое изменение `SKILL.md` должно заменить слабую инструкцию, удалить устаревший текст или вынести справку в supporting file.

### Supporting files — практическая структура

Supporting files нужны, когда навык должен давать богатый контекст без превращения `SKILL.md` в длинный монолит. В модели Agent Skills дополнительные файлы лежат рядом с `SKILL.md` и загружаются только по требованию `[L2]` `[vendor/spec]`.

```
skill-name/
├── SKILL.md                    ← контракт, quick start, карта файлов
├── references/
│   ├── quality-checklist.md     ← критерии и edge cases
│   └── runbook.md               ← подробная процедура
├── scripts/
│   └── validate.py              ← исполняемый валидатор
├── assets/
│   └── template.md              ← статический шаблон
├── LEARNINGS.md                 ← reusable lessons
└── EVALS.md                     ← regression cases
```

**Что держать в `SKILL.md`:**
- Workflow Contract, entry/exit, next_skill
- быстрый алгоритм, достаточный для обычного запуска
- таблицу «если ситуация X — читать файл Y / запускать скрипт Z»
- критичные ограничения, которые нельзя пропустить

**Что выносить в `references/`:**
- длинные критерии качества, чеклисты, rubrics
- редкие edge cases и troubleshooting
- domain-specific справку для подтипов задачи
- примеры, которые полезны не при каждом запуске

**Что выносить в `scripts/`:**
- проверки, которые должны быть воспроизводимыми
- конвертацию форматов, генерацию артефактов, статический анализ
- операции, где prompt-код каждый раз будет менее надёжен, чем готовый helper

**Правила навигации:**
1. Ссылки из `SKILL.md` держать one-level deep: `SKILL.md -> references/runbook.md`, без цепочек через промежуточные файлы.
2. Файлы длиннее ~100 строк начинать с оглавления `[Evidence Scope: Claude Skills docs, дата: 2026, source: vendor recommendation]`.
3. Имена файлов делать предметными: `requirements-quality.md`, `deploy-rollback.md`, `merge-safety.md`.
4. Для каждого скрипта указывать команду запуска, входы, выходы и пример ошибки.
5. Если файл нужен почти всегда, его содержание стоит сократить и перенести в `SKILL.md`; если нужен редко — оставить в `references/`.

## 1.3 Trigger-фразы и автодискавери

Модель выбирает навык на основе description — модель не читает тело навыка до активации `[L2]`.

**Эффективные trigger-описания (3 примера):**

```yaml
# Пример 1: Workflow-навык с конкретными триггерами
description: >
  Шаг ① workflow: Создание ТЗ + ветка + коммит.
  Triggers: "создай ТЗ", "new feature", "новая фича", "bugfix".
  Использует IEEE 29148:2018 для валидации требований (≥85%).
  После валидации создаёт ветку feature/* или bugfix/* и коммитит spec.

# Пример 2: Инфраструктурный навык
description: >
  Подключение к VPS серверу и диагностика.
  Triggers: "проверь сервер", "server check", "статус сервера",
  "подключись к серверу", "ssh", "что на сервере".

# Пример 3: Аналитический навык
description: >
  Guide for creating effective skills. Use when users want to create
  a new skill or update an existing skill that extends Claude's
  capabilities with specialized knowledge, workflows, or tool integrations.
```

**Правила написания description:**
1. **Первая строка** — что навык делает, в одном предложении
2. **Triggers** — явно перечисленные фразы, которые пользователь может сказать
3. **Ключевые детали** — специфичные ограничения или возможности (IEEE 29148, ≥85%, etc.)
4. **Язык триггеров** — соответствовать языку целевой аудитории (русские триггеры для русскоязычных проектов)
5. **≤1,536 символов** — не более ~300 токенов

**Анти-паттерны в description:**
- «Помощь с кодом» — слишком абстрактно, модель не поймёт, когда активировать
- «Навык для работы с проектом» — не говорит, что конкретно делает
- Отсутствие trigger-фраз — модель не сможет сопоставить запрос пользователя с навыком

## 1.4 next_skill и цепочки workflow

Цепочка навыков реализует progressive disclosure на уровне pipeline: каждый навык активирует следующий `[L2]`.

**Паттерн цепочки:**

```
plan-release ──next_skill──► implement-spec-stage ──next_skill──► write-tests ──next_skill──► integrate-release ──next_skill──► deploy-release
     ①                           ②                              ③                          ④                         ⑤
```

**Правила проектирования цепочек:**

1. **Один навык = одна simple задача** — каждый навык должен быть individually simple, до complexity cliff `[L1]`
2. **Явный next_skill** — каждый навык указывает следующий обязательный шаг в Workflow Contract
3. **Entry/Exit проверка** — каждый навык проверяет предусловия и постусловия
4. **Терминальный навык** — `next_skill: null` или `next_skill: deploy-release` (последний в цепочке)
5. **Ветвление** — через condition: разные next_skill в зависимости от результата

**Примеры цепочек:**

```yaml
# Новая фича
plan-release → implement-spec-stage → write-tests → integrate-release → deploy-release

# Багфикс
plan-release (bugfix) → implement-spec-stage → integrate-release → deploy-release

# Docs-only проект
plan-release → implement-spec-stage → integrate-release  # нет write-tests и deploy-release
```

## 1.5 Файлы агентов

`.claude/agents/*.md` — инструкции для изолированных субагентов. В отличие от навыков, агенты работают в собственном контексте `[L2]`.

**Структура файла агента:**

```markdown
---
name: code-reviewer
description: Independent code review agent
model: sonnet
allowed-tools:
  - Read
  - Grep
  - Glob
---

# Code Reviewer

Reviews code changes and provides feedback.

## Instructions

1. Read the changed files
2. Check for:
   - Security vulnerabilities
   - Performance issues
   - Code style violations
3. Report findings as structured list
```

**Поля агента:**

| Поле | Назначение | Пример |
|------|-----------|--------|
| `name` | Идентификатор агента | `code-reviewer` |
| `description` | Что делает агент | `Independent code review agent` |
| `model` | Override модели | `sonnet`, `opus`, `haiku` |
| `allowed-tools` | Доступные инструменты | `Read`, `Grep`, `Glob` |

**Разделение architect/editor** `[L2]`:

| Тип | Инструменты | Когда использовать | Аналоги |
|------|-----------|-------------------|---------|
| **Architect** (read-only) | Read, Grep, Glob | Исследование, анализ, планирование | Aider architect, Claude Code Explore |
| **Editor** (full) | Read, Write, Edit, Bash | Реализация, модификация кода | Aider editor, Claude Code General-purpose |

**Рекомендации:**
- Агенты для исследования → `model: haiku`, только read-tools — быстро и дёшево
- Агенты для сложных задач → `model: sonnet` или `model: opus` — выше качество
- Не делегировать тривиальные задачи (overhead ~12K токенов на вызов субагента) `[L3]`

## 1.6 Анти-паттерны

**1. Слишком длинное тело навыка** `[L2]` `[L3]`:
- >1,500 токенов → выход за sweet spot → деградация compliance
- Решение: вынести справочный контент в отдельные файлы, загружать через Read

**2. Отсутствие чётких триггеров** `[L2]`:
- Description без trigger-фраз → модель не понимает, когда активировать
- Решение: явно перечислить trigger-фразы в description

**3. Дублирование с CLAUDE.md/rules** `[L2]`:
- Правила, повторённые из CLAUDE.md в навыке → рост контекста, противоречия
- Решение: навык ссылается на CLAUDE.md, не копирует

**4. Отсутствие entry/exit условий** `[L2]`:
- Без контракта модель не знает, когда навык завершён
- Решение: explicit Workflow Contract в начале тела навыка

**5. Nested sub-agents** `[L1]`:
- Субагент, вызывающий субагента → потеря контекста, рост overhead
- Ограничение: 1 уровень вложенности. Субагент не может делегировать дальше

**6. Саморедактирование без eval gate** `[L2]`:
- Навык автоматически дописывает `SKILL.md` после каждого запуска → накопление противоречий и раздувание контекста
- Решение: `LEARNINGS.md` для наблюдений, `EVALS.md` для regression cases, `SKILL.md` обновлять только при проходящем eval

## 1.7 Чеклист

1. **Frontmatter с name, description, type** — минимум 3 поля для автодискавери
2. **Trigger-фразы в description** — ≥3 конкретных фразы для активации
3. **Workflow Contract с entry/exit** — пред- и постусловия в начале тела
4. **next_skill указан** — явная связь с следующим шагом pipeline
5. **≤1,500 токенов тело** — sweet spot для compliance
6. **Алгоритм по фазам** — инициализация → сбор информации → реализация → проверка
7. **Нет дублирования с CLAUDE.md** — навык дополняет, не копирует
8. **Примеры в конце** — 2–3 canonical examples как якорь recall
9. **allowed-tools ограничен** — только необходимые инструменты для задачи
10. **Агент-файлы для изоляции** — когда нужен чистый контекст или read-only доступ
11. **Supporting files one-level deep** — `SKILL.md` напрямую указывает на релевантные `references/`, `scripts/`, `assets/`
12. **Скрипты имеют явный контракт** — команда запуска, inputs, outputs, зависимости, понятные ошибки
13. **Continuous Improvement опционален** — если нужен самообучающийся навык, есть `LEARNINGS.md`, `EVALS.md` и gate для `SKILL.md`
