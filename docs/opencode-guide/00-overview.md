# Как превратить OpenCode в полноценный слой проекта, а не просто CLI

**Глава 00 · Обзор и введение**

Этот гайд объясняет, как оформить репозиторий так, чтобы OpenCode понимал структуру проекта, опирался на реальные правила команды, читал спецификации рядом с кодом, использовал role-based subagents и не делал лишнего без продуманной политики разрешений.

Основа гайда: [официальная документация OpenCode](https://opencode.ai/docs/ru/) и репозиторий-пример [github.com/ivanshamaev/ai-agent-codex](https://github.com/ivanshamaev/ai-agent-codex).

---

## Что вы получите

### Не набор советов, а рабочую систему

В гайде разобраны не только команды запуска, но и структура репозитория, правила, skills, агенты, конфиг, разрешения и командные процессы.

- Как должен выглядеть OpenCode-проект
- Что хранить в `AGENTS.md`
- Как проектировать `opencode.json`
- Когда нужны `docs/specs`, агенты и skills
- Как выстроить воспроизводимую работу команды

---

## Дополнительные материалы

| Ресурс | Описание |
|--------|----------|
| [Видеообзор интерфейса OpenCode](https://www.youtube.com/watch?v=KSEfr8h-tH8) | TUI и десктоп, подключение провайдеров через API-ключи |
| [Расширенный туториал](https://www.youtube.com/watch?v=z7901BIReGs) | Установка, MCP, skills, rules, нейросети |
| [Claude Skills Guide](https://fkonovalov.github.io/claude-skills-guide-ru/) | Русскоязычное руководство по проектированию skills |

### Где искать готовые skills и MCP

- [cursor.directory](https://cursor.directory/) — подборка skills и MCP
- [MCP Market](https://mcpmarket.com/) — маркетплейс MCP серверов
- [skills.sh](https://skills.sh/) — онлайн-редактор с превью
- [SkillHub](https://skillhub.club) — сообщество с подборками skills
- [skillsmp](https://skillsmp.com) — маркетплейс кастомных skills
- [Skill Seekers](https://github.com/yusufkaraaslan/Skill_Seekers) — коллекция OpenCode skills
- [prompt-master](https://github.com/nidhinjs/prompt-master) — шаблоны для skills
- [claude-skills](https://github.com/alirezarezvani/claude-skills/) — Claude-навыки
- [pm-skills](https://github.com/phuryn/pm-skills) — skills для продуктовых задач
- [awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills) — консолидированный список

---

## Зачем вообще нужен отдельный гайд по настройке OpenCode-проекта

Почти любой AI coding tool можно установить за несколько минут. Но разница между «CLI запускается» и «агент стабильно помогает всей команде» огромная. Во втором случае нужен отдельный слой проектной настройки: что агент считает обязательными правилами, где он читает требования, как он понимает архитектуру репозитория, когда он вызывает специальные роли и какие действия он может выполнять автоматически.

Если этот слой не настроен, агент каждый раз начинает почти с нуля. Он вынужден угадывать, какие папки считаются canonical, где хранятся требования, что такое "правильный" способ внесения изменений и какие действия допустимы без лишних вопросов.

1. **`AGENTS.md`** — проектный контракт
2. **`opencode.json`** — control plane
3. **`.opencode/`** — слой расширения

---

## Что именно покрывает этот гайд

| Глава | О чём |
|-------|-------|
| **00 — Введение** | Рамка всего гайда, карта разделов, базовые принципы |
| **01 — Быстрый старт** | Установка, /connect, /init, первый AGENTS.md и opencode.json |
| **02 — Анатомия проекта** | Разбор реального репозитория-примера |
| **03 — Агенты и skills** | Subagents, роли, playbooks |
| **04 — Конфиг и разрешения** | opencode.json, instructions, permissions |
| **05 — Командные процессы** | Plan/build, specs-first работа, маршрутизация |
| **06 — MCP и интеграции** | Локальные/удаленные серверы, OAuth |
| **07 — Best Practices** | Модельная стратегия, cost-контроль, онбординг |
| **08 — Development Process** | Delivery cycles, quality gates, review |
| **09 — Step 1: Project Example** | Blueprint: AGENTS.md, stage-based delivery, prompts |
| **09 — Step 2: Project Example** | Структура /docs для online shop |

---

## Репозиторий-пример

Весь гайд опирается на реальный проект: [github.com/ivanshamaev/ai-agent-codex](https://github.com/ivanshamaev/ai-agent-codex)

```
ai-agent-codex/
├─ AGENTS.md
├─ opencode.json
├─ .env.example
├─ docker-compose.yml
├─ pyproject.toml
├─ pyrightconfig.json
├─ README.md
├─ apps/
│  ├─ api/
│  └─ web/
├─ dags/
├─ src/
├─ dbt/
├─ sql/
├─ docs/
│  └─ specs/
├─ data/
├─ logs/
├─ plugins/
└─ .opencode/
   ├─ agents/
   └─ skills/
```

---

## Полная структура целевого OpenCode-проекта

```
opencode-project/
├─ AGENTS.md
├─ opencode.json
├─ instructions/
│  ├─ defaults.md
│  └─ safety.md
├─ docs/
│  └─ specs/
├─ .opencode/
│  ├─ agents/
│  ├─ skills/
│  ├─ patterns/
│  └─ templates/
├─ mcp/
│  ├─ local/
│  └─ remote/
└─ README.md
```

### Компоненты OpenCode-уровня

| Компонент | Назначение | Комментарий |
|-----------|-----------|-------------|
| `AGENTS.md` | Проектный контракт | Структура репозитория, роли, роутинг задач, правила |
| `opencode.json` | Control plane | Инструкции, инструменты, MCP, лимиты, разрешения |
| `instructions/` | Базовые правила | Долгоживущие инструкции (defaults, security, style) |
| `.opencode/agents/` | Role-based subagents | Профили ролей (analyst, infra, architect) |
| `.opencode/skills/` | Playbooks | Повторяемые стратегии мышления и workflow |
| `.opencode/patterns/` | Контроль безопасности | whitelist/blacklist для инструментов |
| `.opencode/templates/` | Шаблоны ответов | RCA, планы миграций, спеки задач |
| `docs/specs/` | Durable спецификации | Технические и продуктовые контракты |
| `mcp/local/` | Локальные MCP | Скрипты рядом с проектом |
| `mcp/remote/` | Удалённые MCP | Конфигурации для внешних сервисов |

---

*Источники: официальная документация OpenCode на opencode.ai/docs/ru и репозиторий-пример github.com/ivanshamaev/ai-agent-codex*
