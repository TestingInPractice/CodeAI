Policies | OpenCode     [Перейти к содержимому](#_top)

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
-   [Configuration](#configuration)
-   [Available Policies](#available-policies)
-   [Matching](#matching)
-   [Rule Order](#rule-order)
-   [Provider Lists](#provider-lists)

## На этой странице

-   [Обзор](#_top)
-   [Configuration](#configuration)
-   [Available Policies](#available-policies)
-   [Matching](#matching)
-   [Rule Order](#rule-order)
-   [Provider Lists](#provider-lists)

# Policies

Control which configured resources OpenCode may use.

Это содержимое пока не доступно на вашем языке.

Policies control whether OpenCode may perform an action on a named resource. This feature is experimental and is configured with the `experimental.policies` array in `opencode.json`.

Policies are separate from [permissions](/docs/permissions). Permissions control what tools can do during a session, while policies control whether OpenCode may use a resource such as an LLM provider.

---

## [Configuration](#configuration)

Each policy statement has three fields:

-   `effect` - Either `"allow"` or `"deny"`.
-   `action` - The operation being controlled.
-   `resource` - The resource ID or wildcard pattern the statement applies to.

For example, deny use of the `openai` provider:

opencode.json

```
{  "$schema": "https://opencode.ai/config.json",  "experimental": {    "policies": [      {        "effect": "deny",        "action": "provider.use",        "resource": "openai"      }    ]  }}
```

A provider denied by policy is not available for model selection or model use, even if it has credentials or is otherwise configured correctly.

---

## [Available Policies](#available-policies)

OpenCode currently supports one policy action:

Action

Resource

Description

`provider.use`

Provider ID, such as `openai`

Allow or deny use of an LLM provider.

More policy actions may be added in the future.

---

## [Matching](#matching)

The `resource` field supports wildcard matching. Use `*` to match zero or more characters and `?` to match one character.

opencode.json

```
{  "$schema": "https://opencode.ai/config.json",  "experimental": {    "policies": [      {        "effect": "deny",        "action": "provider.use",        "resource": "company-*"      }    ]  }}
```

This denies providers such as `company-us` and `company-eu`.

---

## [Rule Order](#rule-order)

When multiple statements match, the last matching statement wins. Put broad rules first, then more specific exceptions after them.

For example, allow only Anthropic:

opencode.json

```
{  "$schema": "https://opencode.ai/config.json",  "experimental": {    "policies": [      {        "effect": "deny",        "action": "provider.use",        "resource": "*"      },      {        "effect": "allow",        "action": "provider.use",        "resource": "anthropic"      }    ]  }}
```

If no policy matches a provider, provider use is allowed by default.

Policies may be set in both your global config and project config. If policies from both locations match the same provider, your global policy takes priority over the project policy. This prevents a repository from re-enabling a provider that you deny globally.

---

## [Provider Lists](#provider-lists)

Use policies instead of the older `disabled_providers` and `enabled_providers` settings when controlling provider access.

To replace `disabled_providers`:

opencode.json

```
{  "experimental": {    "policies": [      { "effect": "deny", "action": "provider.use", "resource": "openai" },      { "effect": "deny", "action": "provider.use", "resource": "google" }    ]  }}
```

To replace `enabled_providers`, deny all providers first and allow the selected providers after it:

opencode.json

```
{  "experimental": {    "policies": [      { "effect": "deny", "action": "provider.use", "resource": "*" },      { "effect": "allow", "action": "provider.use", "resource": "anthropic" },      { "effect": "allow", "action": "provider.use", "resource": "openai" }    ]  }}
```

[Редактировать страницу](https://github.com/anomalyco/opencode/edit/dev/packages/web/src/content/docs/policies.mdx)[Found a bug? Open an issue](https://github.com/anomalyco/opencode/issues/new)[Join our Discord community](https://opencode.ai/discord) Выберите язык EnglishالعربيةBosanskiDanskDeutschEspañolFrançaisItaliano日本語한국어Norsk BokmålPolskiPortuguês (Brasil)РусскийไทยTürkçe简体中文繁體中文 

© [Anomaly](https://anoma.ly)

Последнее обновление: 30 мая 2026 г.
