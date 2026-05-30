Навыки агента | OpenCode     [Перейти к содержимому](#_top)

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
-   [Разместить файлы](#разместить-файлы)
-   [Понимание обнаружения](#понимание-обнаружения)
-   [Напишите заголовок](#напишите-заголовок)
-   [Проверка имен](#проверка-имен)
-   [Соблюдайте правила длины](#соблюдайте-правила-длины)
-   [Используйте пример](#используйте-пример)
-   [Распознавание описания инструмента](#распознавание-описания-инструмента)
-   [Настройка разрешений](#настройка-разрешений)
-   [Переопределить для каждого агента](#переопределить-для-каждого-агента)
-   [Отключить инструмент навыков](#отключить-инструмент-навыков)
-   [Устранение неполадок с загрузкой](#устранение-неполадок-с-загрузкой)

## На этой странице

-   [Обзор](#_top)
-   [Разместить файлы](#разместить-файлы)
-   [Понимание обнаружения](#понимание-обнаружения)
-   [Напишите заголовок](#напишите-заголовок)
-   [Проверка имен](#проверка-имен)
-   [Соблюдайте правила длины](#соблюдайте-правила-длины)
-   [Используйте пример](#используйте-пример)
-   [Распознавание описания инструмента](#распознавание-описания-инструмента)
-   [Настройка разрешений](#настройка-разрешений)
-   [Переопределить для каждого агента](#переопределить-для-каждого-агента)
-   [Отключить инструмент навыков](#отключить-инструмент-навыков)
-   [Устранение неполадок с загрузкой](#устранение-неполадок-с-загрузкой)

# Навыки агента

Определите повторно используемое поведение с помощью определений SKILL.md

Навыки агента позволяют opencode обнаруживать многократно используемые инструкции из вашего репозитория или домашнего каталога. Навыки загружаются по требованию с помощью встроенного инструмента `skill`: агенты видят доступные навыки и при необходимости могут загрузить весь контент.

---

## [Разместить файлы](#разместить-файлы)

Создайте одну папку для каждого имени навыка и поместите в нее `SKILL.md`. opencode выполняет поиск в следующих местах:

-   Конфигурация проекта: `.opencode/skills/<name>/SKILL.md`
-   Глобальная конфигурация: `~/.config/opencode/skills/<name>/SKILL.md`.
-   Совместимость с Project Claude: `.claude/skills/<name>/SKILL.md`
-   Глобальная совместимость с Claude: `~/.claude/skills/<name>/SKILL.md`
-   Совместимость с агентом проекта: `.agents/skills/<name>/SKILL.md`
-   Совместимость с глобальным агентом: `~/.agents/skills/<name>/SKILL.md`

---

## [Понимание обнаружения](#понимание-обнаружения)

Для локальных путей проекта opencode переходит из вашего текущего рабочего каталога, пока не достигнет рабочего дерева git. Он загружает все соответствующие `skills/*/SKILL.md` в `.opencode/` и все соответствующие `.claude/skills/*/SKILL.md` или `.agents/skills/*/SKILL.md` по пути.

Глобальные определения также загружаются из `~/.config/opencode/skills/*/SKILL.md`, `~/.claude/skills/*/SKILL.md` и `~/.agents/skills/*/SKILL.md`.

---

## [Напишите заголовок](#напишите-заголовок)

Каждый `SKILL.md` должен начинаться с заголовка YAML. Распознаются только эти поля:

-   `name` (required)
-   `description` (required)
-   `license` (необязательно)
-   `compatibility` (необязательно)
-   `metadata` (необязательно, преобразование строк в строки)

Неизвестные поля заголовка игнорируются.

---

## [Проверка имен](#проверка-имен)

`name` должен:

-   Длина от 1 до 64 символов.
-   Используйте строчные буквы и цифры с одинарным дефисом.
-   Не начинаться и не заканчиваться на `-`.
-   Не содержать последовательных `--`
-   Сопоставьте имя каталога, содержащее `SKILL.md`.

Эквивалентное регулярное выражение:

```
^[a-z0-9]+(-[a-z0-9]+)*$
```

---

## [Соблюдайте правила длины](#соблюдайте-правила-длины)

`description` должно содержать от 1 до 1024 символов. Держите его достаточно конкретным, чтобы агент мог сделать правильный выбор.

---

## [Используйте пример](#используйте-пример)

Создайте `.opencode/skills/git-release/SKILL.md` следующим образом:

```
---name: git-releasedescription: Create consistent releases and changelogslicense: MITcompatibility: opencodemetadata:  audience: maintainers  workflow: github---
## What I do
- Draft release notes from merged PRs- Propose a version bump- Provide a copy-pasteable `gh release create` command
## When to use me
Use this when you are preparing a tagged release.Ask clarifying questions if the target versioning scheme is unclear.
```

---

## [Распознавание описания инструмента](#распознавание-описания-инструмента)

opencode перечисляет доступные навыки в описании инструмента `skill`. Каждая запись включает название и описание навыка:

```
<available_skills>  <skill>    <name>git-release</name>    <description>Create consistent releases and changelogs</description>  </skill></available_skills>
```

Агент загружает навык, вызывая инструмент:

```
skill({ name: "git-release" })
```

---

## [Настройка разрешений](#настройка-разрешений)

Контролируйте, к каким навыкам агенты могут получить доступ, используя разрешения на основе шаблонов в `opencode.json`:

```
{  "permission": {    "skill": {      "*": "allow",      "pr-review": "allow",      "internal-*": "deny",      "experimental-*": "ask"    }  }}
```

Разрешение

Поведение

`allow`

Skill loads immediately

`deny`

Skill hidden from agent, access rejected

`ask`

User prompted for approval before loading

Шаблоны поддерживают подстановочные знаки: `internal-*` соответствует `internal-docs`, `internal-tools` и т. д.

---

## [Переопределить для каждого агента](#переопределить-для-каждого-агента)

Предоставьте конкретным агентам разрешения, отличные от глобальных настроек по умолчанию.

**Для пользовательских агентов** (в заголовке агента):

```
---permission:  skill:    "documents-*": "allow"---
```

**Для встроенных агентов** (в формате `opencode.json`):

```
{  "agent": {    "plan": {      "permission": {        "skill": {          "internal-*": "allow"        }      }    }  }}
```

---

## [Отключить инструмент навыков](#отключить-инструмент-навыков)

Полностью отключить навыки для агентов, которым не следует их использовать:

**Для индивидуальных агентов**:

```
---tools:  skill: false---
```

**Для встроенных агентов**:

```
{  "agent": {    "plan": {      "tools": {        "skill": false      }    }  }}
```

Если этот параметр отключен, раздел `<available_skills>` полностью опускается.

---

## [Устранение неполадок с загрузкой](#устранение-неполадок-с-загрузкой)

Если навык не отображается:

1.  Убедитесь, что `SKILL.md` написано заглавными буквами.
2.  Убедитесь, что заголовок включает `name` и `description`.
3.  Убедитесь, что названия навыков уникальны во всех локациях.
4.  Проверьте разрешения — навыки с `deny` скрыты от агентов.

[Редактировать страницу](https://github.com/anomalyco/opencode/edit/dev/packages/web/src/content/docs/ru/skills.mdx)[Found a bug? Open an issue](https://github.com/anomalyco/opencode/issues/new)[Join our Discord community](https://opencode.ai/discord) Выберите язык EnglishالعربيةBosanskiDanskDeutschEspañolFrançaisItaliano日本語한국어Norsk BokmålPolskiPortuguês (Brasil)РусскийไทยTürkçe简体中文繁體中文 

© [Anomaly](https://anoma.ly)

Последнее обновление: 30 мая 2026 г.
