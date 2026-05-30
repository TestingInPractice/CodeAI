# Superpowers — Полная методология разработки для AI-агентов

> **Источник:** https://github.com/obra/superpowers  
> **Автор:** Jesse Vincent (Prime Radiant)  
> **Лицензия:** MIT  
> **Звёзд:** 213k  

---

Superpowers — это полная методология разработки ПО для AI-агентов, построенная на наборе композируемых навыков (skills). Вместо того чтобы просто писать код, агент с Superpowers шагает назад, задаёт уточняющие вопросы, составляет spec, разбивает на задачи и исполняет их через **subagent-driven-development** — когда каждая задача выполняется в свежем суб-агенте с двухстадийным ревью.

Поддерживает: Claude Code, Codex CLI/App, OpenCode, Gemini CLI, Cursor, Factory Droid, GitHub Copilot CLI.

---

## Установка

### Claude Code

**Официальный маркетплейс Anthropic:**
```bash
/plugin install superpowers@claude-plugins-official
```

**Superpowers Marketplace:**
```bash
/plugin marketplace add obra/superpowers-marketplace
/plugin install superpowers@superpowers-marketplace
```

### Codex CLI
```bash
/plugins
# найти Superpowers → Install Plugin
```

### Factory Droid
```bash
droid plugin marketplace add https://github.com/obra/superpowers
droid plugin install superpowers@superpowers
```

### Gemini CLI
```bash
gemini extensions install https://github.com/obra/superpowers
```

### Cursor
```
/add-plugin superpowers
```

### GitHub Copilot CLI
```bash
copilot plugin marketplace add obra/superpowers-marketplace
copilot plugin install superpowers@superpowers-marketplace
```

### OpenCode

