# Большой гайд по настройке OpenCode-проекта

**Источник:** https://datatalks.ru/opencode/index.html

---

Русскоязычное руководство по превращению OpenCode из "просто CLI" в полноценный инженерный слой проекта. Основано на официальной документации и репозитории-примере `ivanshamaev/ai-agent-codex`.

**Структура гайда (9 глав):** введение, быстрый старт, анатомия проекта, агенты и skills, конфиг и разрешения, командные процессы, MCP и интеграции, best practices, development process, пример проекта.

**Эталонная структура OpenCode-слоя:**
```
AGENTS.md              — проектный контракт
opencode.json          — control plane
instructions/          — долгоживущие правила
.opencode/agents/      — role-based subagents
.opencode/skills/      — playbooks
.opencode/patterns/    — безопасность
docs/specs/            — durable спецификации
mcp/local/ + mcp/remote/ — интеграции
```

**Ключевая идея:** "разница между CLI запускается и агент стабильно помогает всей команде — огромная". Полезные каталоги: cursor.directory, MCP Market, skills.sh, SkillHub.

---

**↪️ Категория:** [[README]]
