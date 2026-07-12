# CodeAI Platform — Technology Stack

**Status:** Active  
**Date:** 2026-07-11  
**Rule:** Technology Stack следует за архитектурой. При смене технологии обновлять здесь.

---

## Текущая реализация (2026-07)

| Подсистема | Технология | Версия | License | Почему |
|-----------|-----------|--------|---------|--------|
| **Spec Engine** | Custom Python | — | — | Нет готового решения для spec generation + validation |
| **Workflow Engine** | python-statemachine | v3.x | MIT | Full statechart, guards, async, dict-based serialization |
| **OODA Runtime** | LangGraph | v1.x | MIT | Typed state, checkpointing, HITL, lowest token overhead |
| **Knowledge Layer** | MCP + Obsidian + OHS | — | — | Существующая инфраструктура, hybrid search |
| **Memory Layer** | JSON + SQLite | — | — | Простота, zero-config, файл-based persistence |
| **Judge Engine** | Custom + DeepEval | v4.x | Apache-2.0 | 50+ metrics, CI/CD, extensible BaseMetric |

---

## Альтернативы

### Workflow Engine

| Технология | Stars | License | Плюсы | Минусы |
|-----------|-------|---------|-------|--------|
| **python-statemachine** (current) | 1,250 | MIT | Full statechart, async, typed | Меньше stars |
| `transitions` | 6,550 | MIT | Проще, больше stars | Нет parallel states |
| Custom FSM | — | — | Полный контроль | Нужно писать всё самим |

### OODA Runtime

| Технология | Stars | License | Плюсы | Минусы |
|-----------|-------|---------|-------|--------|
| **LangGraph** (current) | 36,700 | MIT | Checkpointing, HITL, time travel | LangChain dependency |
| Custom runtime | — | — | Полный контроль | Нужно писать checkpointing |
| CrewAI | 55,000 | MIT | Role-based, быстро | Хуже на сложных workflow |

### Knowledge Layer

| Технология | Stars | License | Плюсы | Минусы |
|-----------|-------|---------|-------|--------|
| **MCP + OHS** (current) | — | — | Существует, работает | Привязка к Obsidian |
| GraphRAG | — | — | Граф связей | Сложнее в настройке |
| Vector DB (Chroma/Qdrant) | — | — | Semantic search | Дополнительная инфраструктура |

### Memory Layer

| Технология | Stars | License | Плюсы | Минусы |
|-----------|-------|---------|-------|--------|
| **JSON + SQLite** (current) | — | — | Zero-config, файл-based | Нет scaling |
| Redis | — | BSD | Быстро, pub/sub | Сервер required |
| Postgres | — | PostgreSQL | Надёжно, JSONB | Сервер required |

### Judge Engine

| Технология | Stars | License | Плюсы | Минусы |
|-----------|-------|---------|-------|--------|
| **Custom + DeepEval** (current) | 16,800 | Apache-2.0 | 50+ metrics, CI/CD | LLM API dependency |
| Promptfoo | 23,000 | MIT | YAML config, гибкость | TypeScript primary |
| Custom only | — | — | Полный контроль | Нужно писать всё самим |

---

## Когда менять технологию

| Сигнал | Действие |
|--------|----------|
| Библиотека заброшена (>1 года без обновлений) | Оценить альтернативы, мигрировать |
| Появилось критическое ограничение | Создать ADR, оценить замену |
| Появилась значительно лучшая альтернатива | Создать ADR, оценить ROI миграции |
| Проблемы производительности | Профилировать, оценить замену |
| Проблемы безопасности | Немедленная оценка, создать ADR |

---

## Зависимости (requirements.txt — будущее)

```
# Core
python-statemachine>=3.0
langgraph>=1.0

# Judge (optional)
deepeval>=4.0

# Knowledge Layer
# MCP protocol (встроен в opencode)

# Memory Layer
# sqlite3 (встроен в Python)

# Development
pytest>=7.0
pytest-asyncio>=0.21
```
