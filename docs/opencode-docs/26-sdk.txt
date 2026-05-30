SDK | OpenCode     [Перейти к содержимому](#_top)

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
-   [Установить](#установить)
-   [Создать клиента](#создать-клиента)
-   [Конфигурация](#конфигурация)
-   [Только клиент](#только-клиент)
-   [Типы](#типы)
-   [Ошибки](#ошибки)
-   [Структурированный вывод](#структурированный-вывод)
    -   [Основное использование](#основное-использование)
    -   [Типы форматов вывода](#типы-форматов-вывода)
    -   [Формат схемы JSON](#формат-схемы-json)
    -   [Обработка ошибок](#обработка-ошибок)
    -   [Лучшие практики](#лучшие-практики)
-   [API](#api)
    -   [Глобальный](#глобальный)
    -   [Приложение](#приложение)
    -   [Проект](#проект)
    -   [Путь](#путь)
    -   [Конфигурация](#конфигурация-1)
    -   [Сессии](#сессии)
    -   [Файлы](#файлы)
    -   [TUI](#tui)
    -   [Аутентификация](#аутентификация)
    -   [События](#события)

## На этой странице

-   [Обзор](#_top)
-   [Установить](#установить)
-   [Создать клиента](#создать-клиента)
-   [Конфигурация](#конфигурация)
-   [Только клиент](#только-клиент)
-   [Типы](#типы)
-   [Ошибки](#ошибки)
-   [Структурированный вывод](#структурированный-вывод)
    -   [Основное использование](#основное-использование)
    -   [Типы форматов вывода](#типы-форматов-вывода)
    -   [Формат схемы JSON](#формат-схемы-json)
    -   [Обработка ошибок](#обработка-ошибок)
    -   [Лучшие практики](#лучшие-практики)
-   [API](#api)
    -   [Глобальный](#глобальный)
    -   [Приложение](#приложение)
    -   [Проект](#проект)
    -   [Путь](#путь)
    -   [Конфигурация](#конфигурация-1)
    -   [Сессии](#сессии)
    -   [Файлы](#файлы)
    -   [TUI](#tui)
    -   [Аутентификация](#аутентификация)
    -   [События](#события)

# SDK

Типобезопасный JS-клиент для сервера opencode.

SDK JS/TS с открытым кодом предоставляет типобезопасный клиент для взаимодействия с сервером. Используйте его для создания интеграции и программного управления открытым кодом.

[Узнайте больше](/docs/server) о том, как работает сервер. Примеры можно найти в [projects](/docs/ecosystem#projects), созданном сообществом.

---

## [Установить](#установить)

Установите SDK из npm:

Окно терминала

```
npm install @opencode-ai/sdk
```

---

## [Создать клиента](#создать-клиента)

Создайте экземпляр opencode:

```
import { createOpencode } from "@opencode-ai/sdk"
const { client } = await createOpencode()
```

Это запускает и сервер, и клиент.

#### [Параметры](#параметры)

Вариант

Тип

Описание

По умолчанию

`hostname`

`string`

Server hostname

`127.0.0.1`

`port`

`number`

Server port

`4096`

`signal`

`AbortSignal`

Abort signal for cancellation

`undefined`

`timeout`

`number`

Timeout in ms for server start

`5000`

`config`

`Config`

Configuration object

`{}`

---

## [Конфигурация](#конфигурация)

Вы можете передать объект конфигурации для настройки поведения. Экземпляр по-прежнему получает ваш `opencode.json`, но вы можете переопределить или добавить встроенную конфигурацию:

```
import { createOpencode } from "@opencode-ai/sdk"
const opencode = await createOpencode({  hostname: "127.0.0.1",  port: 4096,  config: {    model: "anthropic/claude-3-5-sonnet-20241022",  },})
console.log(`Server running at ${opencode.server.url}`)
opencode.server.close()
```

## [Только клиент](#только-клиент)

Если у вас уже есть работающий экземпляр opencode, вы можете создать экземпляр клиента для подключения к нему:

```
import { createOpencodeClient } from "@opencode-ai/sdk"
const client = createOpencodeClient({  baseUrl: "http://localhost:4096",})
```

#### [Параметры](#параметры-1)

Вариант

Тип

Описание

По умолчанию

`baseUrl`

`string`

URL of the server

`http://localhost:4096`

`fetch`

`function`

Custom fetch implementation

`globalThis.fetch`

`parseAs`

`string`

Response parsing method

`auto`

`responseStyle`

`string`

Return style: `data` or `fields`

`fields`

`throwOnError`

`boolean`

Throw errors instead of return

`false`

---

## [Типы](#типы)

SDK включает определения TypeScript для всех типов API. Импортируйте их напрямую:

```
import type { Session, Message, Part } from "@opencode-ai/sdk"
```

Все типы генерируются на основе спецификации OpenAPI сервера и доступны в файле [types](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts).

---

## [Ошибки](#ошибки)

SDK может выдавать ошибки, которые вы можете отловить и обработать:

```
try {  await client.session.get({ path: { id: "invalid-id" } })} catch (error) {  console.error("Failed to get session:", (error as Error).message)}
```

---

## [Структурированный вывод](#структурированный-вывод)

Вы можете запросить структурированный вывод JSON от модели, указав `format` со схемой JSON. Модель будет использовать инструмент `StructuredOutput` для возврата проверенного JSON, соответствующего вашей схеме.

### [Основное использование](#основное-использование)

```
const result = await client.session.prompt({  path: { id: sessionId },  body: {    parts: [{ type: "text", text: "Research Anthropic and provide company info" }],    format: {      type: "json_schema",      schema: {        type: "object",        properties: {          company: { type: "string", description: "Company name" },          founded: { type: "number", description: "Year founded" },          products: {            type: "array",            items: { type: "string" },            description: "Main products",          },        },        required: ["company", "founded"],      },    },  },})
// Access the structured outputconsole.log(result.data.info.structured_output)// { company: "Anthropic", founded: 2021, products: ["Claude", "Claude API"] }
```

### [Типы форматов вывода](#типы-форматов-вывода)

Тип

Описание

`text`

По умолчанию. Стандартный текстовый ответ (без структурированного вывода)

`json_schema`

Возвращает проверенный JSON, соответствующий предоставленной схеме

### [Формат схемы JSON](#формат-схемы-json)

При использовании `type: 'json_schema'`, укажите:

Поле

Тип

Описание

`type`

`'json_schema'`

Обязательно. Указывает режим схемы JSON

`schema`

`object`

Обязательно. Объект JSON Schema, определяющий структуру вывода

`retryCount`

`number`

Необязательно. Количество повторных попыток проверки (по умолчанию: 2)

### [Обработка ошибок](#обработка-ошибок)

Если модель не может выдать действительный структурированный вывод после всех повторных попыток, ответ будет включать `StructuredOutputError`:

```
if (result.data.info.error?.name === "StructuredOutputError") {  console.error("Failed to produce structured output:", result.data.info.error.message)  console.error("Attempts:", result.data.info.error.retries)}
```

### [Лучшие практики](#лучшие-практики)

1.  **Предоставляйте четкие описания** в свойствах вашей схемы, чтобы помочь модели понять, какие данные извлекать
2.  **Используйте `required`**, чтобы указать, какие поля должны присутствовать
3.  **Делайте схемы сфокусированными** — сложные вложенные схемы могут быть труднее для правильного заполнения моделью
4.  **Устанавливайте соответствующий `retryCount`** — увеличивайте для сложных схем, уменьшайте для простых

---

## [API](#api)

SDK предоставляет все серверные API через типобезопасный клиент.

---

### [Глобальный](#глобальный)

Метод

Описание

Ответ

`global.health()`

Check server health and version

`{ healthy: true, version: string }`

---

#### [Примеры](#примеры)

```
const health = await client.global.health()console.log(health.data.version)
```

---

### [Приложение](#приложение)

Метод

Описание

Ответ

`app.log()`

Write a log entry

`boolean`

`app.agents()`

List all available agents

[`Agent[]`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)

---

#### [Примеры](#примеры-1)

```
// Write a log entryawait client.app.log({  body: {    service: "my-app",    level: "info",    message: "Operation completed",  },})
// List available agentsconst agents = await client.app.agents()
```

---

### [Проект](#проект)

Метод

Описание

Ответ

`project.list()`

List all projects

[`Project[]`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)

`project.current()`

Get current project

[`Project`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)

---

#### [Примеры](#примеры-2)

```
// List all projectsconst projects = await client.project.list()
// Get current projectconst currentProject = await client.project.current()
```

---

### [Путь](#путь)

Метод

Описание

Ответ

`path.get()`

Get current path

[`Path`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)

---

#### [Примеры](#примеры-3)

```
// Get current path informationconst pathInfo = await client.path.get()
```

---

### [Конфигурация](#конфигурация-1)

Метод

Описание

Ответ

`config.get()`

Get config info

[`Config`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)

`config.providers()`

List providers and default models

`{ providers:` [`Provider[]`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)`, default: { [key: string]: string } }`

---

#### [Примеры](#примеры-4)

```
const config = await client.config.get()
const { providers, default: defaults } = await client.config.providers()
```

---

### [Сессии](#сессии)

Метод

Описание

Примечания

`session.list()`

List sessions

Returns [`Session[]`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)

`session.get({ path })`

Get session

Returns [`Session`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)

`session.children({ path })`

List child sessions

Returns [`Session[]`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)

`session.create({ body })`

Create session

Returns [`Session`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)

`session.delete({ path })`

Delete session

Returns `boolean`

`session.update({ path, body })`

Update session properties

Returns [`Session`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)

`session.init({ path, body })`

Analyze app and create `AGENTS.md`

Returns `boolean`

`session.abort({ path })`

Abort a running session

Returns `boolean`

`session.share({ path })`

Share session

Returns [`Session`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)

`session.unshare({ path })`

Unshare session

Returns [`Session`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)

`session.summarize({ path, body })`

Summarize session

Returns `boolean`

`session.messages({ path })`

List messages in a session

Returns `{ info:` [`Message`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)`, parts:` [`Part[]`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)`}[]`

`session.message({ path })`

Get message details

Returns `{ info:` [`Message`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)`, parts:` [`Part[]`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)`}`

`session.prompt({ path, body })`

Send prompt message

`body.noReply: true` возвращает UserMessage (только контекст). По умолчанию возвращает [`AssistantMessage`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts) с ответом ИИ. Поддерживает `body.outputFormat` для [структурированного вывода](#структурированный-вывод)

`session.command({ path, body })`

Send command to session

Returns `{ info:` [`AssistantMessage`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)`, parts:` [`Part[]`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)`}`

`session.shell({ path, body })`

Run a shell command

Returns [`AssistantMessage`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)

`session.revert({ path, body })`

Revert a message

Returns [`Session`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)

`session.unrevert({ path })`

Restore reverted messages

Returns [`Session`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)

`postSessionByIdPermissionsByPermissionId({ path, body })`

Respond to a permission request

Returns `boolean`

---

#### [Примеры](#примеры-5)

```
// Create and manage sessionsconst session = await client.session.create({  body: { title: "My session" },})
const sessions = await client.session.list()
// Send a prompt messageconst result = await client.session.prompt({  path: { id: session.id },  body: {    model: { providerID: "anthropic", modelID: "claude-3-5-sonnet-20241022" },    parts: [{ type: "text", text: "Hello!" }],  },})
// Inject context without triggering AI response (useful for plugins)await client.session.prompt({  path: { id: session.id },  body: {    noReply: true,    parts: [{ type: "text", text: "You are a helpful assistant." }],  },})
```

---

### [Файлы](#файлы)

Метод

Описание

Ответ

`find.text({ query })`

Search for text in files

Array of match objects with `path`, `lines`, `line_number`, `absolute_offset`, `submatches`

`find.files({ query })`

Find files and directories by name

`string[]` (paths)

`find.symbols({ query })`

Find workspace symbols

[`Symbol[]`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)

`file.read({ query })`

Read a file

`{ type: "raw" | "patch", content: string }`

`file.status({ query? })`

Get status for tracked files

[`File[]`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)

`find.files` поддерживает несколько дополнительных полей запроса:

-   `type`: `"file"` или `"directory"`
-   `directory`: переопределить корень проекта для поиска.
-   `limit`: максимальное количество результатов (1–200)

---

#### [Примеры](#примеры-6)

```
// Search and read filesconst textResults = await client.find.text({  query: { pattern: "function.*opencode" },})
const files = await client.find.files({  query: { query: "*.ts", type: "file" },})
const directories = await client.find.files({  query: { query: "packages", type: "directory", limit: 20 },})
const content = await client.file.read({  query: { path: "src/index.ts" },})
```

---

### [TUI](#tui)

Метод

Описание

Ответ

`tui.appendPrompt({ body })`

Append text to the prompt

`boolean`

`tui.openHelp()`

Open the help dialog

`boolean`

`tui.openSessions()`

Open the session selector

`boolean`

`tui.openThemes()`

Open the theme selector

`boolean`

`tui.openModels()`

Open the model selector

`boolean`

`tui.submitPrompt()`

Submit the current prompt

`boolean`

`tui.clearPrompt()`

Clear the prompt

`boolean`

`tui.executeCommand({ body })`

Execute a command

`boolean`

`tui.showToast({ body })`

Show toast notification

`boolean`

---

#### [Примеры](#примеры-7)

```
// Control TUI interfaceawait client.tui.appendPrompt({  body: { text: "Add this to prompt" },})
await client.tui.showToast({  body: { message: "Task completed", variant: "success" },})
```

---

### [Аутентификация](#аутентификация)

Метод

Описание

Ответ

`auth.set({ ... })`

Set authentication credentials

`boolean`

---

#### [Примеры](#примеры-8)

```
await client.auth.set({  path: { id: "anthropic" },  body: { type: "api", key: "your-api-key" },})
```

---

### [События](#события)

Метод

Описание

Ответ

`event.subscribe()`

Server-sent events stream

Server-sent events stream

---

#### [Примеры](#примеры-9)

```
// Listen to real-time eventsconst events = await client.event.subscribe()for await (const event of events.stream) {  console.log("Event:", event.type, event.properties)}
```

[Редактировать страницу](https://github.com/anomalyco/opencode/edit/dev/packages/web/src/content/docs/ru/sdk.mdx)[Found a bug? Open an issue](https://github.com/anomalyco/opencode/issues/new)[Join our Discord community](https://opencode.ai/discord) Выберите язык EnglishالعربيةBosanskiDanskDeutschEspañolFrançaisItaliano日本語한국어Norsk BokmålPolskiPortuguês (Brasil)РусскийไทยTürkçe简体中文繁體中文 

© [Anomaly](https://anoma.ly)

Последнее обновление: 30 мая 2026 г.
