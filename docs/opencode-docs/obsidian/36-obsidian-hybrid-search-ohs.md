# Obsidian Hybrid Search (OHS) — семантический поиск для AI-агентов

> **Источник:** https://github.com/flowing-abyss/obsidian-hybrid-search  
> **Статья:** https://habr.com/ru/articles/1040948/  
> **Автор:** flowing_abyss  
> **npm:** `obsidian-hybrid-search`  
> **Плагин Obsidian:** https://flowing-abyss.com/Obsidian-Hybrid-Search---plugin

---

OHS — это MCP-сервер и CLI, который даёт AI-агентам **гибридный поиск** по Obsidian-хранилищу: BM25 + fuzzy title (триграм) + семантический (векторный) с объединением через RRF и опциональным cross-encoder rerank.

Без OHS агенты ищут по заметкам через `glob`/`grep` как по коду — теряются смысловые связи. OHS превращает хранилище в семантический граф, доступный через MCP-протокол.

---

## Установка

### CLI (глобально)

```bash
npm install -g obsidian-hybrid-search
```

Переменные окружения (в `.zshrc`):

```bash
export OBSIDIAN_VAULT_PATH="/path/to/your/vault"
export OBSIDIAN_IGNORE_PATTERNS=".obsidian/**,templates/**"
export OPENAI_API_KEY="sk-or-v1-..."
export OPENAI_BASE_URL="https://openrouter.ai/api/v1"
export OPENAI_EMBEDDING_MODEL="baai/bge-m3"
```

Удобные алиасы:

```bash
alias ohs='obsidian-hybrid-search'
alias ohss='obsidian-hybrid-search --mode semantic'
alias ohst='obsidian-hybrid-search --mode title'
alias ohsf='obsidian-hybrid-search --mode fulltext'
alias ohsi='obsidian-hybrid-search reindex'
alias ohsst='obsidian-hybrid-search status'
```

Индексация хранилища:

```bash
ohs reindex --force
```

Поиск:

```bash
ohs "управление вниманием"
ohs "docker qdrant" --mode fulltext
ohs "zettleksten" --mode title
ohs --path notes/pkm/zettelkasten.md --related
```

### MCP (для Claude Code, OpenCode и др.)

`.mcp.json` в корне проекта:

```json
{
  "mcpServers": {
    "obsidian-hybrid-search": {
      "command": "npx",
      "args": ["-y", "-p", "obsidian-hybrid-search@latest", "obsidian-hybrid-search-mcp"],
      "env": {
        "OBSIDIAN_VAULT_PATH": "/path/to/your/vault",
        "OBSIDIAN_IGNORE_PATTERNS": ".obsidian/**,templates/**",
        "OPENAI_API_KEY": "sk-or-v1-...",
        "OPENAI_BASE_URL": "https://openrouter.ai/api/v1",
        "OPENAI_EMBEDDING_MODEL": "baai/bge-m3"
      }
    }
  }
}
```

После запуска агента хранилище индексируется автоматически. Инкрементальное обновление через Chokidar — без ручной переиндексации.

---

## Как работает гибридный поиск

```
         ┌──────────────────────┐
         │   Поисковый запрос    │
         └──────────┬───────────┘
                    │
         ┌──────────┴──────────┐
         ▼                     ▼
┌─────────────────┐   ┌─────────────────┐
│  Лексический     │   │  Семантический   │
│                  │   │                  │
│ ┌──────────────┐ │   │ ┌──────────────┐ │
│ │ BM25         │ │   │ │ Эмбеддинги   │ │
│ │ (точный FTS) │ │   │ │ (multilingual│ │
│ ├──────────────┤ │   │ │  e5-small)   │ │
│ │ Fuzzy title  │ │   │ └──────────────┘ │
│ │ (триграм)    │ │   └─────────────────┘
│ └──────────────┘ │
└─────────────────┘
         │                     │
         └──────────┬──────────┘
                    ▼
         ┌──────────────────────┐
         │  RRF (Reciprocal     │
         │  Rank Fusion)        │
         └──────────┬───────────┘
                    │
         ┌──────────▼───────────┐
         │  Cross-encoder       │
         │  rerank (bge-reranker│
         │  v2-m3, опционально) │
         └──────────┬───────────┘
                    ▼
         ┌──────────────────────┐
         │  Ранжированный       │
         │  список заметок      │
         └──────────────────────┘
```

### Три режима поиска

