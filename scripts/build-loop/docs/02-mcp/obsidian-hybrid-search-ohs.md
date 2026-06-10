# Obsidian Hybrid Search (OHS) — MCP для семантического поиска

**Источник:** https://habr.com/ru/articles/1040948/
**Автор:** flowing_abyss

---

MCP-сервер + CLI (`obsidian-hybrid-search`) для гибридного поиска по Obsidian-хранилищу. Объединяет три режима:

- **BM25** — полнотекстовый поиск
- **Fuzzy title** — триграмный поиск (терпит опечатки)
- **Semantic** — векторный по эмбеддингам (Xenova/multilingual-e5-small, 117 MB, 100+ языков)

Ансамблирование через RRF, опционально cross-encoder reranking (bge-reranker-v2-m3).

**CLI:** `ohs "запрос"` с флагами `--mode`, `--rerank`, `--json`, `--open`, `--related`
**MCP:** подключается к Claude Code / OpenCode через `.mcp.json`

**Актуальность:** пример проектирования MCP-сервера для knowledge management. Показывает, как дать агенту семантический доступ к базе знаний вместо грубого glob/grep.

---

**↪️ Категория:** [[README]]
