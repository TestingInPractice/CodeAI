Инструменты | OpenCode     [Перейти к содержимому](#_top)

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
-   [Настройка](#настройка)
-   [Встроенный](#встроенный)
    -   [bash](#bash)
    -   [edit](#edit)
    -   [write](#write)
    -   [read](#read)
    -   [grep](#grep)
    -   [glob](#glob)
    -   [lsp (экспериментальный)](#lsp-экспериментальный)
    -   [patch](#patch)
    -   [skill](#skill)
    -   [todowrite](#todowrite)
    -   [webfetch](#webfetch)
    -   [websearch](#websearch)
    -   [question](#question)
-   [Пользовательские инструменты](#пользовательские-инструменты)
-   [MCP-серверы](#mcp-серверы)
-   [Внутреннее устройство](#внутреннее-устройство)
    -   [Игнорировать шаблоны](#игнорировать-шаблоны)

## На этой странице

-   [Обзор](#_top)
-   [Настройка](#настройка)
-   [Встроенный](#встроенный)
    -   [bash](#bash)
    -   [edit](#edit)
    -   [write](#write)
    -   [read](#read)
    -   [grep](#grep)
    -   [glob](#glob)
    -   [lsp (экспериментальный)](#lsp-экспериментальный)
    -   [patch](#patch)
    -   [skill](#skill)
    -   [todowrite](#todowrite)
    -   [webfetch](#webfetch)
    -   [websearch](#websearch)
    -   [question](#question)
-   [Пользовательские инструменты](#пользовательские-инструменты)
-   [MCP-серверы](#mcp-серверы)
-   [Внутреннее устройство](#внутреннее-устройство)
    -   [Игнорировать шаблоны](#игнорировать-шаблоны)

# Инструменты

Управляйте инструментами, которые может использовать LLM.

Инструменты позволяют LLM выполнять действия в вашей кодовой базе. opencode поставляется с набором встроенных инструментов, но вы можете расширить его с помощью [пользовательских инструментов](/docs/custom-tools) или [MCP-серверов](/docs/mcp-servers).

По умолчанию все инструменты **включены** и не требуют разрешения для запуска. Вы можете контролировать поведение инструмента через [permissions](/docs/permissions).

---

## [Настройка](#настройка)

Используйте поле `permission` для управления поведением инструмента. Вы можете разрешить, запретить или потребовать одобрения для каждого инструмента.

opencode.json

```
{  "$schema": "https://opencode.ai/config.json",  "permission": {    "edit": "deny",    "bash": "ask",    "webfetch": "allow"  }}
```

Вы также можете использовать подстановочные знаки для одновременного управления несколькими инструментами. Например, чтобы потребовать одобрения всех инструментов с сервера MCP:

opencode.json

```
{  "$schema": "https://opencode.ai/config.json",  "permission": {    "mymcp_*": "ask"  }}
```

[Подробнее](/docs/permissions) о настройке разрешений.

---

## [Встроенный](#встроенный)

Вот все встроенные инструменты, доступные в opencode.

---

### [bash](#bash)

Выполняйте shell-команды в среде вашего проекта.

opencode.json

```
{  "$schema": "https://opencode.ai/config.json",  "permission": {    "bash": "allow"  }}
```

Этот инструмент позволяет LLM запускать команды терминала, такие как `npm install`, `git status` или любую другую shell-команду.

---

### [edit](#edit)

Измените существующие файлы, используя точную замену строк.

opencode.json

```
{  "$schema": "https://opencode.ai/config.json",  "permission": {    "edit": "allow"  }}
```

Этот инструмент выполняет точное редактирование файлов, заменяя точные совпадения текста. Это основной способ изменения кода в LLM.

---

### [write](#write)

Создавайте новые файлы или перезаписывайте существующие.

opencode.json

```
{  "$schema": "https://opencode.ai/config.json",  "permission": {    "edit": "allow"  }}
```

Используйте это, чтобы позволить LLM создавать новые файлы. Он перезапишет существующие файлы, если они уже существуют.

Заметка

Инструмент `write` контролируется разрешением `edit`, которое распространяется на все модификации файлов (`edit`, `write`, `patch`).

---

### [read](#read)

Прочитайте содержимое файла из вашей кодовой базы.

opencode.json

```
{  "$schema": "https://opencode.ai/config.json",  "permission": {    "read": "allow"  }}
```

Этот инструмент читает файлы и возвращает их содержимое. Он поддерживает чтение определенных диапазонов строк для больших файлов.

---

### [grep](#grep)

Поиск содержимого файла с помощью регулярных выражений.

opencode.json

```
{  "$schema": "https://opencode.ai/config.json",  "permission": {    "grep": "allow"  }}
```

Быстрый поиск контента по вашей кодовой базе. Поддерживает полный синтаксис регулярных выражений и фильтрацию шаблонов файлов.

---

### [glob](#glob)

Найдите файлы по шаблону.

opencode.json

```
{  "$schema": "https://opencode.ai/config.json",  "permission": {    "glob": "allow"  }}
```

Ищите файлы, используя шаблоны glob, например `**/*.js` или `src/**/*.ts`. Возвращает соответствующие пути к файлам, отсортированные по времени изменения.

---

### [lsp (экспериментальный)](#lsp-экспериментальный)

Взаимодействуйте с настроенными серверами LSP, чтобы получить функции анализа кода, такие как определения, ссылки, информация о наведении и иерархия вызовов.

Заметка

Этот инструмент доступен только при `OPENCODE_EXPERIMENTAL_LSP_TOOL=true` (или `OPENCODE_EXPERIMENTAL=true`).

opencode.json

```
{  "$schema": "https://opencode.ai/config.json",  "permission": {    "lsp": "allow"  }}
```

Поддерживаемые операции включают `goToDefinition`, `findReferences`, `hover`, `documentSymbol`, `workspaceSymbol`, `goToImplementation`, `prepareCallHierarchy`, `incomingCalls` и `outgoingCalls`.

Чтобы настроить серверы LSP, доступные для вашего проекта, см. [LSP Servers](/docs/lsp).

---

### [patch](#patch)

Применяйте патчи к файлам.

opencode.json

```
{  "$schema": "https://opencode.ai/config.json",  "permission": {    "edit": "allow"  }}
```

Этот инструмент применяет файлы исправлений к вашей кодовой базе. Полезно для применения различий и патчей из различных источников.

Заметка

Инструмент `patch` контролируется разрешением `edit`, которое распространяется на все модификации файлов (`edit`, `write`, `patch`).

---

### [skill](#skill)

Загрузите [skill](/docs/skills) (файл `SKILL.md`) и верните его содержимое в диалог.

opencode.json

```
{  "$schema": "https://opencode.ai/config.json",  "permission": {    "skill": "allow"  }}
```

---

### [todowrite](#todowrite)

Управляйте списками дел во время сеансов кодирования.

opencode.json

```
{  "$schema": "https://opencode.ai/config.json",  "permission": {    "todowrite": "allow"  }}
```

Создает и обновляет списки задач для отслеживания прогресса во время сложных операций. LLM использует это для организации многоэтапных задач.

Заметка

По умолчанию этот инструмент отключен для субагентов, но вы можете включить его вручную. [Подробнее](/docs/agents/#permissions)

---

### [webfetch](#webfetch)

Получить веб-контент.

opencode.json

```
{  "$schema": "https://opencode.ai/config.json",  "permission": {    "webfetch": "allow"  }}
```

Позволяет LLM получать и читать веб-страницы. Полезно для поиска документации или исследования онлайн-ресурсов.

---

### [websearch](#websearch)

Найдите информацию в Интернете.

Заметка

Этот инструмент доступен только при использовании поставщика opencode или когда для переменной среды `OPENCODE_ENABLE_EXA` установлено любое истинное значение (например, `true` или `1`).

Чтобы включить при запуске opencode:

Окно терминала

```
OPENCODE_ENABLE_EXA=1 opencode
```

opencode.json

```
{  "$schema": "https://opencode.ai/config.json",  "permission": {    "websearch": "allow"  }}
```

Выполняет поиск в Интернете с помощью Exa AI для поиска соответствующей информации в Интернете. Полезно для исследования тем, поиска текущих событий или сбора информации, выходящей за рамки данных обучения.

Ключ API не требуется — инструмент подключается напрямую к сервису MCP, размещенному на Exa AI, без аутентификации.

Совет

Используйте `websearch`, когда вам нужно найти информацию (обнаружение), и `webfetch`, когда вам нужно получить контент с определенного URL-адреса (извлечение).

---

### [question](#question)

Задавайте вопросы пользователю во время выполнения.

opencode.json

```
{  "$schema": "https://opencode.ai/config.json",  "permission": {    "question": "allow"  }}
```

Этот инструмент позволяет LLM задавать вопросы пользователю во время выполнения задачи. Это полезно для:

-   Сбор предпочтений или требований пользователей
-   Уточнение двусмысленных инструкций
-   Получение решений по вариантам реализации
-   Предлагая выбор, в каком направлении двигаться

Каждый вопрос включает заголовок, текст вопроса и список вариантов. Пользователи могут выбрать один из предложенных вариантов или ввести собственный ответ. Если вопросов несколько, пользователи могут перемещаться между ними, прежде чем отправлять все ответы.

---

## [Пользовательские инструменты](#пользовательские-инструменты)

Пользовательские инструменты позволяют вам определять собственные функции, которые может вызывать LLM. Они определены в вашем файле конфигурации и могут выполнять произвольный код.

[Подробнее](/docs/custom-tools) о создании собственных инструментов.

---

## [MCP-серверы](#mcp-серверы)

Серверы MCP (Model Context Protocol) позволяют интегрировать внешние инструменты и сервисы. Сюда входит доступ к базе данных, интеграция API и сторонние сервисы.

[Подробнее](/docs/mcp-servers) о настройке серверов MCP.

---

## [Внутреннее устройство](#внутреннее-устройство)

Внутренне такие инструменты, как `grep` и `glob`, используют [ripgrep](https://github.com/BurntSushi/ripgrep). По умолчанию ripgrep учитывает шаблоны `.gitignore`, что означает, что файлы и каталоги, перечисленные в вашем `.gitignore`, будут исключены из поиска и списков.

---

### [Игнорировать шаблоны](#игнорировать-шаблоны)

Чтобы включить файлы, которые обычно игнорируются, создайте файл `.ignore` в корне вашего проекта. Этот файл может явно разрешать определенные пути.

.ignore

```
!node_modules/!dist/!build/
```

Например, этот файл `.ignore` позволяет ripgrep выполнять поиск в каталогах `node_modules/`, `dist/` и `build/`, даже если они указаны в `.gitignore`.

[Редактировать страницу](https://github.com/anomalyco/opencode/edit/dev/packages/web/src/content/docs/ru/tools.mdx)[Found a bug? Open an issue](https://github.com/anomalyco/opencode/issues/new)[Join our Discord community](https://opencode.ai/discord) Выберите язык EnglishالعربيةBosanskiDanskDeutschEspañolFrançaisItaliano日本語한국어Norsk BokmålPolskiPortuguês (Brasil)РусскийไทยTürkçe简体中文繁體中文 

© [Anomaly](https://anoma.ly)

Последнее обновление: 30 мая 2026 г.