| Режим | Алгоритм | Когда использовать |
|-------|----------|-------------------|
| **BM25** | Полнотекстовый FTS | Точное ключевое слово, например `docker qdrant` |
| **Fuzzy title** | Триграм по названиям + aliases | Не помню точное название, толерантен к опечаткам |
| **Semantic** | Векторный по эмбеддингам | Нужны смысловые связи, а не точное совпадение |

### RRF (Reciprocal Rank Fusion)

Объединяет три ранжированных списка: заметка, стабильно высокая во всех режимах, побеждает заметку с пиком только в одном. Нивелирует слабости каждого метода.

### Cross-encoder rerank (опция)

Модель `bge-reranker-v2-m3` переранжирует результаты гибридного поиска для максимальной точности. Требовательна к железу, поэтому выключена по умолчанию.

---

## Возможности

| Возможность | Описание |
|-------------|----------|
| Aliases и теги | Индексируются и участвуют в поиске |
| Фильтрация | По тегам и папкам |
| Граф заметок | backlinks (-1/-2) и outgoing links (+1/+2) для любой заметки |
| SQLite-индекс | Один файл в корне хранилища, без внешних серверов |
| Инкрементальная индексация | Chokidar следит за изменениями, MCP-режим обновляется в фоне |
| Open via Obsidian CLI | `ohs "поиск" --open` открывает результаты в Obsidian |
| JSON-вывод | `ohs "запрос" --json` для скриптов и пайплайнов |

---

## Паттерны использования с AI-агентами

### 1. MCP-щуп (основной)

Агент сам решает, когда искать — не нужно вставлять заметки в контекст вручную:

```
Пользователь: "найди всё, что я писал про spaced repetition, и выдели противоречия"
Агент: → search("spaced repetition")
       → read(scores[0].path), read(scores[1].path), ...
       → синтез с цитатами
```

### 2. Cross-session memory для GSD

Фазы GSD выполняются в чистых сессиях (Ralph Loop). OHS — persistent storage между ними:

```
Фаза 1: /gsd-discuss-phase 1 → решения сохранены в Obsidian
Фаза 7: /gsd-discuss-phase 7 → OHS: ohs "решения фаза 1"
         агент находит и использует предыдущие решения
         не перегружая контекст
```

### 3. Discourse Graph поверх Spec-Driven Development

GStack пишет design doc → Obsidian сохраняет как связанную заметку. Superpowers добавляет TDD-план → следующая заметка ссылается на spec. Граф решений растёт между спринтами:

```
spec.md ←── plan.md ←── implementation.md ←── review.md
   │                                              │
   └────── discourse graph ───────────────────────┘
         (OHS находит связи через эмбеддинги)
```

### 4. Архитектурный граф

```
ohs --path docs/adr/0011-skill-surface-budget-module.md --related
→ -1 backlinks: какие заметки ссылаются на это ADR
→ +1 outgoing: какие решения из него вытекают
```

Быстрый способ для агента понять контекст решения, не читая весь текст.

---

## Модели эмбеддингов

| Модель | Размер | Языки | Где запускать |
|--------|--------|-------|---------------|
| `Xenova/multilingual-e5-small` | 117 MB | 100+ (вкл. русский) | По умолчанию, встроенная |
| `baai/bge-m3` | ~2.2 GB | Мультиязычная | OpenRouter / Ollama с GPU |
| Любая OpenAI-совместимая | — | — | Через `OPENAI_BASE_URL` |

---

## Интеграция с фреймворками

### GStack
OHS как MCP → агенты GStack ищут по графу решений вместо grep. `/office-hours` пишет doc → OHS индексирует → `/plan-ceo-review` находит релевантные предыдущие решения.

### GSD
Фазы GSD живут в чистых сессиях. OHS — внешняя память между ними. `/gsd-discuss-phase` → решения в Obsidian → следующая сессия находит через гибридный поиск.

### Superpowers
Brainstorming сохраняет spec → OHS индексирует → subagent-ы находят при двухстадийном ревью.

### Ralph Loop
Оркестратор не засоряет контекст деталями фаз — они в Obsidian. Headless-сессии через OHS получают ровно то, что нужно.

---

## Ограничения

1. **Не заменяет систему заметок** — автор предупреждает: мощный поиск провоцирует беспорядок. Сила PKM в преемственности, а не в быстром поиске
2. **Cross-encoder требователен к GPU** — rerank выключен по умолчанию
3. **Первая индексация** — на большом хранилище может занять время (дальше — инкрементально)
