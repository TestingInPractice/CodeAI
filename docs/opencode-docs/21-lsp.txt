LSP-серверы | OpenCode     [Перейти к содержимому](#_top)

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
-   [Как это работает](#как-это-работает)
-   [Рекомендации](#рекомендации)
-   [Настройка](#настройка)
    -   [Переменные среды](#переменные-среды)
    -   [Параметры инициализации](#параметры-инициализации)
    -   [Отключение LSP-серверов](#отключение-lsp-серверов)
    -   [Пользовательские LSP-серверы](#пользовательские-lsp-серверы)
-   [Дополнительная информация](#дополнительная-информация)
    -   [PHP Intelephense](#php-intelephense)

## На этой странице

-   [Обзор](#_top)
-   [Встроенные](#встроенные)
-   [Как это работает](#как-это-работает)
-   [Рекомендации](#рекомендации)
-   [Настройка](#настройка)
    -   [Переменные среды](#переменные-среды)
    -   [Параметры инициализации](#параметры-инициализации)
    -   [Отключение LSP-серверов](#отключение-lsp-серверов)
    -   [Пользовательские LSP-серверы](#пользовательские-lsp-серверы)
-   [Дополнительная информация](#дополнительная-информация)
    -   [PHP Intelephense](#php-intelephense)

# LSP-серверы

opencode интегрируется с вашими серверами LSP.

opencode может интегрироваться с серверами Language Server Protocol (LSP), чтобы использовать диагностику как обратную связь для агента.

---

## [Встроенные](#встроенные)

opencode поставляется с несколькими встроенными LSP-серверами для популярных языков:

LSP Server

Extensions

Requirements

astro

.astro

Автоматически устанавливается для проектов Astro

bash

.sh, .bash, .zsh, .ksh

Автоматически устанавливает bash-language-server

clangd

.c, .cpp, .cc, .cxx, .c++, .h, .hpp, .hh, .hxx, .h++

Автоматически устанавливается для проектов C/C++

csharp

.cs

`.NET SDK` установлен

clojure-lsp

.clj, .cljs, .cljc, .edn

`clojure-lsp` команда доступна

dart

.dart

`dart` команда доступна

deno

.ts, .tsx, .js, .jsx, .mjs

`deno` команда доступна (автоматически обнаруживает deno.json/deno.jsonc)

elixir-ls

.ex, .exs

`elixir` команда доступна

eslint

.ts, .tsx, .js, .jsx, .mjs, .cjs, .mts, .cts, .vue

`eslint` зависимость в проекте

fsharp

.fs, .fsi, .fsx, .fsscript

`.NET SDK` установлен

gleam

.gleam

`gleam` команда доступна

gopls

.go

`go` команда доступна

hls

.hs, .lhs

`haskell-language-server-wrapper` команда доступна

jdtls

.java

`Java SDK (version 21+)` установлен

kotlin-ls

.kt, .kts

Автоматически устанавливается для проектов Kotlin

lua-ls

.lua

Автоматически устанавливается для проектов Lua

nixd

.nix

`nixd` команда доступна

ocaml-lsp

.ml, .mli

`ocamllsp` команда доступна

oxlint

.ts, .tsx, .js, .jsx, .mjs, .cjs, .mts, .cts, .vue, .astro, .svelte

`oxlint` зависимость в проекте

php intelephense

.php

Автоматически устанавливается для проектов PHP

prisma

.prisma

`prisma` команда доступна

pyright

.py, .pyi

`pyright` зависимость установлена

ruby-lsp (rubocop)

.rb, .rake, .gemspec, .ru

`ruby` и `gem` команды доступны

rust

.rs

`rust-analyzer` команда доступна

sourcekit-lsp

.swift, .objc, .objcpp

`swift` установлен (`xcode` на macOS)

svelte

.svelte

Автоматически устанавливается для проектов Svelte

terraform

.tf, .tfvars

Автоматически устанавливается из релизов GitHub

tinymist

.typ, .typc

Автоматически устанавливается из релизов GitHub

typescript

.ts, .tsx, .js, .jsx, .mjs, .cjs, .mts, .cts

`typescript` зависимость в проекте

vue

.vue

Автоматически устанавливается для проектов Vue

yaml-ls

.yaml, .yml

Автоматически устанавливает Red Hat yaml-language-server

zls

.zig, .zon

`zig` команда доступна

LSP отключен по умолчанию. Когда он включен, серверы запускаются при обнаружении одного из указанных выше расширений файлов и выполнении требований.

Заметка

Вы можете отключить автоматическую загрузку LSP-сервера, установив для переменной среды `OPENCODE_DISABLE_LSP_DOWNLOAD` значение `true`.

---

## [Как это работает](#как-это-работает)

Когда LSP включен и opencode открывает файл, он:

1.  Проверяет расширение файла на всех включенных серверах LSP.
2.  Запускает соответствующий сервер LSP, если он еще не запущен.

---

## [Рекомендации](#рекомендации)

LSP может помочь агенту находить и исправлять проблемы, предоставляя диагностику от языковых серверов. Это полезно в некоторых проектах, но не всегда является однозначным преимуществом.

Языковые серверы могут рассинхронизироваться, потреблять много памяти, отличаться по поведению между версиями или проектами и замедлять рабочие процессы агента. Во многих проектах лучше, чтобы агент напрямую запускал lint, typecheck или другие диагностические CLI-инструменты; так ошибки возвращаются в цикл агента без этих компромиссов. Задокументируйте эти команды в файлах инструкций, например `AGENTS.md` или skills, чтобы агент знал, что запускать. Включайте LSP, когда проект получает пользу от дополнительной обратной связи языкового сервера.

---

## [Настройка](#настройка)

Вы можете включить и настроить серверы LSP через раздел `lsp` в конфигурации opencode.

Чтобы включить все встроенные LSP-серверы, установите `lsp` в `true`.

opencode.json

```
{  "$schema": "https://opencode.ai/config.json",  "lsp": true}
```

Используйте объект, чтобы оставить встроенные серверы включенными и при этом настроить переопределения или пользовательские серверы.

opencode.json

```
{  "$schema": "https://opencode.ai/config.json",  "lsp": {}}
```

Каждый LSP-сервер поддерживает следующее:

Свойство

Тип

Описание

`disabled`

boolean

Установите для этого параметра значение `true`, чтобы отключить сервер LSP.

`command`

string\[\]

Команда запуска LSP-сервера

`extensions`

string\[\]

Расширения файлов, которые должен обрабатывать этот сервер LSP

`env`

object

Переменные среды, которые нужно установить при запуске сервера

`initialization`

object

Параметры инициализации для отправки на сервер LSP

Давайте посмотрим на несколько примеров.

---

### [Переменные среды](#переменные-среды)

Используйте свойство `env` для установки переменных среды при запуске сервера LSP:

opencode.json

```
{  "$schema": "https://opencode.ai/config.json",  "lsp": {    "rust": {      "env": {        "RUST_LOG": "debug"      }    }  }}
```

---

### [Параметры инициализации](#параметры-инициализации)

Используйте свойство `initialization` для передачи параметров инициализации на LSP-сервер. Это настройки, специфичные для сервера, отправляемые во время запроса LSP `initialize`:

opencode.json

```
{  "$schema": "https://opencode.ai/config.json",  "lsp": {    "typescript": {      "initialization": {        "preferences": {          "importModuleSpecifierPreference": "relative"        }      }    }  }}
```

Заметка

Параметры инициализации зависят от сервера LSP. Проверьте документацию вашего LSP-сервера на наличие доступных опций.

---

### [Отключение LSP-серверов](#отключение-lsp-серверов)

Если `lsp` не указан, все LSP-серверы отключены. Чтобы отключить все LSP-серверы после того, как другая конфигурация их включила, установите для `lsp` значение `false`:

opencode.json

```
{  "$schema": "https://opencode.ai/config.json",  "lsp": false}
```

Чтобы отключить **конкретный** LSP-сервер, установите для `disabled` значение `true`:

opencode.json

```
{  "$schema": "https://opencode.ai/config.json",  "lsp": {    "typescript": {      "disabled": true    }  }}
```

---

### [Пользовательские LSP-серверы](#пользовательские-lsp-серверы)

Вы можете добавить собственные LSP-серверы, указав команду и расширения файлов:

opencode.json

```
{  "$schema": "https://opencode.ai/config.json",  "lsp": {    "custom-lsp": {      "command": ["custom-lsp-server", "--stdio"],      "extensions": [".custom"]    }  }}
```

---

## [Дополнительная информация](#дополнительная-информация)

### [PHP Intelephense](#php-intelephense)

PHP Intelephense предлагает дополнительные функции через лицензионный ключ. Вы можете предоставить лицензионный ключ, поместив (только) ключ в текстовый файл по адресу:

-   В macOS/Linux: `$HOME/intelephense/license.txt`
-   В Windows: `%USERPROFILE%/intelephense/license.txt`

Файл должен содержать только лицензионный ключ без какого-либо дополнительного содержимого.

[Редактировать страницу](https://github.com/anomalyco/opencode/edit/dev/packages/web/src/content/docs/ru/lsp.mdx)[Found a bug? Open an issue](https://github.com/anomalyco/opencode/issues/new)[Join our Discord community](https://opencode.ai/discord) Выберите язык EnglishالعربيةBosanskiDanskDeutschEspañolFrançaisItaliano日本語한국어Norsk BokmålPolskiPortuguês (Brasil)РусскийไทยTürkçe简体中文繁體中文 

© [Anomaly](https://anoma.ly)

Последнее обновление: 30 мая 2026 г.
