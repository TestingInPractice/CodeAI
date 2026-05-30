CLI | OpenCode     [Перейти к содержимому](#_top)

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
    -   [tui](#tui)
-   [Команды](#команды)
    -   [agent](#agent)
    -   [attach](#attach)
    -   [auth](#auth)
    -   [github](#github)
    -   [mcp](#mcp)
    -   [models](#models)
    -   [run](#run-1)
    -   [serve](#serve)
    -   [session](#session)
    -   [stats](#stats)
    -   [export](#export)
    -   [import](#import)
    -   [web](#web)
    -   [acp](#acp)
    -   [uninstall](#uninstall)
    -   [upgrade](#upgrade)
-   [Глобальные флаги](#глобальные-флаги)
-   [Переменные среды](#переменные-среды)
    -   [Экспериментальные функции](#экспериментальные-функции)

## На этой странице

-   [Обзор](#_top)
    -   [tui](#tui)
-   [Команды](#команды)
    -   [agent](#agent)
    -   [attach](#attach)
    -   [auth](#auth)
    -   [github](#github)
    -   [mcp](#mcp)
    -   [models](#models)
    -   [run](#run-1)
    -   [serve](#serve)
    -   [session](#session)
    -   [stats](#stats)
    -   [export](#export)
    -   [import](#import)
    -   [web](#web)
    -   [acp](#acp)
    -   [uninstall](#uninstall)
    -   [upgrade](#upgrade)
-   [Глобальные флаги](#глобальные-флаги)
-   [Переменные среды](#переменные-среды)
    -   [Экспериментальные функции](#экспериментальные-функции)

# CLI

Параметры и команда opencode CLI.

CLI opencode по умолчанию запускает [TUI](/docs/tui) при запуске без каких-либо аргументов.

Окно терминала

```
opencode
```

Но он также принимает команды, описанные на этой странице. Это позволяет вам программно взаимодействовать с opencode.

Окно терминала

```
opencode run "Explain how closures work in JavaScript"
```

---

### [tui](#tui)

Запустите TUI opencode.

Окно терминала

```
opencode [project]
```

#### [Флаги](#флаги)

Флаг

Короткий

Описание

`--continue`

`-c`

Продолжить последний сеанс

`--session`

`-s`

Идентификатор сеанса для продолжения

`--fork`

Разветвить сеанс при продолжении (используйте с `--continue` или `--session`)

`--prompt`

Промпт для использования

`--model`

`-m`

Модель для использования в виде поставщика/модели.

`--agent`

Агент для использования

`--port`

Порт для прослушивания

`--hostname`

Имя хоста для прослушивания

---

## [Команды](#команды)

CLI opencode также имеет следующие команды.

---

### [agent](#agent)

Управляйте агентами для opencode.

Окно терминала

```
opencode agent [command]
```

---

### [attach](#attach)

Подключите терминал к уже работающему внутреннему серверу opencode, запущенному с помощью команд `serve` или `web`.

Окно терминала

```
opencode attach [url]
```

Это позволяет использовать TUI с удаленным сервером opencode. Например:

Окно терминала

```
# Start the backend server for web/mobile accessopencode web --port 4096 --hostname 0.0.0.0
# In another terminal, attach the TUI to the running backendopencode attach http://10.20.30.40:4096
```

#### [Флаги](#флаги-1)

Флаг

Короткий

Описание

`--dir`

Рабочий каталог для запуска TUI

`--continue`

`-c`

Продолжить последний сеанс

`--session`

`-s`

Идентификатор сеанса для продолжения

`--fork`

Создать ответвление сеанса при продолжении (используйте с `--continue` или `--session`)

`--password`

`-p`

Пароль базовой аутентификации (по умолчанию `OPENCODE_SERVER_PASSWORD`)

`--username`

`-u`

Имя пользователя базовой аутентификации (по умолчанию `OPENCODE_SERVER_USERNAME` или `opencode`)

---

#### [create](#create)

Создайте нового агента с пользовательской конфигурацией.

Окно терминала

```
opencode agent create
```

Эта команда поможет вам создать новый агент с настраиваемой системной подсказкой и настройкой инструмента.

---

#### [list](#list)

Перечислите всех доступных агентов.

Окно терминала

```
opencode agent list
```

---

### [auth](#auth)

Команда для управления учетными данными и входом в систему для провайдеров.

Окно терминала

```
opencode auth [command]
```

---

#### [login](#login)

opencode использует список провайдеров с [Models.dev](https://models.dev), поэтому вы можете использовать `opencode auth login` для настройки ключей API для любого поставщика, которого вы хотите использовать. Это хранится в `~/.local/share/opencode/auth.json`.

Окно терминала

```
opencode auth login
```

Когда opencode запускается, он загружает поставщиков из файла учетных данных. И если в ваших средах определены какие-либо ключи или файл `.env` в вашем проекте.

---

#### [list](#list-1)

Перечисляет всех проверенных поставщиков, которые хранятся в файле учетных данных.

Окно терминала

```
opencode auth list
```

Или короткая версия.

Окно терминала

```
opencode auth ls
```

---

#### [logout](#logout)

Выключает вас из провайдера, удаляя его из файла учетных данных.

Окно терминала

```
opencode auth logout
```

---

### [github](#github)

Управляйте агентом GitHub для автоматизации репозитория.

Окно терминала

```
opencode github [command]
```

---

#### [install](#install)

Установите агент GitHub в свой репозиторий.

Окно терминала

```
opencode github install
```

Это настроит необходимый рабочий процесс GitHub Actions и проведет вас через процесс настройки. [Подробнее](/docs/github).

---

#### [run](#run)

Запустите агент GitHub. Обычно это используется в действиях GitHub.

Окно терминала

```
opencode github run
```

##### [Флаги](#флаги-2)

Флаг

Описание

`--event`

Имитирующее событие GitHub для запуска агента

`--token`

Токен личного доступа GitHub

---

### [mcp](#mcp)

Управляйте серверами протокола контекста модели.

Окно терминала

```
opencode mcp [command]
```

---

#### [add](#add)

Добавьте сервер MCP в свою конфигурацию.

Окно терминала

```
opencode mcp add
```

Эта команда поможет вам добавить локальный или удаленный сервер MCP.

---

#### [list](#list-2)

Перечислите все настроенные серверы MCP и состояние их подключения.

Окно терминала

```
opencode mcp list
```

Или используйте короткую версию.

Окно терминала

```
opencode mcp ls
```

---

#### [auth](#auth-1)

Аутентификация с помощью сервера MCP с поддержкой OAuth.

Окно терминала

```
opencode mcp auth [name]
```

Если вы не укажете имя сервера, вам будет предложено выбрать один из доступных серверов с поддержкой OAuth.

Вы также можете перечислить серверы с поддержкой OAuth и их статус аутентификации.

Окно терминала

```
opencode mcp auth list
```

Или используйте короткую версию.

Окно терминала

```
opencode mcp auth ls
```

---

#### [logout](#logout-1)

Удалите учетные данные OAuth для сервера MCP.

Окно терминала

```
opencode mcp logout [name]
```

---

#### [debug](#debug)

Отладка проблем с подключением OAuth для сервера MCP.

Окно терминала

```
opencode mcp debug <name>
```

---

### [models](#models)

Перечислите все доступные модели от настроенных поставщиков.

Окно терминала

```
opencode models [provider]
```

Эта команда отображает все модели, доступные у настроенных вами поставщиков, в формате `provider/model`.

Это полезно для определения точного названия модели, которое будет использоваться в [вашем config](/docs/config/).

При желании вы можете передать идентификатор поставщика, чтобы фильтровать модели по этому поставщику.

Окно терминала

```
opencode models anthropic
```

#### [Флаги](#флаги-3)

Флаг

Описание

`--refresh`

Обновите кеш моделей на сайте models.dev.

`--verbose`

Используйте более подробный вывод модели (включая метаданные, такие как затраты).

Используйте флаг `--refresh` для обновления списка кэшированных моделей. Это полезно, когда к поставщику добавлены новые модели и вы хотите увидеть их в opencode.

Окно терминала

```
opencode models --refresh
```

---

### [run](#run-1)

Запустите opencode в неинтерактивном режиме, передав приглашение напрямую.

Окно терминала

```
opencode run [message..]
```

Это полезно для создания сценариев, автоматизации или когда вам нужен быстрый ответ без запуска полного TUI. Например.

Окно терминала

```
opencode run Explain the use of context in Go
```

Вы также можете подключиться к работающему экземпляру `opencode serve`, чтобы избежать холодной загрузки сервера MCP при каждом запуске:

Окно терминала

```
# Start a headless server in one terminalopencode serve
# In another terminal, run commands that attach to itopencode run --attach http://localhost:4096 "Explain async/await in JavaScript"
```

#### [Флаги](#флаги-4)

Флаг

Короткий

Описание

`--command`

Команда для запуска, используйте сообщение для аргументов

`--continue`

`-c`

Продолжить последний сеанс

`--session`

`-s`

Идентификатор сеанса для продолжения

`--fork`

Разветвить сеанс при продолжении (используйте с `--continue` или `--session`)

`--share`

Поделиться сеансом

`--model`

`-m`

Модель для использования в виде поставщика/модели.

`--agent`

Агент для использования

`--file`

`-f`

Файл(ы) для прикрепления к сообщению

`--format`

Формат: по умолчанию (отформатированный) или json (необработанные события JSON).

`--title`

Название сеанса (использует усеченное приглашение, если значение не указано)

`--attach`

Подключитесь к работающему серверу opencode (например, [http://localhost:4096](http://localhost:4096))

`--password`

`-p`

Пароль базовой аутентификации (по умолчанию `OPENCODE_SERVER_PASSWORD`)

`--username`

`-u`

Имя пользователя базовой аутентификации (по умолчанию `OPENCODE_SERVER_USERNAME` или `opencode`)

`--dir`

Каталог для выполнения или путь на удалённом сервере при подключении

`--variant`

Вариант модели (уровень рассуждений для провайдера)

`--thinking`

Показать блоки размышлений

`--port`

Порт локального сервера (по умолчанию случайный порт)

---

### [serve](#serve)

Запустите автономный сервер opencode для доступа к API. Полный HTTP-интерфейс можно найти в [server docs](/docs/server).

Окно терминала

```
opencode serve
```

При этом запускается HTTP-сервер, который обеспечивает доступ API к функциям opencode без интерфейса TUI. Установите `OPENCODE_SERVER_PASSWORD`, чтобы включить базовую аутентификацию HTTP (имя пользователя по умолчанию — `opencode`).

#### [Флаги](#флаги-5)

Флаг

Описание

`--port`

Порт для прослушивания

`--hostname`

Имя хоста для прослушивания

`--mdns`

Включить обнаружение mDNS

`--cors`

Дополнительные источники браузера, позволяющие разрешить CORS

---

### [session](#session)

Управляйте сессиями opencode.

Окно терминала

```
opencode session [command]
```

---

#### [list](#list-3)

Перечислите все сеансы opencode.

Окно терминала

```
opencode session list
```

##### [Флаги](#флаги-6)

Флаг

Короткий

Описание

`--max-count`

`-n`

Ограничить N последних сеансов.

`--format`

Формат вывода: таблица или json (таблица)

---

### [stats](#stats)

Покажите статистику использования токенов и затрат для ваших сеансов opencode.

Окно терминала

```
opencode stats
```

#### [Флаги](#флаги-7)

Флаг

Описание

`--days`

Показать статистику за последние N дней (все время)

`--tools`

Количество инструментов для отображения (все)

`--models`

Показать разбивку по использованию модели (по умолчанию скрыто). Передайте номер, чтобы показать верхнюю N

`--project`

Фильтровать по проекту (все проекты, пустая строка: текущий проект)

---

### [export](#export)

Экспортируйте данные сеанса в формате JSON.

Окно терминала

```
opencode export [sessionID]
```

Если вы не укажете идентификатор сеанса, вам будет предложено выбрать один из доступных сеансов.

---

### [import](#import)

Импортируйте данные сеанса из файла JSON или URL-адреса общего ресурса opencode.

Окно терминала

```
opencode import <file>
```

Вы можете импортировать из локального файла или URL-адреса общего ресурса opencode.

Окно терминала

```
opencode import session.jsonopencode import https://opncd.ai/s/abc123
```

---

### [web](#web)

Запустите автономный сервер opencode с веб-интерфейсом.

Окно терминала

```
opencode web
```

При этом запускается HTTP-сервер и открывается веб-браузер для доступа к opencode через веб-интерфейс. Установите `OPENCODE_SERVER_PASSWORD`, чтобы включить базовую аутентификацию HTTP (имя пользователя по умолчанию — `opencode`).

#### [Флаги](#флаги-8)

Флаг

Описание

`--port`

Порт для прослушивания

`--hostname`

Имя хоста для прослушивания

`--mdns`

Включить обнаружение mDNS

`--cors`

Дополнительные источники браузера, позволяющие разрешить CORS

---

### [acp](#acp)

Запустите сервер ACP (агент-клиентский протокол).

Окно терминала

```
opencode acp
```

Эта команда запускает сервер ACP, который обменивается данными через stdin/stdout с использованием nd-JSON.

#### [Флаги](#флаги-9)

Флаг

Описание

`--cwd`

Рабочий каталог

`--port`

Порт для прослушивания

`--hostname`

Имя хоста для прослушивания

---

### [uninstall](#uninstall)

Удалите opencode и удалите все связанные файлы.

Окно терминала

```
opencode uninstall
```

#### [Флаги](#флаги-10)

Флаг

Короткий

Описание

`--keep-config`

`-c`

Сохраняйте файлы конфигурации

`--keep-data`

`-d`

Храните данные сеанса и снимки

`--dry-run`

Покажите, что было бы удалено без удаления

`--force`

`-f`

Пропустить запросы подтверждения

---

### [upgrade](#upgrade)

Обновляет opencode до последней версии или определенной версии.

Окно терминала

```
opencode upgrade [target]
```

Чтобы обновиться до последней версии.

Окно терминала

```
opencode upgrade
```

Для обновления до определенной версии.

Окно терминала

```
opencode upgrade v0.1.48
```

#### [Флаги](#флаги-11)

Флаг

Короткий

Описание

`--method`

`-m`

Используемый метод установки: local, npm, pnpm, bun, brew

---

## [Глобальные флаги](#глобальные-флаги)

CLI opencode принимает следующие глобальные флаги.

Флаг

Короткий

Описание

`--help`

`-h`

Отобразить справку

`--version`

`-v`

Распечатать номер версии

`--print-logs`

Печать журналов в stderr

`--log-level`

Уровень журнала (DEBUG, INFO, WARN, ERROR)

---

## [Переменные среды](#переменные-среды)

opencode можно настроить с помощью переменных среды.

Переменная

Тип

Описание

`OPENCODE_AUTO_SHARE`

логическое значение

Автоматически делиться сеансами

`OPENCODE_GIT_BASH_PATH`

строка

Путь к исполняемому файлу Git Bash в Windows

`OPENCODE_CONFIG`

строка

Путь к файлу конфигурации

`OPENCODE_TUI_CONFIG`

строка

Путь к файлу конфигурации TUI

`OPENCODE_CONFIG_DIR`

строка

Путь к каталогу конфигурации

`OPENCODE_CONFIG_CONTENT`

строка

Встроенное содержимое конфигурации json

`OPENCODE_DISABLE_AUTOUPDATE`

логическое значение

Отключить автоматическую проверку обновлений

`OPENCODE_DISABLE_PRUNE`

логическое значение

Отключить удаление старых данных

`OPENCODE_DISABLE_TERMINAL_TITLE`

логическое значение

Отключить автоматическое обновление заголовка терминала

`OPENCODE_PERMISSION`

строка

Встроенная конфигурация разрешений json

`OPENCODE_DISABLE_DEFAULT_PLUGINS`

логическое значение

Отключить плагины по умолчанию

`OPENCODE_DISABLE_LSP_DOWNLOAD`

логическое значение

Отключить автоматическую загрузку LSP-сервера

`OPENCODE_ENABLE_EXPERIMENTAL_MODELS`

логическое значение

Включить экспериментальные модели

`OPENCODE_DISABLE_AUTOCOMPACT`

логическое значение

Отключить автоматическое сжатие контекста

`OPENCODE_DISABLE_CLAUDE_CODE`

логическое значение

Отключить чтение из `.claude` (подсказка + навыки)

`OPENCODE_DISABLE_CLAUDE_CODE_PROMPT`

логическое значение

Отключить чтение `~/.claude/CLAUDE.md`

`OPENCODE_DISABLE_CLAUDE_CODE_SKILLS`

логическое значение

Отключить загрузку `.claude/skills`

`OPENCODE_DISABLE_MODELS_FETCH`

логическое значение

Отключить получение моделей из удаленных источников

`OPENCODE_FAKE_VCS`

строка

Поддельный поставщик VCS для целей тестирования

`OPENCODE_CLIENT`

строка

Идентификатор клиента (по умолчанию `cli`)

`OPENCODE_ENABLE_EXA`

логическое значение

Включить инструменты веб-поиска Exa

`OPENCODE_SERVER_PASSWORD`

строка

Включить базовую аутентификацию для `serve`/`web`

`OPENCODE_SERVER_USERNAME`

строка

Переопределить имя пользователя базовой аутентификации (по умолчанию `opencode`)

`OPENCODE_MODELS_URL`

строка

Пользовательский URL-адрес для получения конфигурации модели

---

### [Экспериментальные функции](#экспериментальные-функции)

Эти переменные среды позволяют использовать экспериментальные функции, которые могут быть изменены или удалены.

Переменная

Тип

Описание

`OPENCODE_EXPERIMENTAL`

логическое значение

Включить экспериментальные функции под общим флагом

`OPENCODE_EXPERIMENTAL_ICON_DISCOVERY`

логическое значение

Включить обнаружение значков

`OPENCODE_EXPERIMENTAL_DISABLE_COPY_ON_SELECT`

логическое значение

Отключить копирование при выборе в TUI

`OPENCODE_EXPERIMENTAL_BASH_DEFAULT_TIMEOUT_MS`

число

Таймаут по умолчанию для команд bash в мс

`OPENCODE_EXPERIMENTAL_OUTPUT_TOKEN_MAX`

число

Максимальное количество токенов вывода для ответов LLM

`OPENCODE_EXPERIMENTAL_FILEWATCHER`

логическое значение

Включить просмотр файлов для всего каталога

`OPENCODE_EXPERIMENTAL_OXFMT`

логическое значение

Включить форматтер oxfmt

`OPENCODE_EXPERIMENTAL_LSP_TOOL`

логическое значение

Включить экспериментальный инструмент LSP

`OPENCODE_EXPERIMENTAL_DISABLE_FILEWATCHER`

логическое значение

Отключить просмотрщик файлов

`OPENCODE_EXPERIMENTAL_EXA`

логическое значение

Включить экспериментальные функции Exa

`OPENCODE_EXPERIMENTAL_LSP_TY`

логическое значение

Включить TY LSP для файлов python

`OPENCODE_EXPERIMENTAL_PLAN_MODE`

логическое значение

Включить режим плана

`OPENCODE_EXPERIMENTAL_BACKGROUND_SUBAGENTS`

логическое значение

Включить фоновые задачи субагентов

`OPENCODE_EXPERIMENTAL_EVENT_SYSTEM`

логическое значение

Включить экспериментальную систему событий

`OPENCODE_EXPERIMENTAL_NATIVE_LLM`

логическое значение

Включить нативный путь запросов LLM

`OPENCODE_EXPERIMENTAL_PARALLEL`

логическое значение

Включить параллельное выполнение веб-поиска

`OPENCODE_EXPERIMENTAL_SCOUT`

логическое значение

Включить субагент Scout

`OPENCODE_EXPERIMENTAL_WORKSPACES`

логическое значение

Включить поддержку рабочих областей

[Редактировать страницу](https://github.com/anomalyco/opencode/edit/dev/packages/web/src/content/docs/ru/cli.mdx)[Found a bug? Open an issue](https://github.com/anomalyco/opencode/issues/new)[Join our Discord community](https://opencode.ai/discord) Выберите язык EnglishالعربيةBosanskiDanskDeutschEspañolFrançaisItaliano日本語한국어Norsk BokmålPolskiPortuguês (Brasil)РусскийไทยTürkçe简体中文繁體中文 

© [Anomaly](https://anoma.ly)

Последнее обновление: 30 мая 2026 г.
