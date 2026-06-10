# Hooks — эффективность автоматизации

> **Дата:** 2026-05-07
> **Версия:** 1.0
> **Источник:** [ai-agent-mechanisms-review.md](ai-agent-mechanisms-review.md)
> **Библиография:** [summary.md](summary.md#54-библиография)

---

Hooks (хуки) — детерминированные lifecycle-обработчики, выполняющие shell-команды, HTTP-запросы или MCP-вызовы в ответ на события в AI-ассистенте. В отличие от rules (вероятностное управление через инструкции), hooks обеспечивают **гарантированный enforcement** через код, а не через compliance модели.

## 4.1 Детерминированное vs вероятностное управление

Фундаментальное различие между rules и hooks: rules — **вероятностны** (модель может не последовать инструкции), hooks — **детерминированы** (код выполняется независимо от «желания» модели).

**Вероятностное управление (Rules, Skills)** `[L1]` `[L2]`:
- Curse of Instructions: compliance <100%, деградирует с ростом числа правил
- Instruction Gap: ни одна модель не достигает >95% на строгих бенчмарках
- Instruction Hierarchy: даже с обучением, приоритизация инструкций ненадёжна
- Подходит для: направления поведения, предоставления контекста, рекомендаций

**Детерминированное управление (Hooks)** `[L2]`:
- Код выполняется всегда, независимо от compliance модели
- PreToolUse hook может **заблокировать** выполнение инструмента (deny)
- PostToolUse hook может **добавить feedback** после выполнения
- Подходит для: enforcement ограничений, валидации, линтинга, форматирования

**Правило выбора** `[L1]` `[L2]`:
- Если нарушение инструкции **допустимо** (лучше, но не критично) → rules
- Если нарушение инструкции **недопустимо** (security, compliance, целостность) → hooks
- Комбинация: rules задают направление, hooks гарантируют enforcement

## 4.2 Типы хуков и их применимость

Claude Code поддерживает **27 lifecycle hook events** `[L2]`. Полный реестр — в разделе [4.7](#47-реестр-триггеров-27-событий).

**Пять типов хуков** `[L2]`:

| Тип | Механизм | Применение |
|---|---|---|
| `command` | Shell-команда (stdin/stdout/exit codes) | Линтинг, форматирование, валидация |
| `http` | POST на URL endpoint | Интеграция с CI/CD, мониторинг |
| `mcp_tool` | Вызов MCP-инструмента | Интеграция с MCP-серверами |
| `prompt` | Однотурная LLM-оценка (Haiku) | Качественная оценка результатов |
| `agent` | Многоходовая верификация с инструментами | Сложная валидация (экспериментальный) |

## 4.3 Что можно и нельзя делать в хуках

**Можно** `[L2]`:
- Блокировать выполнение инструментов (PreToolUse → deny)
- Модифицировать ввод инструментов (PreToolUse → updatedInput)
- Добавлять feedback после выполнения (PostToolUse)
- Управлять разрешениями (PermissionRequest → allow/deny)
- Заставлять Claude продолжать работу (Stop → продолжить)
- Выполнять детерминированные действия (линтинг, форматирование)

**Нельзя** `[L2]`:
- `PostToolUse` не может отменить уже выполненное действие
- Хуки не могут запускать `/`-команды или tool calls
- Несколько `PreToolUse` с `updatedInput` — последний завершившийся побеждает (недетерминированный порядок при параллельном выполнении)
- Хуки могут **ужесточать** ограничения, но не **ослаблять**: `deny` работает даже в `bypassPermissions`, но `allow` не отменяет deny-правила

## 4.4 Генерализация на другие инструменты

Хуки как концепция не уникальны для Claude Code. Разные инструменты реализуют lifecycle-автоматизацию по-разному.

| Инструмент | Механизм автоматизации | Тип | Scope |
|---|---|---|---|
| **Claude Code** | Hooks (command/http/mcp_tool/prompt/agent) | Детерминированный | PreToolUse, PostToolUse, Stop, SessionStart... |
| **Cursor** | Run on Save, lint-on-edit, pre-commit hooks интеграция | Детерминированный | На уровне IDE, не на уровне AI-агента |
| **GitHub Copilot** | GitHub Actions integration, pre-commit hooks | Детерминированный | CI/CD pipeline, не в момент генерации кода |
| **Aider** | lint/test commands, auto-commit | Детерминированный + вероятностный | Выполняются после каждого изменения |
| **Общий паттерн** | CI/CD как «внешний hook» для AI-агентов | Детерминированный | Линтинг, тесты, security scans на CI |

**Общий паттерн: CI/CD как внешний hook** `[L2]` `[L3]`:
- Все инструменты зависят от внешних проверок для enforcement
- Claude Code: hooks встроены в lifecycle → enforcement на уровне агента
- Cursor/Copilot/Aider: enforcement на уровне IDE или CI → после генерации кода
- Преимущество Claude Code: enforcement **до** выполнения действия (PreToolUse)
- Преимущество CI/CD: не зависит от конкретного AI-ассистента

**Интеграция hooks с навыками** `[L2]`:
- Хуки могут быть scoped к жизненному циклу навыка через поле `hooks` в frontmatter
- Это позволяет детерминированные действия (например, линтинг) только когда конкретный навык активен
- Хуки обеспечивают соблюдение поведения, не зависящее от compliance модели

## 4.5 Анти-паттерны

**1. Сложная логика в хуках** `[L2]` `[L3]`:
- Хуки должны быть простыми и быстрыми (default timeout: 10 минут)
- Сложная логика → непредсказуемое поведение, трудно отлаживать
- Решение: хук → delegate to script, не inline logic

**2. Ожидание контекстуального понимания** `[L2]`:
- Хук (тип `command`) — это shell-команда, не LLM. Не понимает контекст беседы
- Анти-паттерн: «если пользователь спрашивает про X, делай Y» в command-хуке
- Решение: для контекстуальных решений используй `prompt` или `agent` тип хука

**3. Гонки между параллельными хуками** `[L2]`:
- Несколько `PreToolUse` с `updatedInput` выполняются параллельно
- Последний завершившийся побеждает — недетерминированный порядок
- Решение: минимум хуков с `updatedInput` на одно событие

## 4.6 Практические рекомендации

1. **Hooks для enforcement, rules для направления** — комбинация вероятностного и детерминированного подхода `[L1]` `[L2]`
2. **PreToolUse для блокировки** — единственный механизм гарантированного запрета операций `[L2]`
3. **PostToolUse для валидации** — линтинг, форматирование, проверка результатов `[L2]`
4. **Простые хуки** — delegate сложную логику в отдельные скрипты `[L2]` `[L3]`
5. **CI/CD как внешний enforcement** — не зависит от конкретного AI-ассистента `[L2]`
6. **Не заменяй rules хуками полностью** — rules дают контекст, hooks дают гарантии `[L2]`

## 4.7 Реестр триггеров (27 событий)

Полный список lifecycle-событий Claude Code, на которые можно назначить хуки `[L2]`.

```yaml
session_lifecycle:          # Жизненный цикл сессии
  SessionStart:
    blocking: false
    description: Новая сессия или возобновление после перерыва
  Setup:
    blocking: false
    description: Запуск с --init-only/--init/--maintenance в -p режиме, одноразовая подготовка в CI
  SessionEnd:
    blocking: false
    description: Завершение сессии

prompt_processing:          # Обработка промптов (один раз за ход)
  UserPromptSubmit:
    blocking: true
    description: Пользователь отправил промпт, до обработки Claude
  UserPromptExpansion:
    blocking: true
    description: Команда / раскрылась в промпт, до попадания к Claude
  Stop:
    blocking: true
    description: Claude завершил ответ
  StopFailure:
    blocking: false
    description: Ход прерван из-за API-ошибки (stdout и exit code игнорируются)
  Notification:
    blocking: false
    description: Claude Code отправляет уведомление

tool_execution:             # Вызов инструментов (agentic loop)
  PreToolUse:
    blocking: true
    description: Перед выполнением tool call, единственный механизм гарантированного запрета
  PermissionRequest:
    blocking: false
    description: Появился диалог разрешения, возвращает JSON-решение allow/deny
  PermissionDenied:
    blocking: false
    description: Tool call отклонён auto-mode классификатором, retry: true разрешает повтор
  PostToolUse:
    blocking: false
    description: После успешного выполнения tool call
  PostToolUseFailure:
    blocking: false
    description: После неудачного выполнения tool call
  PostToolBatch:
    blocking: false
    description: После завершения batch параллельных tool calls, до следующего model call

subagents_and_tasks:        # Субагенты и задачи
  SubagentStart:
    blocking: false
    description: Запуск субагента
  SubagentStop:
    blocking: true
    description: Субагент завершил работу
  TaskCreated:
    blocking: false
    description: Создание задачи через TaskCreate
  TaskCompleted:
    blocking: false
    description: Задача отмечена как завершённая
  TeammateIdle:
    blocking: false
    description: Агент-участник команды переходит в idle

context_and_config:         # Контекст и конфигурация
  InstructionsLoaded:
    blocking: false
    description: Загружен CLAUDE.md или .claude/rules/*.md, срабатывает при старте и lazy load
  ConfigChange:
    blocking: false
    description: Изменился конфигурационный файл в течение сессии
  CwdChanged:
    blocking: false
    description: Сменилась рабочая директория (например, Claude выполнил cd)
  FileChanged:
    blocking: false
    description: Изменился файл на диске, matcher указывает отслеживаемые имена

worktree:                   # Worktree
  WorktreeCreate:
    blocking: true
    description: Создание worktree через --worktree или isolation: worktree, заменяет стандартное git-поведение
  WorktreeRemove:
    blocking: true
    description: Удаление worktree (выход из сессии или завершение субагента)

compaction:                 # Compaction
  PreCompact:
    blocking: false
    description: Перед сжатием контекста
  PostCompact:
    blocking: false
    description: После сжатия контекста

mcp_elicitation:            # MCP Elicitation
  Elicitation:
    blocking: false
    description: MCP-сервер запрашивает ввод пользователя во время tool call
  ElicitationResult:
    blocking: true
    description: Пользователь ответил на MCP-запрос, до отправки ответа серверу
```
