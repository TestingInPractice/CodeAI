# microsoft/skills — 174 скилла для AI агентов по Azure

**Источник:** https://github.com/microsoft/skills
**Звёзд:** ~2.5k

---

Репозиторий содержит 174 domain-specific skill'а для AI coding agents, работающих с Azure SDK и Microsoft AI Foundry.

**Структура:**
- Skills: Python (39), .NET (28), TypeScript (25), Java (25), Rust (7) + Core (10) + Foundry (11)
- MCP-серверы: Microsoft Docs, Context7, GitHub, Playwright, Terraform, ESLint
- Плагины: deep-wiki (AI wiki-генератор), azure-skills (Azure MCP + Foundry sub-skills)
- AGENTS.md шаблон для конфигурации поведения агента

**Установка:** `npx skills add microsoft/skills`

**Важный принцип:** "Use skills selectively. Loading all skills causes context rot." — загрузка всех скиллов подряд ведёт к раздуванию контекста.

---

**↪️ Категория:** [[README]]
