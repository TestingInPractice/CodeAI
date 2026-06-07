# INDEX — Полный список документации

## Build Loop (скрипты)

| Файл | Описание |
|------|----------|
| `setup.sh` | Установка инструментов и инициализация проекта |
| `init.sh` | Инициализация AGENTS.md и структуры проекта |
| `decompose.sh` | Декомпозиция spec на фазы |
| `build-loop.sh` | Главный оркестратор: установка + декомпозиция + запуск |
| `run-loop.sh` | Запуск одной фазы Build Loop |
| `next-phase.sh` | Показать следующую фазу из phases.json |

---

## Build Loop (транскрипты и тезисы)

Каждый видео-разбор состоит из двух файлов: `*.md` (полная стенограмма) + `*-thesis.md` (структурированные тезисы для агента).

### GSD & Superpowers (Владилен Минин, русский)
- `2025-07-26_GSD-Superpowers.md` / `*-thesis.md`
- **Video:** https://youtu.be/SOm_F7UtJno
- SDLC эволюция 2026, GSD pipeline (6 core hooks + 73 advanced), Superpowers (7 skills), сравнение фреймворков

### GSD vs Paul (английский)
- `2025-06-07_GSD-vs-Paul.md` / `*-thesis.md`
- **Video:** https://youtu.be/MppKHh_MfFc
- 7 критических проблем GSD (context loss, broken loop, fake verification, drift, token cost, parallel conflicts, silent drift) и как Paul решает их через sequential processing + обязательный UAT

### GSD for OpenCode (Владилен Минин, английский)
- `2025-07-26_GSD-for-OpenCode.md` / `*-thesis.md`
- **Video:** https://youtu.be/zRJ0UWHBjCY
- Адаптация GSD Tasher'а для OpenCode: sub-agent архитектура, отдельные context windows, параллельное исполнение с верификацией

### GSD vs OpenSpec (английский)
- `2025-07-26_GSD-vs-OpenSpec.md` / `*-thesis.md`
- **Video:** https://youtu.be/6FRk19CZSBY
- Сравнение GSD и OpenSpec (оба пересобрали NewWriter): OpenSpec: 1ч52мин / 35М токенов; GSD: 6ч46мин / 126М токенов; GSD дал сильнее repo (тесты/lint/typecheck) но в 3.6x дороже

### MCP Tools — Telegram Watcher (Let's Code Drew, русский)
- `2025-06-07_MCP-tools-telegram-watcher.md` / `*-thesis.md`
- **Video:** https://youtu.be/mBA9Vk1jXDE
- 6 фич MCP (3 серверных + 3 клиентских), создание MCP сервера на Python через OpenCode, Telegram Watcher с 4 tools, подключение к Claude Code

### DOTI — ИИ-агенты без хаоса в коде (русский)
- `2025-07-26_DOTI.md`
- **Video:** https://youtu.be/q9Pbvgj3188
- DOTI — методика работы с AI-агентами без хаоса, структурированный подход к постановке задач

### Hermes agent. Как ставить задачи агенту? (русский)
- `2025-07-26_Hermes-agent.md`
- **Video:** https://youtu.be/nBSd9-wxCVQ
- Принципы постановки задач AI-агентам в парадигме Hermes agent

### Простые подходы к системному улучшению AI-продуктов (русский)
- `2025-07-26_AI-products-systematic-improvement.md`
- **Video:** https://youtu.be/BGZDLKPMgEo
- Практические подходы к системному улучшению AI-продуктов

---

## Внешние инструменты

| Файл | Описание |
|------|----------|
| `browse-sh.md` | **browse.sh** — Browser CLI и каталог веб-скиллов для агентов, установка через `npm install -g browse`, сотни готовых skills для Amazon, Airbnb, LinkedIn, FedEx и др. |

---

## Структура репозитория (основные разделы)

| Путь | Описание |
|------|----------|
| `AGENTS.md` | Главный индекс репозитория, карта всех разделов |
| `scripts/build-loop/` | Shell-скрипты Build Loop (оркестрация AI-разработки) |
| `scripts/build-loop/transcripts/` | Стенограммы и тезисы с YouTube-разборов |
| `docs/opencode-docs/` | Документация OpenCode |
| `docs/opencode-guide/` | Гайды по настройке OpenCode |
| `docs/skills/` | Набор навыков для Azure, Foundry, Python, TypeScript, Java, .NET, Rust и др. |
