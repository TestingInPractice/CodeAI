# GSD (Get Shit Done) — Spec-Driven Development через контекст-инжиниринг

> **Активный репозиторий:** https://github.com/open-gsd/gsd-core (open-gsd/gsd-core, бывший get-shit-done-redux)  
> **Легаси:** https://github.com/gsd-build/get-shit-done (архивирован, 63.8k ★)  
> **npm:** `@opengsd/get-shit-done-redux`  
> **Авторы:** open-gsd team (форк), оригинал — TÂCHES  
> **Лицензия:** MIT  
> **Сайт:** https://opengsd.net

---

GSD — это лёгкая система meta-prompting'а, контекст-инжиниринга и spec-driven разработки для Claude Code, OpenCode, Gemini CLI, Codex, Copilot, Cursor, Windsurf и других AI-агентов.

**Решает context rot** — деградацию качества ответов по мере заполнения контекстного окна. Вместо того чтобы держать всё в одной сессии, GSD разбивает работу на фазы и выполняет каждую в **свежем суб-агенте с 200k токенов**.

---

## История: разделение проекта

В мае 2026 года оригинальный репозиторий (`gsd-build/get-shit-done`, 63.8k ★) был покинут создателем после инцидента с meme-coin rug-pull. Команда мейнтейнеров продолжила разработку в форке `open-gsd/get-shit-done-redux` (теперь `open-gsd/gsd-core`):

| | Легаси | Активный |
|---|---|---|
| Репозиторий | `gsd-build/get-shit-done` | `open-gsd/gsd-core` |
| npm | `@gsd-build/get-shit-done` | `@opengsd/get-shit-done-redux` |
| Статус | Архив (редирект) | Активная разработка |
| Звёзд | 63.8k | 1.8k |

---

## Установка

```bash
npx @opengsd/get-shit-done-redux@latest
```

Инсталлятор определяет окружение (Claude Code, OpenCode, Gemini CLI, Kilo, Codex, Copilot, Cursor, Windsurf и др.) и устанавливает глобально или локально.

**Профили установки:**
- `--profile=core` / `--minimal` — только 6 команд основного цикла
- `--profile=standard` — core + управление фазами
- По умолчанию — полная установка

**Рекомендуется запускать с:**
```bash
claude --dangerously-skip-permissions
```

---

## Основной цикл — 6 команд

```
/gsd-new-project                  ─── Инициализация
    │                                 Вопросы → research → требования → roadmap
    ▼
/gsd-discuss-phase [N]            ─── Обсуждение
    │                                 Фиксация решений до планирования
    ▼
/gsd-plan-phase [N]               ─── Планирование
    │                                 Research → план → verify (цикл)
    ▼
/gsd-execute-phase <N>            ─── Исполнение
    │                                 Параллельные волны, свежий контекст
    ▼
/gsd-verify-work [N]              ─── Верификация
    │                                 Walkthrough + debug-агенты
    ▼
/gsd-ship [N]                     ─── Ship
/gsd-complete-milestone                PR → archive → tag
/gsd-new-milestone                     Следующий milestone
```

## Как это работает

```
          ┌──────────────────────────────────────┐
          │         Основная сессия               │
          │  Контекст ~30-40%                     │
          │                                       │
          │  PROJECT.md (vision)                  │
          │  REQUIREMENTS.md (scope)              │
          │  ROADMAP.md (куда идём)              │
          │  STATE.md (текущая позиция)           │
          │  CONTEXT.md (решения по фазе)         │
          └──────────┬───────────────────────────┘
                     │
     ┌───────────────┼───────────────┐
     ▼               ▼               ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│ Research │  │  Plan    │  │ Execute  │
│ Агент    │  │  Агент   │  │ Агент    │
│ 200k ctx │  │ 200k ctx │  │ 200k ctx │
└──────────┘  └──────────┘  └──────────┘
     │               │               │
     └───────────────┼───────────────┘
                     ▼
          ┌──────────────────────┐
          │  Verify + Debug      │
          │  агенты              │
          └──────────────────────┘
```

**Ключевой принцип:** исследователи, планировщики и исполнители каждый раз стартуют со свежим 200k-токен контекстом, получая ровно то, что нужно. Основная сессия остаётся на ~30–40% контекстного окна.

## Команды

| Команда | Описание |
|---------|----------|
| `/gsd-new-project` | Вопросы → research → requirements → roadmap |
| `/gsd-map-codebase` | Анализ стека, архитектуры, конвенций (перед new-project) |
| `/gsd-discuss-phase [N]` | Захват решений по реализации до планирования |
| `/gsd-plan-phase [N]` | Research + план + verify в цикле |
| `/gsd-execute-phase <N>` | Параллельное исполнение планов |
| `/gsd-verify-work [N]` | Приёмочное тестирование |
| `/gsd-ship [N]` | PR из верифицированной фазы |
| `/gsd-progress --next` | Авто-детект следующего шага |
| `/gsd-complete-milestone` | Архивация milestone и тег релиза |
| `/gsd-new-milestone` | Старт следующей версии |
| `/gsd:surface` | Вкл/выкл кластеры скиллов без переустановки |
| `/gsd-code-review` | Code review с опциональным fallow pre-pass |
| `/gsd-settings` | Обновление конфигурации |

