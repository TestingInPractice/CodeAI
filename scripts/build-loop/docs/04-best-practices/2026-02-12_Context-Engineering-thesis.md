---
tags: [context-engineering, best-practices]
aliases: [Context Engineering тезисы]
---
# Context Engineering — тезисы

**Источник:** datatalks.ru, перевод статьи "Data teams should become context teams"
**Ссылка:** https://datatalks.ru/context-engineering-data-teams/
**Оригинал:** https://thenewaiorder.substack.com/p/data-teams-should-become-context

---

Концепция **Context Engineering** — data-команды должны стать командами контекста для AI-агентов.

- **Context Engineering = Data Governance + Data Engineering + Data Science**, но вместо данных — контекст для агентов
- **Проблема:** сегодня AI-агенты подключаются напрямую к сырым источникам (диски, Notion, почта) — как BI к продакшен-БД 10 лет назад
- **Нужен контекстный слой:** единый, управляемый, версионируемый Source of Truth для знаний компании

### Оптимальный контекст агента — 4 метрики:
- **Доля ответов** — % вопросов, на которые агент может ответить
- **Точность** — % корректных ответов
- **Стоимость** — расходы на LLM
- **Скорость** — время ответа

### Компромиссы:
- Мало контекста → галлюцинации, пропущенные нюансы
- Много контекста → дорого (1M токенов Claude Opus 4.5 = $5, 50-100K/запрос = ~$0.50) + шум размывает сигнал

### Context Stack = Data Stack, но для знаний:
- Ingestion источников контекста
- Трансформация (выбор source of truth)
- Контекстный слой
- Оркестрация для актуальности
- Мониторинг AI

### Context Sciences — eval-driven подход:
- Определить метрики успеха (accuracy, cost, speed)
- Создать unit-тесты из промптов + ожидаемых ответов
- Менять контекст → прогонять тесты → измерять → итерировать
- Дополнительная сложность: измерение надёжности агента (LLM-as-judge, exact match, проверка файлов)

### Как войти в Context Engineering сейчас:
1. **Coding agents** (Cursor, Claude Code, Cowork, Codex) — контекст читается из файлов, прозрачно, управляемо
2. **In-house агенты** — полный контроль над конвейером контекста

### Ссылки из статьи:
- [12-Factor Agents](https://github.com/humanlayer/12-factor-agents/)
- [Context Engineering Guide (DataCamp)](https://www.datacamp.com/blog/context-engineering)
- [awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills)
- [microsoft/skills](https://github.com/microsoft/skills)
- [microsoft/ai-agents-for-beginners](https://github.com/microsoft/ai-agents-for-beginners)
- [Astronomer — AI agent tooling for Airflow](https://github.com/astronomer/agents)
- [data-formulator (Microsoft)](https://github.com/microsoft/data-formulator)

---

**↪️ Категория:** [[README]]
