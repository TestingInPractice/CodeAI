---
tags: [gsd, opencode]
aliases: [GSD for OpenCode тезисы]
date: 2025-07-26
version: 1.0
source: 2025-07-26_GSD-for-OpenCode
---

> **Дата:** 2025-07-26
> **Версия:** 1.0
> **Источник:** [[2025-07-26_GSD-for-OpenCode]] — Владилен Минин (на английском), "GSD for OpenCode — полный обзор и демонстрация"
> **Библиография:** [[../bibliography|Библиография]]


# GSD for OpenCode: Структурированные тезисы для работы с агентом


## 1. Что это?

- Адаптация GSD (Get Shit Done) под **OpenCode**
- Оригинальный GSD → для Claude Code
- Адаптация от **Tasher** — расширена на OpenCode, Claude Code и Gemini
- Владилен попробовал Tasher-версию, не очень понравилась → использует свою адаптацию
- ~80-90 файлов конфигурации

---

## 2. Полный pipeline (как работает GSD в OpenCode)

### Шаг 1: GSD New Project
- Выполняется в пустой папке (без git, без файлов)
- Система задаёт вопросы о проекте (идея, требования, vision)
- Не нужно определять всё заранее — LLM сама найдёт gaps и спросит
- Создаёт `planning/` папку с project.md

### Шаг 2: Research
- GSD запускает 4+ параллельных агента-исследователя
- Каждый агент работает в своём context window
- Web fetch для документации, SDK, фреймворков
- Результат: architecture.md, features.md, pitfalls.md, requirements.md, roadmap.md

### Шаг 3: Discuss Phase
- Дроп контекста → новая сессия
- Система читает все подготовленные документы
- Задаёт уточняющие вопросы по фазе
- Создаёт `phases/01-name/` с context.md для фазы

### Шаг 4: Plan Phase
- Дроп контекста → plan command
- Создаёт sub-agents для планирования подзадач
- Phase делится на 3-4 tasks/plans
- Задачи проектируются без пересечений → можно в параллель
- Создаёт breakdown с зависимостями (task1 → task2+task3 параллельно → task4)

### Шаг 5: Execute Phase
- Исполняет задачи через sub-agents
- Каждый sub-agent в своём context window
- Параллельное исполнение независимых задач
- Автоматические git-коммиты
- Self-check / verification против спецификации
- Запускает тесты, проверяет API
- Обновляет state.md, roadmap.md
- Показывает progress (2/13 requirements done, 15%)

### Шаг 6: Repeat
- Discuss Phase 2 → Plan Phase 2 → Execute Phase 2 → ...

---

## 3. Ключевые особенности GSD for OpenCode

### Sub-agents (главная фича)
- Каждый sub-agent = отдельный context window
- Контекст не смешивается → нет проблемы "забывания"
- Можно исполнять задачи параллельно
- Sub-agent умирает, когда задача выполнена (context освобождается)

### Research before planning
- Система автоматически ищет актуальную документацию
- Использует web fetch для проверки версий SDK, фреймворков
- Заполняет gaps, которые не были покрыты вопросами

### Context management
- Каждая фаза → новый context window (drop + reload)
- Долгосрочная память = файлы в `planning/` и `phases/`
- state.md постоянно обновляется (progress bar)
- roadmap.md синхронизируется с текущим статусом

### Error handling
- При ошибке тула (например, Write tool) — умная модель retry с другими параметрами
- Если контекст потерян → можно перезапустить execute с той же точки
- Все решения сохранены в файлах, не в диалоге

---

## 4. Практические инсайты

### Роль разработчика
- Ответить на вопросы системы (они reasonable)
- Принимать решения, когда LLM не уверена
- Проверять файлы (project.md, requirements.md, roadmap.md)
- Утверждать результаты фазы → переходить к следующей

### Время
- Research: ~5-10 минут (4 параллельных агента)
- Planning: ~5-10 минут
- Execution: ~15-30 минут на фазу
- Весь процесс: может занять часы, но разработчик почти не участвует

### Цены
- Контекст растёт: ~11-33% за research, до 60% допустимо
- Sub-agents используют свой контекст (не влияет на основной)

### Когда останавливать
- Систему можно остановить в любой момент
- state.md и файлы сохраняют прогресс
- При перезапуске — продолжение с той же точки

---

## 5. GSD vs Vibe Coding (ещё раз)

| Vibe Coding | GSD |
|-------------|-----|
| Весь проект в одном контексте | Дробится на sub-agents |
| Потеря контекста = потеря работы | Всё сохраняется в файлах |
| Нет research | Research перед каждой фазой |
| Нет планирования | Plan → Execute → Verify |
| Нет декомпозиции | Phase → Tasks → Sub-agents |
| Один LLM на всё | Параллельные агенты |
| Хаос при масштабировании | Структура enterprise-уровня |

---

## 6. Шпаргалка: команды GSD for OpenCode

```bash
# Инициализация нового проекта
GSD New Project

# Обсуждение фазы
GSD Discuss Phase <number>

# Планирование фазы
GSD Plan Phase <number>

# Исполнение фазы
GSD Execute Phase <number>

# Быстрые фиксы
GSD Quick <description>
```

**Важно:** после каждой команды — очищать контекст (новая сессия). Система перечитает файлы.

---

## 7. Ключевые термины

| Термин | Значение |
|--------|----------|
| GSD OpenCode | Адаптация GSD для OpenCode (от Tasher) |
| Planning folder | Папка с project.md, requirements.md, roadmap.md, state.md |
| Phase folder | `phases/01-name/` с context.md для фазы |
| Sub-agent | Отдельный LLM-агент в своём context window |
| Parallel execution | Запуск независимых sub-agents одновременно |
| State file | Файл с прогрессом (requirements done / total) |
| Research | Автоматический web fetch для актуализации знаний |
| Context drop | Очистка диалога перед новой командой (файлы — долгосрочная память) |

---

**↪️ 2025-07-26_GSD-for-OpenCode:** [[2025-07-26_GSD-for-OpenCode]]

**↪️ Категория:** [[README]]