## Почему это работает

### 1. Контекстный блот — решён

По мере роста сессии качество падает. GSD выносит тяжёлую работу в свежие суб-агентные контексты:

- **Research Agent** — изучает требования, стек, альтернативы
- **Plan Agent** — разбивает на задачи, проверяет полноту
- **Execute Agent** — пишет код в параллельных волнах
- **Verify Agent** — проверяет результат, диагностирует ошибки

### 2. Разделяемая память между сессиями

Структурированные артефакты, переживающие границы сессий:

| Файл | Содержит |
|------|----------|
| `PROJECT.md` | Видение продукта |
| `REQUIREMENTS.md` | Scope и требования |
| `ROADMAP.md` | План по фазам |
| `STATE.md` | Текущая позиция и решения |
| `CONTEXT.md` | Детали реализации по фазам |

Каждая новая сессия загружает эти файлы и знает, где остановились.

### 3. Верификация — обязательна

`/gsd-verify-work` — проход по тому, что построено. Сломанное получает диагностированный план фикса, готовый к немедленному `/gsd-execute-phase`.

## Конфигурация

Настройки в `.planning/config.json`. Задаются при `/gsd-new-project` или через `/gsd-settings`.

| Параметр | Что контролирует |
|----------|------------------|
| `mode` | `interactive` (подтверждать каждый шаг) или `yolo` (авто-утверждение) |
| Model profiles | `quality` / `balanced` / `budget` — модель для каждого агента |
| `workflow.research` | Вкл/выкл research-агента |
| `workflow.plan_check` | Вкл/выкл проверку планов |
| `workflow.verifier` | Вкл/выкл верификатора |
| `parallelization.enabled` | Параллельное исполнение независимых планов |

**Fallow structural review:** `code_quality.fallow.enabled = true` добавляет fallow pre-pass к `/gsd-code-review`. Требует `npm install -D fallow@^2.70.0`.

## Архитектура

```
                    ┌──────────────────┐
                    │  .planning/       │
                    │  config.json      │
                    │  PROJECT.md       │
                    │  REQUIREMENTS.md  │
                    │  ROADMAP.md       │
                    │  STATE.md         │
                    │  CONTEXT.md       │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
    ┌────────────────┐ ┌──────────┐ ┌──────────────┐
    │ Research Loop  │ │Plan Loop │ │Execute Wave  │
    │                │ │          │ │              │
    │ 1. Research    │ │1. Plan   │ │ Task A  Task B
    │ 2. Review      │ │2. Verify │ │ Task C  Task D
    │ 3. Iterate     │ │3. Iterate│ │              │
    └────────────────┘ └──────────┘ └──────────────┘
```

**Research Loop:**
1. Исследование — агент изучает требования и стек
2. Review — проверка исследования
3. Итерация до прохождения

**Plan Loop:**
1. Планирование — разбивка на задачи с точными путями
2. Verify — проверка плана суб-агентом
3. Итерация до прохождения

**Execute Wave:**
- Независимые задачи выполняются параллельно
- Каждая задача = атомарный коммит
- После волны — автоматическое продолжение

## Troubleshooting

| Проблема | Решение |
|----------|---------|
| Команды не отображаются | Перезапустить runtime после установки |
| Codex — дублирующиеся gsd-* | Обновить до Codex CLI 0.130.0+ |
| Что-то сломалось | `npx @opengsd/get-shit-done-redux@latest` (идемпотентно) |
| Docker/контейнеры | `CLAUDE_CONFIG_DIR=/home/user/.claude npx @opengsd/get-shit-done-redux --global` |

---

## Документация

- **User Guide:** https://github.com/open-gsd/gsd-core/blob/next/docs/USER-GUIDE.md
- **Commands:** https://github.com/open-gsd/gsd-core/blob/next/docs/COMMANDS.md
- **Configuration:** https://github.com/open-gsd/gsd-core/blob/next/docs/CONFIGURATION.md
- **Architecture:** https://github.com/open-gsd/gsd-core/blob/next/docs/ARCHITECTURE.md
- **Changelog:** https://github.com/open-gsd/gsd-core/blob/next/CHANGELOG.md

## Сообщество

- **Discord:** https://discord.gg/mYgfVNfA2r
- **OpenCode port:** https://github.com/rokicool/gsd-opencode
- **Сайт:** https://opengsd.net
