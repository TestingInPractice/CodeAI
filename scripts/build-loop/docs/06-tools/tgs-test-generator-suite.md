# Test Generator Suite (TGS) — генератор API-тестов на LLM

**Источник:** https://habr.com/ru/articles/1038390/
**Автор:** Илья Акрицкий

---

TGS (Test Generator Suite) — веб-приложение на FastAPI для автоматизации трёх рутинных QA-задач через LLM:

1. **API-тесты** — OpenAPI spec → Postman collection v2.1
2. **Тест-кейсы** — Jira-тикет → структурированные сценарии в TMS
3. **Doc Review** — оценка полноты требований

**Архитектура:** монолит FastAPI + Pydantic, слой адаптеров для TMS и LLM-провайдеров (любой OpenAI-совместимый: GPT-4o, Claude, DeepSeek, локальные через vLLM/Ollama). Интеграция с Jira, Confluence, Zephyr Scale, TestRail, TestIT.

**Ключевой урок для AI-разработки:** хороший харнесс ≠ замена человека, а снятие повторяющейся работы. LLM-вывод парсится с защитой от markdown-обёрток и валидацией JSON-схемы.

---

**↪️ Категория:** [[README]]
