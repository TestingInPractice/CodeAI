Правила | OpenCode     [Перейти к содержимому](#_top)

  [![](/docs/_astro/logo-dark.DOStV66V.svg) ![](/docs/_astro/logo-light.B0yzR0O5.svg) OpenCode](/docs/ru)

[app.header.home](/)[app.header.docs](/docs/)

[](https://github.com/anomalyco/opencode)[](https://opencode.ai/discord)

Поиск CtrlK

Отменить

-   [Введение](/docs/ru/)
-   [Конфигурация](/docs/ru/config/)
-   [Провайдеры](/docs/ru/providers/)
-   [Сеть](/docs/ru/network/)
-   [Корпоративное использование](/docs/ru/enterprise/)
-   [Поиск неисправностей](/docs/ru/troubleshooting/)
-   [Windows](/docs/ru/windows-wsl)
-   Использование
    
    -   [Go](/docs/ru/go/)
    -   [TUI](/docs/ru/tui/)
    -   [CLI](/docs/ru/cli/)
    -   [Интернет](/docs/ru/web/)
    -   [IDE](/docs/ru/ide/)
    -   [Zen](/docs/ru/zen/)
    -   [Делиться](/docs/ru/share/)
    -   [GitHub](/docs/ru/github/)
    -   [GitLab](/docs/ru/gitlab/)
    
-   Настройка
    
    -   [Инструменты](/docs/ru/tools/)
    -   [Правила](/docs/ru/rules/)
    -   [Агенты](/docs/ru/agents/)
    -   [Модели](/docs/ru/models/)
    -   [Темы](/docs/ru/themes/)
    -   [Сочетания клавиш](/docs/ru/keybinds/)
    -   [Команды](/docs/ru/commands/)
    -   [Форматтеры](/docs/ru/formatters/)
    -   [Разрешения](/docs/ru/permissions/)
    -   [Policies](/docs/ru/policies/)
    -   [LSP-серверы](/docs/ru/lsp/)
    -   [MCP-серверы](/docs/ru/mcp-servers/)
    -   [Поддержка ACP](/docs/ru/acp/)
    -   [Навыки агента](/docs/ru/skills/)
    -   [Пользовательские инструменты](/docs/ru/custom-tools/)
    
-   Разработка
    
    -   [SDK](/docs/ru/sdk/)
    -   [Сервер](/docs/ru/server/)
    -   [Плагины](/docs/ru/plugins/)
    -   [Экосистема](/docs/ru/ecosystem/)
    

[GitHub](https://github.com/anomalyco/opencode)[Discord](https://opencode.ai/discord)

Выберите тему ТёмнаяСветлаяАвто   Выберите язык EnglishالعربيةBosanskiDanskDeutschEspañolFrançaisItaliano日本語한국어Norsk BokmålPolskiPortuguês (Brasil)РусскийไทยTürkçe简体中文繁體中文

На этой странице

-   [Обзор](#_top)
-   [Инициализировать](#инициализировать)
-   [Пример](#пример)
-   [Типы](#типы)
    -   [Проект](#проект)
    -   [Глобальный](#глобальный)
    -   [Совместимость кода Клода](#совместимость-кода-клода)
-   [Приоритет](#приоритет)
-   [Пользовательские инструкции](#пользовательские-инструкции)
-   [Ссылки на внешние файлы](#ссылки-на-внешние-файлы)
    -   [Использование opencode.json](#использование-opencodejson)
    -   [Ручные инструкции в AGENTS.md](#ручные-инструкции-в-agentsmd)

## На этой странице

-   [Обзор](#_top)
-   [Инициализировать](#инициализировать)
-   [Пример](#пример)
-   [Типы](#типы)
    -   [Проект](#проект)
    -   [Глобальный](#глобальный)
    -   [Совместимость кода Клода](#совместимость-кода-клода)
-   [Приоритет](#приоритет)
-   [Пользовательские инструкции](#пользовательские-инструкции)
-   [Ссылки на внешние файлы](#ссылки-на-внешние-файлы)
    -   [Использование opencode.json](#использование-opencodejson)
    -   [Ручные инструкции в AGENTS.md](#ручные-инструкции-в-agentsmd)

# Правила

Установите пользовательские инструкции для opencode.

Вы можете предоставить собственные инструкции для opencode, создав файл `AGENTS.md`. Это похоже на правила Cursor. Он содержит инструкции, которые будут включены в контекст LLM для настройки его поведения для вашего конкретного проекта.

---

## [Инициализировать](#инициализировать)

Чтобы создать новый файл `AGENTS.md`, вы можете запустить команду `/init` в opencode.

Совет

Вам следует закоммитить файл `AGENTS.md` вашего проекта в Git.

Это позволит отсканировать ваш проект и все его содержимое, чтобы понять, о чем этот проект, и сгенерировать с его помощью файл `AGENTS.md`. Это помогает opencode лучше ориентироваться в проекте.

Если у вас есть существующий файл `AGENTS.md`, мы попытаемся добавить его.

---

## [Пример](#пример)

Вы также можете просто создать этот файл вручную. Вот пример того, что вы можете поместить в файл `AGENTS.md`.

AGENTS.md

```
# SST v3 Monorepo Project
This is an SST v3 monorepo with TypeScript. The project uses bun workspaces for package management.
## Project Structure
- `packages/` - Contains all workspace packages (functions, core, web, etc.)- `infra/` - Infrastructure definitions split by service (storage.ts, api.ts, web.ts)- `sst.config.ts` - Main SST configuration with dynamic imports
## Code Standards
- Use TypeScript with strict mode enabled- Shared code goes in `packages/core/` with proper exports configuration- Functions go in `packages/functions/`- Infrastructure should be split into logical files in `infra/`
## Monorepo Conventions
- Import shared modules using workspace names: `@my-app/core/example`
```

Мы добавляем сюда инструкции для конкретного проекта, и они будут доступны всей вашей команде.

---

## [Типы](#типы)

opencode также поддерживает чтение файла `AGENTS.md` из нескольких мест. И это служит разным целям.

### [Проект](#проект)

Поместите `AGENTS.md` в корень вашего проекта для правил, специфичных для проекта. Они применяются только тогда, когда вы работаете в этом каталоге или его подкаталогах.

### [Глобальный](#глобальный)

Вы также можете иметь глобальные правила в файле `~/.config/opencode/AGENTS.md`. Это применяется ко всем сеансам opencode.

Поскольку это не коммитится в Git и не передается вашей команде, мы рекомендуем использовать его для указания любых личных правил, которым должен следовать LLM.

### [Совместимость кода Клода](#совместимость-кода-клода)

Для пользователей, переходящих с Claude Code, opencode поддерживает файловые соглашения Claude Code в качестве резерва:

-   **Правила проекта**: `CLAUDE.md` в каталоге вашего проекта (используется, если `AGENTS.md` не существует).
-   **Глобальные правила**: `~/.claude/CLAUDE.md` (используется, если `~/.config/opencode/AGENTS.md` не существует).
-   **Навыки**: `~/.claude/skills/` — подробности см. в [Навыки агента](/docs/skills/).

Чтобы отключить совместимость Claude Code, установите одну из этих переменных среды:

Окно терминала

```
export OPENCODE_DISABLE_CLAUDE_CODE=1        # Disable all .claude supportexport OPENCODE_DISABLE_CLAUDE_CODE_PROMPT=1 # Disable only ~/.claude/CLAUDE.mdexport OPENCODE_DISABLE_CLAUDE_CODE_SKILLS=1 # Disable only .claude/skills
```

---

## [Приоритет](#приоритет)

Когда opencode запускается, он ищет файлы правил в следующем порядке:

1.  **Локальные файлы** путем перехода вверх из текущего каталога (`AGENTS.md`, `CLAUDE.md`)
2.  **Глобальный файл** в `~/.config/opencode/AGENTS.md`.
3.  **Файл кода Клауда** по адресу `~/.claude/CLAUDE.md` (если не отключено)

Первый совпадающий файл побеждает в каждой категории. Например, если у вас есть и `AGENTS.md`, и `CLAUDE.md`, используется только `AGENTS.md`. Аналогично, `~/.config/opencode/AGENTS.md` имеет приоритет над `~/.claude/CLAUDE.md`.

---

## [Пользовательские инструкции](#пользовательские-инструкции)

Вы можете указать собственные файлы инструкций в `opencode.json` или в глобальном `~/.config/opencode/opencode.json`. Это позволит вам и вашей команде повторно использовать существующие правила вместо того, чтобы дублировать их на AGENTS.md.

Пример:

opencode.json

```
{  "$schema": "https://opencode.ai/config.json",  "instructions": ["CONTRIBUTING.md", "docs/guidelines.md", ".cursor/rules/*.md"]}
```

Вы также можете использовать удаленные URL-адреса для загрузки инструкций из Интернета.

opencode.json

```
{  "$schema": "https://opencode.ai/config.json",  "instructions": ["https://raw.githubusercontent.com/my-org/shared-rules/main/style.md"]}
```

Удаленные инструкции извлекаются с таймаутом в 5 секунд.

Все файлы инструкций объединяются с вашими файлами `AGENTS.md`.

---

## [Ссылки на внешние файлы](#ссылки-на-внешние-файлы)

Хотя opencode не анализирует автоматически ссылки на файлы в `AGENTS.md`, аналогичной функциональности можно добиться двумя способами:

### [Использование opencode.json](#использование-opencodejson)

Рекомендуемый подход — использовать поле `instructions` в `opencode.json`:

opencode.json

```
{  "$schema": "https://opencode.ai/config.json",  "instructions": ["docs/development-standards.md", "test/testing-guidelines.md", "packages/*/AGENTS.md"]}
```

### [Ручные инструкции в AGENTS.md](#ручные-инструкции-в-agentsmd)

Вы можете научить opencode читать внешние файлы, предоставив явные инструкции в файле `AGENTS.md`. Вот практический пример:

AGENTS.md

```
# TypeScript Project Rules
## External File Loading
CRITICAL: When you encounter a file reference (e.g., @rules/general.md), use your Read tool to load it on a need-to-know basis. They're relevant to the SPECIFIC task at hand.
Instructions:
- Do NOT preemptively load all references - use lazy loading based on actual need- When loaded, treat content as mandatory instructions that override defaults- Follow references recursively when needed
## Development Guidelines
For TypeScript code style and best practices: @docs/typescript-guidelines.mdFor React component architecture and hooks patterns: @docs/react-patterns.mdFor REST API design and error handling: @docs/api-standards.mdFor testing strategies and coverage requirements: @test/testing-guidelines.md
## General Guidelines
Read the following file immediately as it's relevant to all workflows: @rules/general-guidelines.md.
```

Такой подход позволяет:

-   Создавайте модульные файлы правил многократного использования.
-   Делитесь правилами между проектами с помощью символических ссылок или подмодулей git.
-   Сохраняйте AGENTS.md кратким, ссылаясь на подробные инструкции.
-   Убедитесь, что opencode загружает файлы только тогда, когда это необходимо для конкретной задачи.

Совет

Для монорепозиториев или проектов с общими стандартами использование `opencode.json` с шаблонами glob (например, `packages/*/AGENTS.md`) более удобно в обслуживании, чем инструкции вручную.

[Редактировать страницу](https://github.com/anomalyco/opencode/edit/dev/packages/web/src/content/docs/ru/rules.mdx)[Found a bug? Open an issue](https://github.com/anomalyco/opencode/issues/new)[Join our Discord community](https://opencode.ai/discord) Выберите язык EnglishالعربيةBosanskiDanskDeutschEspañolFrançaisItaliano日本語한국어Norsk BokmålPolskiPortuguês (Brasil)РусскийไทยTürkçe简体中文繁體中文 

© [Anomaly](https://anoma.ly)

Последнее обновление: 30 мая 2026 г.
