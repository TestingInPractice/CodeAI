Форматтеры | OpenCode     [Перейти к содержимому](#_top)

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
-   [Встроенные](#встроенные)
-   [Настройка](#настройка)
    -   [Отключение форматтеров](#отключение-форматтеров)
    -   [Пользовательские форматтеры](#пользовательские-форматтеры)

## На этой странице

-   [Обзор](#_top)
-   [Встроенные](#встроенные)
-   [Настройка](#настройка)
    -   [Отключение форматтеров](#отключение-форматтеров)
    -   [Пользовательские форматтеры](#пользовательские-форматтеры)

# Форматтеры

opencode использует средства форматирования, специфичные для языка.

opencode автоматически форматирует файлы после их записи или редактирования с использованием средств форматирования для конкретного языка. Это гарантирует, что создаваемый код будет соответствовать стилям кода вашего проекта.

---

## [Встроенные](#встроенные)

opencode поставляется с несколькими встроенными форматировщиками для популярных языков и платформ. Ниже приведен список форматтеров, поддерживаемых расширений файлов, а также необходимых команд или параметров конфигурации.

Formatter

Расширения

Требования

gofmt

.go

Доступна команда `gofmt`

mix

.ex, .exs, .eex, .heex, .leex, .neex, .sface

Доступна команда `mix`

prettier

.js, .jsx, .ts, .tsx, .html, .css, .md, .json, .yaml и [подробнее](https://prettier.io/docs/en/index.html)

Зависимость `prettier` в `package.json`

biome

.js, .jsx, .ts, .tsx, .html, .css, .md, .json, .yaml и [подробнее](https://biomejs.dev/)

Конфигурационный файл `biome.json(c)`

zig

.zig, .zon

Доступна команда `zig`

clang-format

.c, .cpp, .h, .hpp, .ino и [подробнее](https://clang.llvm.org/docs/ClangFormat.html)

Конфигурационный файл `.clang-format`

ktlint

.kt, .kts

Доступна команда `ktlint`

ruff

.py, .pyi

Команда `ruff` доступна в конфигурации

rustfmt

.rs

Доступна команда `rustfmt`

cargofmt

.rs

Доступна команда `cargo fmt`

uv

.py, .pyi

Доступна команда `uv`

rubocop

.rb, .rake, .gemspec, .ru

Доступна команда `rubocop`

standardrb

.rb, .rake, .gemspec, .ru

Доступна команда `standardrb`

htmlbeautifier

.erb, .html.erb

Доступна команда `htmlbeautifier`

air

.R

Доступна команда `air`

dart

.dart

Доступна команда `dart`

dfmt

.d

Доступна команда `dfmt`

ocamlformat

.ml, .mli

Доступна команда `ocamlformat` и файл конфигурации `.ocamlformat`.

terraform

.tf, .tfvars

Доступна команда `terraform`

gleam

.gleam

Доступна команда `gleam`

nixfmt

.nix

Доступна команда `nixfmt`

shfmt

.sh, .bash

Доступна команда `shfmt`

pint

.php

Зависимость `laravel/pint` в `composer.json`

oxfmt (Experimental)

.js, .jsx, .ts, .tsx

Зависимость `oxfmt` в `package.json` и [экспериментальный флаг переменной окружения](/docs/cli/#experimental)

ormolu

.hs

Доступна команда `ormolu`

Поэтому, если ваш проект имеет `prettier` в вашем `package.json`, opencode автоматически будет использовать его.

---

## [Настройка](#настройка)

Вы можете настроить форматтеры через раздел `formatter` в конфигурации opencode.

opencode.json

```
{  "$schema": "https://opencode.ai/config.json",  "formatter": {}}
```

Каждая конфигурация форматтера поддерживает следующее:

Свойство

Тип

Описание

`disabled`

boolean

Установите для этого параметра значение `true`, чтобы отключить форматтер.

`command`

string\[\]

Команда для форматирования

`environment`

объект

Переменные среды, которые необходимо установить при запуске средства форматирования

`extensions`

string\[\]

Расширения файлов, которые должен обрабатывать этот форматтер

Давайте посмотрим на несколько примеров.

---

### [Отключение форматтеров](#отключение-форматтеров)

Чтобы глобально отключить **все** средства форматирования, установите для `formatter` значение `false`:

opencode.json

```
{  "$schema": "https://opencode.ai/config.json",  "formatter": false}
```

Чтобы отключить **конкретный** форматтер, установите для `disabled` значение `true`:

opencode.json

```
{  "$schema": "https://opencode.ai/config.json",  "formatter": {    "prettier": {      "disabled": true    }  }}
```

---

### [Пользовательские форматтеры](#пользовательские-форматтеры)

Вы можете переопределить встроенные средства форматирования или добавить новые, указав команду, переменные среды и расширения файлов:

opencode.json

```
{  "$schema": "https://opencode.ai/config.json",  "formatter": {    "prettier": {      "command": ["npx", "prettier", "--write", "$FILE"],      "environment": {        "NODE_ENV": "development"      },      "extensions": [".js", ".ts", ".jsx", ".tsx"]    },    "custom-markdown-formatter": {      "command": ["deno", "fmt", "$FILE"],      "extensions": [".md"]    }  }}
```

Заполнитель **`$FILE`** в команде будет заменен путем к форматируемому файлу.

[Редактировать страницу](https://github.com/anomalyco/opencode/edit/dev/packages/web/src/content/docs/ru/formatters.mdx)[Found a bug? Open an issue](https://github.com/anomalyco/opencode/issues/new)[Join our Discord community](https://opencode.ai/discord) Выберите язык EnglishالعربيةBosanskiDanskDeutschEspañolFrançaisItaliano日本語한국어Norsk BokmålPolskiPortuguês (Brasil)РусскийไทยTürkçe简体中文繁體中文 

© [Anomaly](https://anoma.ly)

Последнее обновление: 30 мая 2026 г.
