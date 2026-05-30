Поддержка ACP | OpenCode     [Перейти к содержимому](#_top)

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
    -   [Zed](#zed)
    -   [IDE JetBrains](#ide-jetbrains)
    -   [Avante.nvim](#avantenvim)
    -   [CodeCompanion.nvim](#codecompanionnvim)
-   [Поддержка](#поддержка)

## На этой странице

-   [Обзор](#_top)
-   [Настройка](#настройка)
    -   [Zed](#zed)
    -   [IDE JetBrains](#ide-jetbrains)
    -   [Avante.nvim](#avantenvim)
    -   [CodeCompanion.nvim](#codecompanionnvim)
-   [Поддержка](#поддержка)

# Поддержка ACP

Используйте opencode в любом ACP-совместимом редакторе.

opencode поддерживает [Agent Client Protocol](https://agentclientprotocol.com) (ACP), что позволяет использовать его непосредственно в совместимых редакторах и IDE.

Совет

Список редакторов и инструментов, поддерживающих ACP, можно найти в [отчете о ходе работы ACP](https://zed.dev/blog/acp-progress-report#available-now).

ACP — это открытый протокол, который стандартизирует взаимодействие между редакторами кода и ИИ-агентами.

---

## [Настройка](#настройка)

Чтобы использовать opencode через ACP, настройте свой редактор для запуска команды `opencode acp`.

Команда запускает opencode как ACP-совместимый подпроцесс, который взаимодействует с вашим редактором через JSON-RPC через stdio.

Ниже приведены примеры популярных редакторов, поддерживающих ACP.

---

### [Zed](#zed)

Добавьте в конфигурацию [Zed](https://zed.dev) (`~/.config/zed/settings.json`):

~/.config/zed/settings.json

```
{  "agent_servers": {    "OpenCode": {      "command": "opencode",      "args": ["acp"]    }  }}
```

Чтобы открыть его, используйте действие `agent: new thread` в **Палитре команд**.

Вы также можете привязать сочетание клавиш, отредактировав свой `keymap.json`:

keymap.json

```
[  {    "bindings": {      "cmd-alt-o": [        "agent::NewExternalAgentThread",        {          "agent": {            "custom": {              "name": "OpenCode",              "command": {                "command": "opencode",                "args": ["acp"]              }            }          }        }      ]    }  }]
```

---

### [IDE JetBrains](#ide-jetbrains)

Добавьте в свою [JetBrains IDE](https://www.jetbrains.com/) acp.json в соответствии с [документацией](https://www.jetbrains.com/help/ai-assistant/acp.html):

acp.json

```
{  "agent_servers": {    "OpenCode": {      "command": "/absolute/path/bin/opencode",      "args": ["acp"]    }  }}
```

Чтобы открыть его, используйте новый агент opencode в селекторе агентов AI Chat.

---

### [Avante.nvim](#avantenvim)

Добавьте в свою конфигурацию [Avante.nvim](https://github.com/yetone/avante.nvim):

```
{  acp_providers = {    ["opencode"] = {      command = "opencode",      args = { "acp" }    }  }}
```

Если вам нужно передать переменные среды:

```
{  acp_providers = {    ["opencode"] = {      command = "opencode",      args = { "acp" },      env = {        OPENCODE_API_KEY = os.getenv("OPENCODE_API_KEY")      }    }  }}
```

---

### [CodeCompanion.nvim](#codecompanionnvim)

Чтобы использовать opencode в качестве агента ACP в [CodeCompanion.nvim](https://github.com/olimorris/codecompanion.nvim), добавьте в конфигурацию Neovim следующее:

```
require("codecompanion").setup({  interactions = {    chat = {      adapter = {        name = "opencode",        model = "claude-sonnet-4",      },    },  },})
```

Эта конфигурация настраивает CodeCompanion для использования opencode в качестве агента ACP для чата.

Если вам нужно передать переменные среды (например, `OPENCODE_API_KEY`), обратитесь к разделу [Настройка адаптеров: переменные среды](https://codecompanion.olimorris.dev/getting-started#setting-an-api-key) в документации CodeCompanion.nvim для получения полной информации.

## [Поддержка](#поддержка)

opencode через ACP работает так же, как и в терминале. Поддерживаются все функции:

Заметка

Некоторые встроенные команды слэша, такие как `/undo` и `/redo`, в настоящее время не поддерживаются.

-   Встроенные инструменты (файловые операции, команды терминала и т. д.)
-   Пользовательские инструменты и команды слэша
-   Серверы MCP, настроенные в вашей конфигурации opencode
-   Правила для конкретного проекта из `AGENTS.md`
-   Пользовательские форматтеры и линтеры
-   Агенты и система разрешений

[Редактировать страницу](https://github.com/anomalyco/opencode/edit/dev/packages/web/src/content/docs/ru/acp.mdx)[Found a bug? Open an issue](https://github.com/anomalyco/opencode/issues/new)[Join our Discord community](https://opencode.ai/discord) Выберите язык EnglishالعربيةBosanskiDanskDeutschEspañolFrançaisItaliano日本語한국어Norsk BokmålPolskiPortuguês (Brasil)РусскийไทยTürkçe简体中文繁體中文 

© [Anomaly](https://anoma.ly)

Последнее обновление: 30 мая 2026 г.