В `opencode.json`:
```json
{
  "plugin": ["superpowers@git+https://github.com/obra/superpowers.git"]
}
```
Подробнее: [docs/README.opencode.md](https://github.com/obra/superpowers/blob/main/docs/README.opencode.md)

---

## Как это работает

```
Пользователь: "Сделай todo-приложение"
    │
    ▼
┌─────────────────────────────────┐
│ 1. Brainstorming (авто-триггер)  │
│    ─ Уточняющие вопросы          │
│    ─ Исследование альтернатив    │
│    ─ Показ spec частями          │
│    ─ Визуальный companion (опц.) │
└──────────┬──────────────────────┘
           ▼
┌─────────────────────────────────┐
│ 2. Design Approved (пользователь)│
└──────────┬──────────────────────┘
           ▼
┌─────────────────────────────────┐
│ 3. Using Git Worktrees           │
│    Изолированный workspace       │
└──────────┬──────────────────────┘
           ▼
┌─────────────────────────────────┐
│ 4. Writing Plans                 │
│    Задачи по 2-5 минут           │
│    Точные пути файлов, код,      │
│    шаги верификации              │
└──────────┬──────────────────────┘
           ▼
┌─────────────────────────────────────┐
│ 5. Subagent-Driven Development      │
│    ┌───────────────────────┐        │
│    │ Task 1: свежий агент  │────    │
│    │  → spec compliance    │  │     │
│    │  → code quality       │  │     │
│    └───────────────────────┘  │     │
│    ┌───────────────────────┐  │     │
│    │ Task N: свежий агент  │←─┘     │
│    └───────────────────────┘        │
└──────────┬──────────────────────────┘
           ▼
┌─────────────────────────────────┐
│ 6. Finishing Branch             │
│    Тесты → merge/PR/keep/discard│
└─────────────────────────────────┘
```

Ключевой принцип: **скиллы триггерятся автоматически**. Агенту не нужно вводить команды — он сам определяет, какой навык применить, основываясь на контексте разговора.

---

## Библиотека навыков

### Тестирование

| Навык | Описание |
|-------|----------|
| **test-driven-development** | RED-GREEN-REFACTOR. Включает справочник анти-паттернов тестирования |

### Отладка

| Навык | Описание |
|-------|----------|
| **systematic-debugging** | 4-фазный root cause process: root-cause-tracing, defense-in-depth, condition-based-waiting |
| **verification-before-completion** | Убедиться, что баг действительно исправлен |

### Коллаборация

| Навык | Описание |
|-------|----------|
| **brainstorming** | Сократическая проработка дизайна. Опциональный браузерный визуальный companion |
| **writing-plans** | Детальные планы имплементации с задачами по 2-5 минут |
| **executing-plans** | Пакетное исполнение с человеческими checkpoint'ами |
| **dispatching-parallel-agents** | Конкурентные subagent-воркфлоу |
| **requesting-code-review** | Pre-review чеклист |
| **receiving-code-review** | Как отвечать на feedback |
| **using-git-worktrees** | Параллельные ветки разработки через `git worktree` |
| **finishing-a-development-branch** | Merge/PR/keep/discard |
| **subagent-driven-development** | Быстрая итерация с двухстадийным ревью (spec compliance → code quality) |

### Meta

| Навык | Описание |
|-------|----------|
| **writing-skills** | Создание новых навыков по best practices |
| **using-superpowers** | Введение в систему навыков |

---

## Subagent-Driven Development — ядро Superpowers

**Ключевая инновация:** каждая задача выполняется в **свежем суб-агенте** с чистым контекстом. Это решает проблему context rot (падение точности LLM после заполнения ~50% контекстного окна).

```
Controller (основная сессия):
  ┌─────────────────────────────────┐
  │ 1. Читает план                   │
  │ 2. Для каждой задачи:            │
  │    ┌────────────────────────┐    │
  │    │ Суб-агент (чистый       │    │
  │    │ контекст)               │    │
  │    │  → пишет код            │    │
  │    │  → self-review          │    │
  │    │  → отчитывается:        │    │
  │    │    DONE / DONE_WITH_    │    │
  │    │    CONCERNS / BLOCKED / │    │
  │    │    NEEDS_CONTEXT        │    │
  │    └────────┬───────────────┘    │
  │             ▼                    │
  │    ┌────────────────────────┐    │
  │    │ Spec Compliance Review │    │
  │    │ Code Quality Review    │    │
  │    └────────────────────────┘    │
  └─────────────────────────────────┘
```

**Двухстадийное ревью:**
1. **Spec Compliance** — скептический ревьювер проверяет, что код точно соответствует spec. Читает реальный код, а не отчёт исполнителя
2. **Code Quality** — запускается только после прохождения spec compliance. Чистота кода, покрытие тестами, поддерживаемость

---

## Brainstorming Server — визуальный companion

Опциональный браузерный интерфейс для сессий брейншторминга. Когда тема требует визуалов, Superpowers предлагает показать мокáпы, диаграммы и сравнения в браузере.

- Zero-dependency Node.js сервер (HTTP + WebSocket, без Express/Chokidar/WS)
- Авто-выход через 30 мин простоя
- Мониторинг owner-PID — сервер выключается, если умирает родительская сессия
- Тёмная/светлая тема

---

## Workflow

```
ШАГ 1: Brainstorming
  Агент задаёт вопросы (по одному), не пишет код.
  Спасает design doc в docs/superpowers/specs/

ШАГ 2: User Approval
  Пользователь утверждает spec

ШАГ 3: Using Git Worktrees
  Изолированная ветка, git worktree, чистый baseline тестов

ШАГ 4: Writing Plans
  Разбивка на задачи по 2-5 минут.
  Каждая задача = точный путь файла + полный код + верификация.

ШАГ 5: Subagent-Driven Development (или Executing Plans)
  Каждая задача → свежий суб-агент → spec-review → code-review → next

ШАГ 6: Finishing Branch
  Тесты пройдены → merge/PR/keep/discard
```

---

## Философия

| Принцип | Суть |
|---------|------|
| **Test-Driven Development** | Пиши тесты сначала. Всегда |
| **Systematic over ad-hoc** | Процесс, а не угадывание |
| **Complexity reduction** | Простота как основная цель |
| **Evidence over claims** | Верифицируй, прежде чем объявить успех |

**Иерархия приоритетов инструкций:**
1. **Пользователь** (CLAUDE.md, AGENTS.md, прямые запросы) — высший приоритет
2. **Superpowers skills** — переопределяют дефолтное поведение системы
3. **System prompt** — низший приоритет

---

## Ключевые особенности v5.x

| Возможность | Описание |
|-------------|----------|
| Суб-агенты с двухстадийным ревью | Каждая задача: spec compliance → code quality |
| Visual brainstorming companion | Браузерный интерфейс для мокапов и диаграмм |
| Git worktree isolation | Каждая фича в изолированном workspace |
| Документ-ревью | Spec-review и plan-review через суб-агентов |
| Inline self-review | Заменил суб-агентные review loop'ы (экономит ~25 мин) |
| Архитектурное руководство | Design-for-isolation, file-size awareness |
| 8 поддерживаемых harness'ов | Claude, Codex, OpenCode, Gemini, Cursor, Copilot, Droid |
| Agentic skills compliance | DOT-диаграммы как исполняемые спецификации процесса |
| SUBAGENT-STOP gate | Суб-агенты не активируют полный skill workflow |
| Статус-протокол суб-агентов | DONE / DONE_WITH_CONCERNS / BLOCKED / NEEDS_CONTEXT |

---

## Требования к вкладу (для AI-агентов)

Superpowers имеет жёсткий pre-submission checklist для AI-агентов:

1. Прочитать PR template
2. Поискать существующие PRs
3. Убедиться, что проблема реальна
4. Подтвердить, что изменение относится к ядру
5. Показать человеку полный diff перед отправкой

**Не принимается:** сторонние зависимости, "compliance"-переписывания, проектная конфигурация, bulk-PR, speculative fixes, fork-specific changes, сфабрикованный контент.

---

## Сообщество

- **Discord:** https://discord.gg/35wsABTejz
- **Issues:** https://github.com/obra/superpowers/issues
- **Release announcements:** https://primeradiant.com/superpowers/
- **Блог:** https://blog.fsck.com/2025/10/09/superpowers/ (оригинальный анонс)
- **Автор:** Jesse Vincent / Prime Radiant
