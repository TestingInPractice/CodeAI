Сервер | OpenCode     [Перейти к содержимому](#_top)

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
    -   [Использование](#использование)
    -   [Аутентификация](#аутентификация)
    -   [Как это работает](#как-это-работает)
-   [Спецификация](#спецификация)
-   [API](#api)
    -   [Глобальный](#глобальный)
    -   [Проект](#проект)
    -   [Путь и система контроля версий](#путь-и-система-контроля-версий)
    -   [Экземпляр](#экземпляр)
    -   [Конфигурация](#конфигурация)
    -   [Поставщик](#поставщик)
    -   [Сессии](#сессии)
    -   [Сообщения](#сообщения)
    -   [Команды](#команды)
    -   [Файлы](#файлы)
    -   [Инструменты (Экспериментальные)](#инструменты-экспериментальные)
    -   [LSP, форматтеры и MCP](#lsp-форматтеры-и-mcp)
    -   [Агенты](#агенты)
    -   [Ведение журнала](#ведение-журнала)
    -   [TUI](#tui)
    -   [Авторизация](#авторизация)
    -   [События](#события)
    -   [Документы](#документы)

## На этой странице

-   [Обзор](#_top)
    -   [Использование](#использование)
    -   [Аутентификация](#аутентификация)
    -   [Как это работает](#как-это-работает)
-   [Спецификация](#спецификация)
-   [API](#api)
    -   [Глобальный](#глобальный)
    -   [Проект](#проект)
    -   [Путь и система контроля версий](#путь-и-система-контроля-версий)
    -   [Экземпляр](#экземпляр)
    -   [Конфигурация](#конфигурация)
    -   [Поставщик](#поставщик)
    -   [Сессии](#сессии)
    -   [Сообщения](#сообщения)
    -   [Команды](#команды)
    -   [Файлы](#файлы)
    -   [Инструменты (Экспериментальные)](#инструменты-экспериментальные)
    -   [LSP, форматтеры и MCP](#lsp-форматтеры-и-mcp)
    -   [Агенты](#агенты)
    -   [Ведение журнала](#ведение-журнала)
    -   [TUI](#tui)
    -   [Авторизация](#авторизация)
    -   [События](#события)
    -   [Документы](#документы)

# Сервер

Взаимодействуйте с сервером opencode через HTTP.

Команда `opencode serve` запускает автономный HTTP-сервер, который предоставляет конечную точку OpenAPI, которую может использовать клиент с открытым кодом.

---

### [Использование](#использование)

Окно терминала

```
opencode serve [--port <number>] [--hostname <string>] [--cors <origin>]
```

#### [Параметры](#параметры)

Флаг

Описание

По умолчанию

`--port`

Порт для прослушивания

`4096`

`--hostname`

Имя хоста для прослушивания

`127.0.0.1`

`--mdns`

Включить обнаружение mDNS

`false`

`--mdns-domain`

Пользовательское доменное имя для mDNS

`opencode.local`

`--cors`

Разрешенные дополнительные источники (CORS)

`[]`

`--cors` можно передать несколько раз:

Окно терминала

```
opencode serve --cors http://localhost:5173 --cors https://app.example.com
```

---

### [Аутентификация](#аутентификация)

Установите `OPENCODE_SERVER_PASSWORD`, чтобы защитить сервер с помощью базовой аутентификации HTTP. Имя пользователя по умолчанию — `opencode` или установите `OPENCODE_SERVER_USERNAME`, чтобы переопределить его. Это относится как к `opencode serve`, так и к `opencode web`.

Окно терминала

```
OPENCODE_SERVER_PASSWORD=your-password opencode serve
```

---

### [Как это работает](#как-это-работает)

Когда вы запускаете `opencode`, он запускает TUI и сервер. Где находится TUI клиент, который общается с сервером. Сервер предоставляет спецификацию OpenAPI 3.1. конечная точка. Эта конечная точка также используется для создания файла [SDK](/docs/sdk).

Совет

Используйте сервер opencode для программного взаимодействия с открытым кодом.

Эта архитектура позволяет открытому коду поддерживать несколько клиентов и позволяет программно взаимодействовать с открытым кодом.

Вы можете запустить `opencode serve`, чтобы запустить автономный сервер. Если у вас есть TUI с открытым кодом запущен, `opencode serve` запустит новый сервер.

---

#### [Подключиться к существующему серверу](#подключиться-к-существующему-серверу)

Когда вы запускаете TUI, он случайным образом назначает порт и имя хоста. Вместо этого вы можете передать `--hostname` и `--port` [flags](/docs/cli). Затем используйте это для подключения к его серверу.

Конечную точку [`/tui`](#tui) можно использовать для управления TUI через сервер. Например, вы можете предварительно заполнить или запустить подсказку. Эта настройка используется плагинами opencode [IDE](/docs/ide).

---

## [Спецификация](#спецификация)

Сервер публикует спецификацию OpenAPI 3.1, которую можно просмотреть по адресу:

```
http://<hostname>:<port>/doc
```

For example, `http://localhost:4096/doc`. Use the spec to generate clients or inspect request and response types. Or view it in a Swagger explorer.

---

## [API](#api)

Сервер opencode предоставляет следующие API.

---

### [Глобальный](#глобальный)

Метод

Путь

Описание

Ответ

`GET`

`/global/health`

Получить состояние и версию сервера

`{ healthy: true, version: string }`

`GET`

`/global/event`

Получить глобальные события (поток SSE)

Поток событий

---

### [Проект](#проект)

Метод

Путь

Описание

Ответ

`GET`

`/project`

Список всех проектов

[`Project[]`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)

`GET`

`/project/current`

Получить текущий проект

[`Project`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)

---

### [Путь и система контроля версий](#путь-и-система-контроля-версий)

Метод

Путь

Описание

Ответ

`GET`

`/path`

Получить текущий путь

[`Path`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)

`GET`

`/vcs`

Получить информацию о VCS для текущего проекта

[`VcsInfo`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)

---

### [Экземпляр](#экземпляр)

Метод

Путь

Описание

Ответ

`POST`

`/instance/dispose`

Удалить текущий экземпляр

`boolean`

---

### [Конфигурация](#конфигурация)

Метод

Путь

Описание

Ответ

`GET`

`/config`

Получить информацию о конфигурации

[`Config`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)

`PATCH`

`/config`

Обновить конфигурацию

[`Config`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)

`GET`

`/config/providers`

Список провайдеров и моделей по умолчанию

`{ providers:` [Provider[]](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)`, default: { [key: string]: string } }`

---

### [Поставщик](#поставщик)

Метод

Путь

Описание

Ответ

`GET`

`/provider`

Список всех провайдеров

`{ all:` [Provider[]](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)`, default: {...}, connected: string[] }`

`GET`

`/provider/auth`

Получить методы аутентификации провайдера

`{ [providerID: string]:` [ProviderAuthMethod[]](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts) `}`

`POST`

`/provider/{id}/oauth/authorize`

Авторизация провайдера через OAuth

[`ProviderAuthAuthorization`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)

`POST`

`/provider/{id}/oauth/callback`

Обработка callback OAuth для провайдера

`boolean`

---

### [Сессии](#сессии)

Метод

Путь

Описание

Примечания

`GET`

`/session`

Список всех сессий

Возвращает [`Session[]`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)

`POST`

`/session`

Создать новую сессию

body: `{ parentID?, title? }`, возвращает [`Session`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)

`GET`

`/session/status`

Получить статус всех сессий

Возвращает `{ [sessionID: string]:` [SessionStatus](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts) `}`

`GET`

`/session/:id`

Получить детали сессии

Возвращает [`Session`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)

`DELETE`

`/session/:id`

Удалить сессию и все её данные

Возвращает `boolean`

`PATCH`

`/session/:id`

Обновить свойства сессии

body: `{ title? }`, возвращает [`Session`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)

`GET`

`/session/:id/children`

Получить дочерние сессии

Возвращает [`Session[]`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)

`GET`

`/session/:id/todo`

Получить список задач для сессии

Возвращает [`Todo[]`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)

`POST`

`/session/:id/init`

Анализ приложения и создание `AGENTS.md`

body: `{ messageID, providerID, modelID }`, возвращает `boolean`

`POST`

`/session/:id/fork`

Ответвление сессии от сообщения

body: `{ messageID? }`, возвращает [`Session`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)

`POST`

`/session/:id/abort`

Прервать запущенную сессию

Возвращает `boolean`

`POST`

`/session/:id/share`

Поделиться сессией

Возвращает [`Session`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)

`DELETE`

`/session/:id/share`

Отменить общий доступ к сессии

Возвращает [`Session`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)

`GET`

`/session/:id/diff`

Получить diff для этой сессии

query: `messageID?`, возвращает [`FileDiff[]`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)

`POST`

`/session/:id/summarize`

Суммировать сессию

body: `{ providerID, modelID }`, возвращает `boolean`

`POST`

`/session/:id/revert`

Отменить сообщение

body: `{ messageID, partID? }`, возвращает `boolean`

`POST`

`/session/:id/unrevert`

Восстановить все отмененные сообщения

Возвращает `boolean`

`POST`

`/session/:id/permissions/:permissionID`

Ответить на запрос разрешения

body: `{ response, remember? }`, возвращает `boolean`

---

### [Сообщения](#сообщения)

Метод

Путь

Описание

Примечания

`GET`

`/session/:id/message`

Список сообщений в сессии

query: `limit?`, возвращает `{ info:` [Message](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)`, parts:` [Part[]](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)`}[]`

`POST`

`/session/:id/message`

Отправить сообщение и ждать ответа

body: `{ messageID?, model?, agent?, noReply?, system?, tools?, parts }`, возвращает `{ info:` [Message](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)`, parts:` [Part[]](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)`}`

`GET`

`/session/:id/message/:messageID`

Получить детали сообщения

Возвращает `{ info:` [Message](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)`, parts:` [Part[]](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)`}`

`POST`

`/session/:id/prompt_async`

Отправить сообщение асинхронно (без ожидания)

body: как в `/session/:id/message`, возвращает `204 No Content`

`POST`

`/session/:id/command`

Выполнить слэш-команду

body: `{ messageID?, agent?, model?, command, arguments }`, возвращает `{ info:` [Message](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)`, parts:` [Part[]](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)`}`

`POST`

`/session/:id/shell`

Запустить команду оболочки

body: `{ agent, model?, command }`, возвращает `{ info:` [Message](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)`, parts:` [Part[]](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)`}`

---

### [Команды](#команды)

Метод

Путь

Описание

Ответ

`GET`

`/command`

Список всех команд

[`Command[]`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)

---

### [Файлы](#файлы)

Метод

Путь

Описание

Ответ

`GET`

`/find?pattern=<pat>`

Поиск текста в файлах

Массив объектов совпадения с `path`, `lines`, `line_number`, `absolute_offset`, `submatches`

`GET`

`/find/file?query=<q>`

Поиск файлов и директорий по имени

`string[]` (пути)

`GET`

`/find/symbol?query=<q>`

Поиск символов рабочего пространства

[`Symbol[]`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)

`GET`

`/file?path=<path>`

Список файлов и директорий

[`FileNode[]`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)

`GET`

`/file/content?path=<p>`

Прочитать файл

[`FileContent`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)

`GET`

`/file/status`

Получить статус отслеживаемых файлов

[`File[]`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)

#### [`/find/file` параметры запроса](#findfile-параметры-запроса)

-   `query` (обязательно) — строка поиска (нечеткое совпадение)
-   `type` (необязательно) — ограничить результаты `"file"` или `"directory"`.
-   `directory` (необязательно) — переопределить корень проекта для поиска.
-   `limit` (необязательно) — максимальное количество результатов (1–200)
-   `dirs` (необязательно) — устаревший флаг (`"false"` возвращает только файлы)

---

### [Инструменты (Экспериментальные)](#инструменты-экспериментальные)

Метод

Путь

Описание

Ответ

`GET`

`/experimental/tool/ids`

Список всех идентификаторов инструментов

[`ToolIDs`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)

`GET`

`/experimental/tool?provider=<p>&model=<m>`

Список инструментов со схемами JSON для модели

[`ToolList`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)

---

### [LSP, форматтеры и MCP](#lsp-форматтеры-и-mcp)

Метод

Путь

Описание

Ответ

`GET`

`/lsp`

Получить статус сервера LSP

[`LSPStatus[]`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)

`GET`

`/formatter`

Получить статус форматера

[`FormatterStatus[]`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)

`GET`

`/mcp`

Получить статус сервера MCP

`{ [name: string]:` [MCPStatus](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts) `}`

`POST`

`/mcp`

Добавить сервер MCP динамически

body: `{ name, config }`, возвращает статус объекта MCP

---

### [Агенты](#агенты)

Метод

Путь

Описание

Ответ

`GET`

`/agent`

Список всех доступных агентов

[`Agent[]`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)

---

### [Ведение журнала](#ведение-журнала)

Метод

Путь

Описание

Ответ

`POST`

`/log`

Записать запись в журнал. Body: `{ service, level, message, extra? }`

`boolean`

---

### [TUI](#tui)

Метод

Путь

Описание

Ответ

`POST`

`/tui/append-prompt`

Добавить текст в подсказку

`boolean`

`POST`

`/tui/open-help`

Открыть диалог помощи

`boolean`

`POST`

`/tui/open-sessions`

Открыть селектор сессий

`boolean`

`POST`

`/tui/open-themes`

Открыть селектор тем

`boolean`

`POST`

`/tui/open-models`

Открыть селектор моделей

`boolean`

`POST`

`/tui/submit-prompt`

Отправить текущую подсказку

`boolean`

`POST`

`/tui/clear-prompt`

Очистить подсказку

`boolean`

`POST`

`/tui/execute-command`

Выполнить команду (`{ command }`)

`boolean`

`POST`

`/tui/show-toast`

Показать уведомление (`{ title?, message, variant }`)

`boolean`

`GET`

`/tui/control/next`

Ожидание следующего запроса управления

Объект запроса управления

`POST`

`/tui/control/response`

Ответить на запрос управления (`{ body }`)

`boolean`

---

### [Авторизация](#авторизация)

Метод

Путь

Описание

Ответ

`PUT`

`/auth/:id`

Установить учетные данные аутентификации. Body должен соответствовать схеме провайдера

`boolean`

---

### [События](#события)

Метод

Путь

Описание

Ответ

`GET`

`/event`

Поток событий, отправляемых сервером. Первое событие — `server.connected`, затем события шины

Поток событий, отправляемых сервером

---

### [Документы](#документы)

Метод

Путь

Описание

Ответ

`GET`

`/doc`

Спецификация OpenAPI 3.1

HTML-страница со спецификацией OpenAPI

[Редактировать страницу](https://github.com/anomalyco/opencode/edit/dev/packages/web/src/content/docs/ru/server.mdx)[Found a bug? Open an issue](https://github.com/anomalyco/opencode/issues/new)[Join our Discord community](https://opencode.ai/discord) Выберите язык EnglishالعربيةBosanskiDanskDeutschEspañolFrançaisItaliano日本語한국어Norsk BokmålPolskiPortuguês (Brasil)РусскийไทยTürkçe简体中文繁體中文 

© [Anomaly](https://anoma.ly)

Последнее обновление: 30 мая 2026 г.
