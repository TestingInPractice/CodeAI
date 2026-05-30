MCP-серверы | OpenCode     [Перейти к содержимому](#_top)

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
-   [Включение](#включение)
    -   [Переопределение удаленных настроек по умолчанию](#переопределение-удаленных-настроек-по-умолчанию)
-   [Локальные](#локальные)
-   [Удаленные](#удаленные)
-   [OAuth](#oauth)
    -   [Автоматически](#автоматически)
    -   [Предварительная регистрация](#предварительная-регистрация)
    -   [Аутентификация](#аутентификация)
-   [Управление](#управление)
    -   [Глобально](#глобально)
    -   [Для каждого агента](#для-каждого-агента)
-   [Примеры](#примеры)
    -   [Sentry](#sentry)
    -   [Context7](#context7)
    -   [Grep by Vercel](#grep-by-vercel)

## На этой странице

-   [Обзор](#_top)
-   [Включение](#включение)
    -   [Переопределение удаленных настроек по умолчанию](#переопределение-удаленных-настроек-по-умолчанию)
-   [Локальные](#локальные)
-   [Удаленные](#удаленные)
-   [OAuth](#oauth)
    -   [Автоматически](#автоматически)
    -   [Предварительная регистрация](#предварительная-регистрация)
    -   [Аутентификация](#аутентификация)
-   [Управление](#управление)
    -   [Глобально](#глобально)
    -   [Для каждого агента](#для-каждого-агента)
-   [Примеры](#примеры)
    -   [Sentry](#sentry)
    -   [Context7](#context7)
    -   [Grep by Vercel](#grep-by-vercel)

# MCP-серверы

Добавьте локальные и удаленные инструменты MCP.

Вы можете добавить внешние инструменты в opencode, используя *Model Context Protocol* или MCP. opencode поддерживает как локальные, так и удаленные серверы.

После добавления инструменты MCP автоматически становятся доступными для LLM наряду со встроенными инструментами.

---

#### [Предостережения](#предостережения)

Когда вы используете сервер MCP, он добавляет контекст. Это может быстро сложиться, если у вас много инструментов. Поэтому мы рекомендуем быть осторожными с тем, какие серверы MCP вы используете.

Совет

Серверы MCP добавляются к вашему контексту, поэтому будьте осторожны с тем, какие из них вы включаете.

Некоторые серверы MCP, такие как сервер MCP GitHub, имеют тенденцию добавлять много токенов и могут легко превысить ограничение контекста.

---

## [Включение](#включение)

Вы можете определить серверы MCP в своем [opencode Config](https://opencode.ai/docs/config/) в разделе `mcp`. Добавьте каждому MCP уникальное имя. Вы можете обратиться к этому MCP по имени при запросе LLM.

opencode.jsonc

```
{  "$schema": "https://opencode.ai/config.json",  "mcp": {    "name-of-mcp-server": {      // ...      "enabled": true,    },    "name-of-other-mcp-server": {      // ...    },  },}
```

Вы также можете отключить сервер, установив для `enabled` значение `false`. Это полезно, если вы хотите временно отключить сервер, не удаляя его из конфигурации.

---

### [Переопределение удаленных настроек по умолчанию](#переопределение-удаленных-настроек-по-умолчанию)

Организации могут предоставлять серверы MCP по умолчанию через свою конечную точку `.well-known/opencode`. Эти серверы могут быть отключены по умолчанию, что позволяет пользователям выбирать те, которые им нужны.

Чтобы включить определенный сервер из удаленной конфигурации вашей организации, добавьте его в локальную конфигурацию с помощью `enabled: true`:

opencode.json

```
{  "$schema": "https://opencode.ai/config.json",  "mcp": {    "jira": {      "type": "remote",      "url": "https://jira.example.com/mcp",      "enabled": true    }  }}
```

Значения вашей локальной конфигурации переопределяют удаленные значения по умолчанию. Дополнительную информацию см. в [приоритете конфигурации](/docs/config#precedence-order).

---

## [Локальные](#локальные)

Добавьте локальные серверы MCP с помощью `type` в `"local"` внутри объекта MCP.

opencode.jsonc

```
{  "$schema": "https://opencode.ai/config.json",  "mcp": {    "my-local-mcp-server": {      "type": "local",      // Or ["bun", "x", "my-mcp-command"]      "command": ["npx", "-y", "my-mcp-command"],      "enabled": true,      "environment": {        "MY_ENV_VAR": "my_env_var_value",      },    },  },}
```

Эта команда запускает локальный сервер MCP. Вы также можете передать список переменных среды.

Например, вот как можно добавить тестовый сервер [`@modelcontextprotocol/server-everything`](https://www.npmjs.com/package/@modelcontextprotocol/server-everything) MCP.

opencode.jsonc

```
{  "$schema": "https://opencode.ai/config.json",  "mcp": {    "mcp_everything": {      "type": "local",      "command": ["npx", "-y", "@modelcontextprotocol/server-everything"],    },  },}
```

И чтобы использовать его, добавьте `use the mcp_everything tool` в свои подсказки.

```
use the mcp_everything tool to add the number 3 and 4
```

---

#### [Параметры](#параметры)

Вот все варианты настройки локального сервера MCP.

Вариант

Тип

Обязательный

Описание

`type`

Строка

Да

Тип подключения к серверу MCP должен быть `"local"`.

`command`

Массив

Да

Команда и аргументы для запуска сервера MCP.

`environment`

Объект

Переменные среды, которые необходимо установить при запуске сервера.

`enabled`

логическое значение

Включите или отключите сервер MCP при запуске.

`timeout`

Число

Тайм-аут в мс для получения инструментов с сервера MCP. По умолчанию 5000 (5 секунд).

---

## [Удаленные](#удаленные)

Добавьте удаленные серверы MCP, установив для `type` значение `"remote"`.

opencode.json

```
{  "$schema": "https://opencode.ai/config.json",  "mcp": {    "my-remote-mcp": {      "type": "remote",      "url": "https://my-mcp-server.com",      "enabled": true,      "headers": {        "Authorization": "Bearer MY_API_KEY"      }    }  }}
```

`url` — это URL-адрес удаленного сервера MCP, а с помощью параметра `headers` вы можете передать список заголовков.

---

#### [Параметры](#параметры-1)

Вариант

Тип

Обязательный

Описание

`type`

Строка

Да

Тип подключения к серверу MCP должен быть `"remote"`.

`url`

Строка

Да

URL-адрес удаленного сервера MCP.

`enabled`

логическое значение

Включите или отключите сервер MCP при запуске.

`headers`

Объект

Заголовки для отправки с запросом.

`oauth`

Объект

Конфигурация аутентификации OAuth. См. раздел [OAuth](#oauth) ниже.

`timeout`

Число

Тайм-аут в мс для получения инструментов с сервера MCP. По умолчанию 5000 (5 секунд).

---

## [OAuth](#oauth)

opencode автоматически обрабатывает аутентификацию OAuth для удаленных серверов MCP. Когда серверу требуется аутентификация, opencode:

1.  Обнаружьте ответ 401 и инициируйте поток OAuth.
2.  Используйте **Динамическую регистрацию клиента (RFC 7591)**, если это поддерживается сервером.
3.  Надежно храните токены для будущих запросов

---

### [Автоматически](#автоматически)

Для большинства серверов MCP с поддержкой OAuth не требуется никакой специальной настройки. Просто настройте удаленный сервер:

opencode.json

```
{  "$schema": "https://opencode.ai/config.json",  "mcp": {    "my-oauth-server": {      "type": "remote",      "url": "https://mcp.example.com/mcp"    }  }}
```

Если сервер требует аутентификации, opencode предложит вам пройти аутентификацию при первой попытке его использования. Если нет, вы можете [вручную запустить поток](#authenticating) с помощью `opencode mcp auth <server-name>`.

---

### [Предварительная регистрация](#предварительная-регистрация)

Если у вас есть учетные данные клиента от поставщика сервера MCP, вы можете их настроить:

opencode.json

```
{  "$schema": "https://opencode.ai/config.json",  "mcp": {    "my-oauth-server": {      "type": "remote",      "url": "https://mcp.example.com/mcp",      "oauth": {        "clientId": "{env:MY_MCP_CLIENT_ID}",        "clientSecret": "{env:MY_MCP_CLIENT_SECRET}",        "scope": "tools:read tools:execute"      }    }  }}
```

---

### [Аутентификация](#аутентификация)

Вы можете вручную активировать аутентификацию или управлять учетными данными.

Аутентификация с помощью определенного сервера MCP:

Окно терминала

```
opencode mcp auth my-oauth-server
```

Перечислите все серверы MCP и их статус аутентификации:

Окно терминала

```
opencode mcp list
```

Удалить сохраненные учетные данные:

Окно терминала

```
opencode mcp logout my-oauth-server
```

Команда `mcp auth` откроет ваш браузер для авторизации. После того как вы авторизуетесь, opencode надежно сохранит токены в `~/.local/share/opencode/mcp-auth.json`.

---

#### [Отключение OAuth](#отключение-oauth)

Если вы хотите отключить автоматический OAuth для сервера (например, для серверов, которые вместо этого используют ключи API), установите для `oauth` значение `false`:

opencode.json

```
{  "$schema": "https://opencode.ai/config.json",  "mcp": {    "my-api-key-server": {      "type": "remote",      "url": "https://mcp.example.com/mcp",      "oauth": false,      "headers": {        "Authorization": "Bearer {env:MY_API_KEY}"      }    }  }}
```

---

#### [Параметры OAuth](#параметры-oauth)

Вариант

Тип

Описание

`oauth`

Object | false

Объект конфигурации OAuth или `false`, чтобы отключить автообнаружение OAuth.

`clientId`

String

OAuth client ID. Если не указан, будет выполнена динамическая регистрация клиента.

`clientSecret`

String

OAuth client secret, если этого требует сервер авторизации.

`scope`

String

OAuth scopes для запроса во время авторизации.

#### [Отладка](#отладка)

Если удаленный сервер MCP не может аутентифицироваться, вы можете диагностировать проблемы с помощью:

Окно терминала

```
# View auth status for all OAuth-capable serversopencode mcp auth list
# Debug connection and OAuth flow for a specific serveropencode mcp debug my-oauth-server
```

Команда `mcp debug` показывает текущий статус аутентификации, проверяет соединение HTTP и пытается выполнить поток обнаружения OAuth.

---

## [Управление](#управление)

Ваши MCP доступны в виде инструментов opencode наряду со встроенными инструментами. Таким образом, вы можете управлять ими через конфигурацию opencode, как и любым другим инструментом.

---

### [Глобально](#глобально)

Это означает, что вы можете включать или отключать их глобально.

opencode.json

```
{  "$schema": "https://opencode.ai/config.json",  "mcp": {    "my-mcp-foo": {      "type": "local",      "command": ["bun", "x", "my-mcp-command-foo"]    },    "my-mcp-bar": {      "type": "local",      "command": ["bun", "x", "my-mcp-command-bar"]    }  },  "tools": {    "my-mcp-foo": false  }}
```

Мы также можем использовать шаблон glob, чтобы отключить все соответствующие MCP.

opencode.json

```
{  "$schema": "https://opencode.ai/config.json",  "mcp": {    "my-mcp-foo": {      "type": "local",      "command": ["bun", "x", "my-mcp-command-foo"]    },    "my-mcp-bar": {      "type": "local",      "command": ["bun", "x", "my-mcp-command-bar"]    }  },  "tools": {    "my-mcp*": false  }}
```

Здесь мы используем шаблон `my-mcp*` для отключения всех MCP.

---

### [Для каждого агента](#для-каждого-агента)

Если у вас большое количество серверов MCP, вы можете включить их только для каждого агента и отключить глобально. Для этого:

1.  Отключите его как инструмент глобально.
2.  В вашей [конфигурации агента](/docs/agents#tools) включите сервер MCP в качестве инструмента.

opencode.json

```
{  "$schema": "https://opencode.ai/config.json",  "mcp": {    "my-mcp": {      "type": "local",      "command": ["bun", "x", "my-mcp-command"],      "enabled": true    }  },  "tools": {    "my-mcp*": false  },  "agent": {    "my-agent": {      "tools": {        "my-mcp*": true      }    }  }}
```

---

#### [Glob-шаблоны](#glob-шаблоны)

Шаблон glob использует простые шаблоны подстановки регулярных выражений:

-   `*` соответствует нулю или более любого символа (например, `"my-mcp*"` соответствует `my-mcp_search`, `my-mcp_list` и т. д.).
-   `?` соответствует ровно одному символу.
-   Все остальные символы совпадают буквально

Заметка

Инструменты сервера MCP регистрируются с именем сервера в качестве префикса, поэтому, чтобы отключить все инструменты для сервера, просто используйте:

```
"mymcpservername_*": false
```

---

## [Примеры](#примеры)

Ниже приведены примеры некоторых распространенных серверов MCP. Вы можете отправить PR, если хотите документировать другие серверы.

---

### [Sentry](#sentry)

Добавьте [сервер Sentry MCP](https://mcp.sentry.dev) для взаимодействия с вашими проектами и проблемами Sentry.

opencode.json

```
{  "$schema": "https://opencode.ai/config.json",  "mcp": {    "sentry": {      "type": "remote",      "url": "https://mcp.sentry.dev/mcp",      "oauth": {}    }  }}
```

После добавления конфигурации пройдите аутентификацию с помощью Sentry:

Окно терминала

```
opencode mcp auth sentry
```

Откроется окно браузера для завершения процесса OAuth и подключения opencode к вашей учетной записи Sentry.

После аутентификации вы можете использовать инструменты Sentry в своих подсказках для запроса данных о проблемах, проектах и ошибках.

```
Show me the latest unresolved issues in my project. use sentry
```

---

### [Context7](#context7)

Добавьте [сервер Context7 MCP](https://github.com/upstash/context7) для поиска в документах.

opencode.json

```
{  "$schema": "https://opencode.ai/config.json",  "mcp": {    "context7": {      "type": "remote",      "url": "https://mcp.context7.com/mcp"    }  }}
```

Если вы зарегистрировали бесплатную учетную запись, вы можете использовать свой ключ API и получить более высокие ограничения скорости.

opencode.json

```
{  "$schema": "https://opencode.ai/config.json",  "mcp": {    "context7": {      "type": "remote",      "url": "https://mcp.context7.com/mcp",      "headers": {        "CONTEXT7_API_KEY": "{env:CONTEXT7_API_KEY}"      }    }  }}
```

Здесь мы предполагаем, что у вас установлена переменная среды `CONTEXT7_API_KEY`.

Добавьте `use context7` в запросы на использование сервера Context7 MCP.

```
Configure a Cloudflare Worker script to cache JSON API responses for five minutes. use context7
```

Альтернативно вы можете добавить что-то подобное в свой файл [AGENTS.md](/docs/rules/).

AGENTS.md

```
When you need to search docs, use `context7` tools.
```

---

### [Grep by Vercel](#grep-by-vercel)

Добавьте сервер MCP [Grep от Vercel](https://grep.app) для поиска по фрагментам кода на GitHub.

opencode.json

```
{  "$schema": "https://opencode.ai/config.json",  "mcp": {    "gh_grep": {      "type": "remote",      "url": "https://mcp.grep.app"    }  }}
```

Поскольку мы назвали наш сервер MCP `gh_grep`, вы можете добавить `use the gh_grep tool` в свои запросы, чтобы агент мог его использовать.

```
What's the right way to set a custom domain in an SST Astro component? use the gh_grep tool
```

Альтернативно вы можете добавить что-то подобное в свой файл [AGENTS.md](/docs/rules/).

AGENTS.md

```
If you are unsure how to do something, use `gh_grep` to search code examples from GitHub.
```

[Редактировать страницу](https://github.com/anomalyco/opencode/edit/dev/packages/web/src/content/docs/ru/mcp-servers.mdx)[Found a bug? Open an issue](https://github.com/anomalyco/opencode/issues/new)[Join our Discord community](https://opencode.ai/discord) Выберите язык EnglishالعربيةBosanskiDanskDeutschEspañolFrançaisItaliano日本語한국어Norsk BokmålPolskiPortuguês (Brasil)РусскийไทยTürkçe简体中文繁體中文 

© [Anomaly](https://anoma.ly)

Последнее обновление: 30 мая 2026 г.
