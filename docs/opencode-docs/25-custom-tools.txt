Пользовательские инструменты | OpenCode     [Перейти к содержимому](#_top)

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
-   [Создание инструмента](#создание-инструмента)
    -   [Расположение](#расположение)
    -   [Структура](#структура)
    -   [Аргументы](#аргументы)
    -   [Контекст](#контекст)
-   [Примеры](#примеры)
    -   [Инструмент на Python](#инструмент-на-python)

## На этой странице

-   [Обзор](#_top)
-   [Создание инструмента](#создание-инструмента)
    -   [Расположение](#расположение)
    -   [Структура](#структура)
    -   [Аргументы](#аргументы)
    -   [Контекст](#контекст)
-   [Примеры](#примеры)
    -   [Инструмент на Python](#инструмент-на-python)

# Пользовательские инструменты

Создавайте инструменты, которые LLM может вызывать в opencode.

Пользовательские инструменты — это создаваемые вами функции, которые LLM может вызывать во время разговоров. Они работают вместе со [встроенными инструментами](/docs/tools) opencode, такими как `read`, `write` и `bash`.

---

## [Создание инструмента](#создание-инструмента)

Инструменты определяются как файлы **TypeScript** или **JavaScript**. Однако определение инструмента может вызывать сценарии, написанные на **любом языке** — TypeScript или JavaScript используются только для самого определения инструмента.

---

### [Расположение](#расположение)

Их можно определить:

-   Локально, поместив их в каталог `.opencode/tools/` вашего проекта.
-   Или глобально, поместив их в `~/.config/opencode/tools/`.

---

### [Структура](#структура)

Самый простой способ создания инструментов — использовать помощник `tool()`, который обеспечивает безопасность типов и проверку.

.opencode/tools/database.ts

```
import { tool } from "@opencode-ai/plugin"
export default tool({  description: "Query the project database",  args: {    query: tool.schema.string().describe("SQL query to execute"),  },  async execute(args) {    // Your database logic here    return `Executed query: ${args.query}`  },})
```

**имя файла** становится **именем инструмента**. Вышеупомянутое создает инструмент `database`.

---

#### [Несколько инструментов в файле](#несколько-инструментов-в-файле)

Вы также можете экспортировать несколько инструментов из одного файла. Каждый экспорт становится **отдельным инструментом** с именем **`<filename>_<exportname>`**:

.opencode/tools/math.ts

```
import { tool } from "@opencode-ai/plugin"
export const add = tool({  description: "Add two numbers",  args: {    a: tool.schema.number().describe("First number"),    b: tool.schema.number().describe("Second number"),  },  async execute(args) {    return args.a + args.b  },})
export const multiply = tool({  description: "Multiply two numbers",  args: {    a: tool.schema.number().describe("First number"),    b: tool.schema.number().describe("Second number"),  },  async execute(args) {    return args.a * args.b  },})
```

При этом создаются два инструмента: `math_add` и `math_multiply`.

---

### [Аргументы](#аргументы)

Вы можете использовать `tool.schema`, то есть просто [Zod](https://zod.dev), для определения типов аргументов.

```
args: {  query: tool.schema.string().describe("SQL query to execute")}
```

Вы также можете импортировать [Zod](https://zod.dev) напрямую и вернуть простой объект:

```
import { z } from "zod"
export default {  description: "Tool description",  args: {    param: z.string().describe("Parameter description"),  },  async execute(args, context) {    // Tool implementation    return "result"  },}
```

---

### [Контекст](#контекст)

Инструменты получают контекст текущего сеанса:

.opencode/tools/project.ts

```
import { tool } from "@opencode-ai/plugin"
export default tool({  description: "Get project information",  args: {},  async execute(args, context) {    // Access context information    const { agent, sessionID, messageID, directory, worktree } = context    return `Agent: ${agent}, Session: ${sessionID}, Message: ${messageID}, Directory: ${directory}, Worktree: ${worktree}`  },})
```

Используйте `context.directory` для рабочего каталога сеанса. Используйте `context.worktree` для корня рабочего дерева git.

---

## [Примеры](#примеры)

### [Инструмент на Python](#инструмент-на-python)

Вы можете писать свои инструменты на любом языке, который захотите. Вот пример сложения двух чисел с использованием Python.

Сначала создайте инструмент как скрипт Python:

.opencode/tools/add.py

```
import sys
a = int(sys.argv[1])b = int(sys.argv[2])print(a + b)
```

Затем создайте определение инструмента, которое его вызывает:

.opencode/tools/python-add.ts

```
import { tool } from "@opencode-ai/plugin"import path from "path"
export default tool({  description: "Add two numbers using Python",  args: {    a: tool.schema.number().describe("First number"),    b: tool.schema.number().describe("Second number"),  },  async execute(args, context) {    const script = path.join(context.worktree, ".opencode/tools/add.py")    const result = await Bun.$`python3 ${script} ${args.a} ${args.b}`.text()    return result.trim()  },})
```

Здесь мы используем утилиту [`Bun.$`](https://bun.com/docs/runtime/shell) для запуска скрипта Python.

[Редактировать страницу](https://github.com/anomalyco/opencode/edit/dev/packages/web/src/content/docs/ru/custom-tools.mdx)[Found a bug? Open an issue](https://github.com/anomalyco/opencode/issues/new)[Join our Discord community](https://opencode.ai/discord) Выберите язык EnglishالعربيةBosanskiDanskDeutschEspañolFrançaisItaliano日本語한국어Norsk BokmålPolskiPortuguês (Brasil)РусскийไทยTürkçe简体中文繁體中文 

© [Anomaly](https://anoma.ly)

Последнее обновление: 30 мая 2026 г.
