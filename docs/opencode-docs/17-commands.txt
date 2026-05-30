Команды | OpenCode     [Перейти к содержимому](#_top)

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
-   [Создание файлов команд](#создание-файлов-команд)
-   [Настройка](#настройка)
    -   [JSON](#json)
    -   [Markdown](#markdown)
-   [Настройка промпта](#настройка-промпта)
    -   [Аргументы](#аргументы)
    -   [Вывод shell](#вывод-shell)
    -   [Ссылки на файлы](#ссылки-на-файлы)
-   [Параметры](#параметры)
    -   [Template](#template)
    -   [Описание](#описание)
    -   [Агент](#агент)
    -   [Subtask](#subtask)
    -   [Модель](#модель)
-   [Встроенные команды](#встроенные-команды)

## На этой странице

-   [Обзор](#_top)
-   [Создание файлов команд](#создание-файлов-команд)
-   [Настройка](#настройка)
    -   [JSON](#json)
    -   [Markdown](#markdown)
-   [Настройка промпта](#настройка-промпта)
    -   [Аргументы](#аргументы)
    -   [Вывод shell](#вывод-shell)
    -   [Ссылки на файлы](#ссылки-на-файлы)
-   [Параметры](#параметры)
    -   [Template](#template)
    -   [Описание](#описание)
    -   [Агент](#агент)
    -   [Subtask](#subtask)
    -   [Модель](#модель)
-   [Встроенные команды](#встроенные-команды)

# Команды

Создавайте собственные команды для повторяющихся задач.

Пользовательские команды позволяют указать подсказку, которую вы хотите запускать при выполнении этой команды в TUI.

```
/my-command
```

Пользовательские команды дополняют встроенные команды, такие как `/init`, `/undo`, `/redo`, `/share`, `/help`. [Подробнее](/docs/tui#commands).

---

## [Создание файлов команд](#создание-файлов-команд)

Создайте Markdown файлы в каталоге `commands/` для определения пользовательских команд.

Создайте `.opencode/commands/test.md`:

.opencode/commands/test.md

```
---description: Run tests with coverageagent: buildmodel: anthropic/claude-3-5-sonnet-20241022---
Run the full test suite with coverage report and show any failures.Focus on the failing tests and suggest fixes.
```

Фронтматтер (frontmatter) определяет свойства команды. Содержимое становится шаблоном.

Используйте команду, набрав `/`, а затем имя команды.

```
"/test"
```

---

## [Настройка](#настройка)

Вы можете добавлять собственные команды через конфигурацию opencode или создав файлы Markdown в каталоге `commands/`.

---

### [JSON](#json)

Используйте опцию `command` в вашем opencode [config](/docs/config):

opencode.jsonc

```
{  "$schema": "https://opencode.ai/config.json",  "command": {    // This becomes the name of the command    "test": {      // This is the prompt that will be sent to the LLM      "template": "Run the full test suite with coverage report and show any failures.\nFocus on the failing tests and suggest fixes.",      // This is shown as the description in the TUI      "description": "Run tests with coverage",      "agent": "build",      "model": "anthropic/claude-3-5-sonnet-20241022"    }  }}
```

Теперь вы можете запустить эту команду в TUI:

```
/test
```

---

### [Markdown](#markdown)

Вы также можете определять команды, используя Markdown файлы. Поместите их в:

-   Глобальный: `~/.config/opencode/commands/`
-   Для каждого проекта: `.opencode/commands/`

~/.config/opencode/commands/test.md

```
---description: Run tests with coverageagent: buildmodel: anthropic/claude-3-5-sonnet-20241022---
Run the full test suite with coverage report and show any failures.Focus on the failing tests and suggest fixes.
```

Имя Markdown файла становится именем команды. Например, `test.md` позволяет вам запустить:

```
/test
```

---

## [Настройка промпта](#настройка-промпта)

Подсказки для пользовательских команд поддерживают несколько специальных заполнителей и синтаксиса.

---

### [Аргументы](#аргументы)

Передавайте аргументы командам, используя заполнитель `$ARGUMENTS`.

.opencode/commands/component.md

```
---description: Create a new component---
Create a new React component named $ARGUMENTS with TypeScript support.Include proper typing and basic structure.
```

Запустите команду с аргументами:

```
/component Button
```

И `$ARGUMENTS` будет заменен на `Button`.

Вы также можете получить доступ к отдельным аргументам, используя позиционные параметры:

-   `$1` — первый аргумент
-   `$2` — Второй аргумент
-   `$3` — Третий аргумент
-   И так далее…

Например:

.opencode/commands/create-file.md

```
---description: Create a new file with content---
Create a file named $1 in the directory $2with the following content: $3
```

Запустите команду:

```
/create-file config.json src "{ \"key\": \"value\" }"
```

Это заменяет:

-   `$1` с `config.json`
-   `$2` с `src`
-   `$3` с `{ "key": "value" }`

---

### [Вывод shell](#вывод-shell)

Используйте *!`command`*, чтобы ввести вывод команды bash\](/docs/tui#bash-commands) в приглашение.

Например, чтобы создать пользовательскую команду, которая анализирует тестовое покрытие:

.opencode/commands/analyze-coverage.md

```
---description: Analyze test coverage---
Here are the current test results:!`npm test`
Based on these results, suggest improvements to increase coverage.
```

Или просмотреть последние изменения:

.opencode/commands/review-changes.md

```
---description: Review recent changes---
Recent git commits:!`git log --oneline -10`
Review these changes and suggest any improvements.
```

Команды выполняются в корневом каталоге вашего проекта, и их вывод становится частью приглашения.

---

### [Ссылки на файлы](#ссылки-на-файлы)

Включите файлы в свою команду, используя `@`, за которым следует имя файла.

.opencode/commands/review-component.md

```
---description: Review component---
Review the component in @src/components/Button.tsx.Check for performance issues and suggest improvements.
```

Содержимое файла автоматически включается в приглашение.

---

## [Параметры](#параметры)

Рассмотрим варианты конфигурации подробнее.

---

### [Template](#template)

Параметр `template` определяет приглашение, которое будет отправлено в LLM при выполнении команды.

opencode.json

```
{  "command": {    "test": {      "template": "Run the full test suite with coverage report and show any failures.\nFocus on the failing tests and suggest fixes."    }  }}
```

Это **обязательный** параметр конфигурации.

---

### [Описание](#описание)

Используйте опцию `description`, чтобы предоставить краткое описание того, что делает команда.

opencode.json

```
{  "command": {    "test": {      "description": "Run tests with coverage"    }  }}
```

Это отображается в виде описания в TUI при вводе команды.

---

### [Агент](#агент)

Используйте конфигурацию `agent`, чтобы дополнительно указать, какой [агент](/docs/agents) должен выполнить эту команду. Если это [subagent](/docs/agents/#subagents), команда по умолчанию инициирует вызов субагента. Чтобы отключить это поведение, установите для `subtask` значение `false`.

opencode.json

```
{  "command": {    "review": {      "agent": "plan"    }  }}
```

Это **необязательный** параметр конфигурации. Если не указано, по умолчанию используется текущий агент.

---

### [Subtask](#subtask)

Используйте логическое значение `subtask`, чтобы заставить команду инициировать вызов [subagent](/docs/agents/#subagents). Это полезно, если вы хотите, чтобы команда не загрязняла ваш основной контекст и **заставляла** агента действовать как субагент. даже если для `mode` установлено значение `primary` в конфигурации [agent](/docs/agents).

opencode.json

```
{  "command": {    "analyze": {      "subtask": true    }  }}
```

Это **необязательный** параметр конфигурации.

---

### [Модель](#модель)

Используйте конфигурацию `model`, чтобы переопределить модель по умолчанию для этой команды.

opencode.json

```
{  "command": {    "analyze": {      "model": "anthropic/claude-3-5-sonnet-20241022"    }  }}
```

Это **необязательный** параметр конфигурации.

---

## [Встроенные команды](#встроенные-команды)

opencode включает несколько встроенных команд, таких как `/init`, `/undo`, `/redo`, `/share`, `/help`; [подробнее](/docs/tui#commands).

Заметка

Пользовательские команды могут переопределять встроенные команды.

Если вы определите пользовательскую команду с тем же именем, она переопределит встроенную команду.

[Редактировать страницу](https://github.com/anomalyco/opencode/edit/dev/packages/web/src/content/docs/ru/commands.mdx)[Found a bug? Open an issue](https://github.com/anomalyco/opencode/issues/new)[Join our Discord community](https://opencode.ai/discord) Выберите язык EnglishالعربيةBosanskiDanskDeutschEspañolFrançaisItaliano日本語한국어Norsk BokmålPolskiPortuguês (Brasil)РусскийไทยTürkçe简体中文繁體中文 

© [Anomaly](https://anoma.ly)

Последнее обновление: 30 мая 2026 г.
