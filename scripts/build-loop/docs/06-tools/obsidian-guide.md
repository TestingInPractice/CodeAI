# Obsidian — инструкция для AI-агентов

**Источник:** [obsidian.md](https://obsidian.md/) (официальная документация)
**CLI docs:** [obsidian.md/help/cli](https://obsidian.md/help/cli)

---

## Обзор

Obsidian — markdown-редактор для connected notes. Для AI-агентов интересен как **persistent knowledge graph** с доступом через CLI, MCP и плагины.

## Obsidian CLI

Устанавливается через настройки Obsidian: **Settings → General → Command line interface** (вкл). После регистрации CLI доступен как `obsidian` в терминале. Требует запущенного приложения Obsidian.

### Основные команды

| Команда | Описание |
|---------|----------|
| `obsidian help` | Справка |
| `obsidian daily` | Открыть сегодняшний daily note |
| `obsidian daily:append content="текст"` | Добавить в daily note |
| `obsidian search query="..."` | Поиск по хранилищу |
| `obsidian read` | Прочитать текущий файл |
| `obsidian tasks daily` | Список задач из daily note |
| `obsidian create name="..." template=..."` | Создать заметку из шаблона |
| `obsidian tags counts` | Теги с частотой |
| `obsidian diff file=README from=1 to=3` | Diff версий файла |
| `obsidian unresolved` | Нераcрешенные ссылки |
| `obsidian files sort=modified limit=5 --copy` | Файлы сортированные, скопировать |

### Команды разработчика

| Команда | Описание |
|---------|----------|
| `obsidian devtools` | Открыть DevTools |
| `obsidian plugin:reload my-plugin` | Перезагрузить плагин |
| `obsidian dev:screenshot file=shot.png` | Скриншот |
| `obsidian eval "app.vault.getFiles().length"` | Выполнить JS |
| `obsidian dev:errors` | JS ошибки |
| `obsidian dev:css selector=".workspace"` | CSS свойства |
| `obsidian dev:dom selector=".nav"` | DOM запросы |

### Пример автоматизации (bash)

```bash
#!/bin/bash
obsidian daily
obsidian daily:append content="- [ ] Review inbox"
obsidian daily:append content="- [ ] Check calendar"
obsidian files sort=modified limit=5 --copy
obsidian unresolved
obsidian search query="status::active" vault="Notes" format=json
```

## Obsidian Hybrid Search (OHS)

MCP-сервер для гибридного поиска: BM25 + fuzzy title + семантический.

Подробно: `02-mcp/obsidian-hybrid-search-ohs.md` (CLI) и `docs/opencode-docs/obsidian/36-obsidian-hybrid-search-ohs.md` (полная документация).

## Headless Sync

Obsidian Sync без GUI — для серверов, CI/CD, агентов. Энд-ту-энд шифрование, версионирование, selective sync.

## Архитектура интеграции с AI

```
AI Agent (Claude Code / OpenCode)
       │
       ├── CLI (obsidian read/search/create)
       │      └── через AGENTS.md инструкции
       │
       ├── MCP (OHS)
       │      └── семантический поиск по vault
       │
       └── Headless Sync
              └── синхронизация с сервером / CI
```

## Контекст-инжиниринг с Obsidian

Obsidian vault как **Source of Truth контекста**:

1. **AGENTS.md + Obsidian** — инструкции агентам в AGENTS.md, глубокая база знаний в Obsidian
2. **Cross-session memory** — фазы GSD выполняются в чистых сессиях, OHS достаёт решения предыдущих фаз
3. **Knowledge graph** — backlinks и semantic search вместо плоского grep
4. **Canvas** — визуальные диаграммы архитектуры, ADR, flowcharts

## Установка

1. Скачать Obsidian: [obsidian.md/download](https://obsidian.md/download)
2. Создать vault (локальная папка с .md файлами)
3. Включить CLI: Settings → General → Command line interface
4. (Опционально) Установить OHS: `npm install -g obsidian-hybrid-search`
5. (Опционально) Настроить AGENTS.md для использования Obsidian CLI

## AGENTS.md фрагмент

```markdown
## Obsidian

Используй Obsidian CLI для работы с базой знаний:
- `obsidian search query="..."` — поиск по хранилищу
- `obsidian read` — чтение текущего файла
- `obsidian create name="..." template=...` — создание заметки
- `obsidian tags counts` — теги

Для семантического поиска используй OHS (MCP):
- поиск связей между заметками через эмбеддинги
- поиск по смыслу, а не по точному совпадению
- backlinks/outgoing links для графа решений
```

---

**↪️ Категория:** [[README]]
