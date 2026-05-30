TUI | OpenCode     [Перейти к содержимому](#_top)

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
-   [Ссылки на файлы](#ссылки-на-файлы)
-   [Bash-команды](#bash-команды)
-   [Команды](#команды)
    -   [connect](#connect)
    -   [compact](#compact)
    -   [details](#details)
    -   [editor](#editor)
    -   [exit](#exit)
    -   [export](#export)
    -   [help](#help)
    -   [init](#init)
    -   [models](#models)
    -   [new](#new)
    -   [redo](#redo)
    -   [sessions](#sessions)
    -   [share](#share)
    -   [theme](#theme)
    -   [thinking](#thinking)
    -   [undo](#undo)
    -   [unshare](#unshare)
-   [Настройка редактора](#настройка-редактора)
-   [Настройка](#настройка)
    -   [Параметры](#параметры)
    -   [Attention](#attention)
-   [Кастомизация](#кастомизация)

## На этой странице

-   [Обзор](#_top)
-   [Ссылки на файлы](#ссылки-на-файлы)
-   [Bash-команды](#bash-команды)
-   [Команды](#команды)
    -   [connect](#connect)
    -   [compact](#compact)
    -   [details](#details)
    -   [editor](#editor)
    -   [exit](#exit)
    -   [export](#export)
    -   [help](#help)
    -   [init](#init)
    -   [models](#models)
    -   [new](#new)
    -   [redo](#redo)
    -   [sessions](#sessions)
    -   [share](#share)
    -   [theme](#theme)
    -   [thinking](#thinking)
    -   [undo](#undo)
    -   [unshare](#unshare)
-   [Настройка редактора](#настройка-редактора)
-   [Настройка](#настройка)
    -   [Параметры](#параметры)
    -   [Attention](#attention)
-   [Кастомизация](#кастомизация)

# TUI

Использование TUI opencode.

opencode предоставляет интерактивный terminal интерфейс или TUI для работы над вашими проектами с помощью LLM.

Запуск opencode запускает TUI для текущего каталога.

Окно терминала

```
opencode
```

Или вы можете запустить его для определенного рабочего каталога.

Окно терминала

```
opencode /path/to/project
```

Как только вы окажетесь в TUI, вы можете запросить его с помощью сообщения.

```
Give me a quick summary of the codebase.
```

---

## [Ссылки на файлы](#ссылки-на-файлы)

Вы можете ссылаться на файлы в своих сообщениях, используя `@`. Это выполняет нечеткий поиск файлов в текущем рабочем каталоге.

Совет

Вы также можете использовать `@` для ссылки на файлы в своих сообщениях.

```
How is auth handled in @packages/functions/src/api/index.ts?
```

Содержимое файла добавляется в беседу автоматически.

---

## [Bash-команды](#bash-команды)

Начните сообщение с `!`, чтобы запустить shell-команду.

```
!ls -la
```

Вывод команды добавляется в диалог как результат работы инструмента.

---

## [Команды](#команды)

При использовании opencode TUI вы можете ввести `/`, а затем имя команды, чтобы быстро выполнить действия. Например:

```
/help
```

Большинство команд также имеют привязку клавиш с использованием `ctrl+x` в качестве ведущей клавиши, где `ctrl+x` — это ведущая клавиша по умолчанию. [Подробнее](/docs/keybinds) .

Вот все доступные слэш-команды:

---

### [connect](#connect)

Добавьте провайдера в opencode. Позволяет выбирать из доступных поставщиков и добавлять их ключи API.

```
/connect
```

---

### [compact](#compact)

Сжать текущий сеанс. *Псевдоним*: `/summarize`

```
/compact
```

**Привязка клавиш:** `ctrl+x c`

---

### [details](#details)

Переключить детали выполнения инструмента.

```
/details
```

**Привязка клавиш:** `ctrl+x d`

---

### [editor](#editor)

Открыть внешний редактор для составления сообщений. Использует редактор, установленный в переменной среды `EDITOR`. [Подробнее](#editor-setup) .

```
/editor
```

**Привязка клавиш:** `ctrl+x e`

---

### [exit](#exit)

Выйдите из opencode. *Псевдонимы*: `/quit`, `/q`

```
/exit
```

**Привязка клавиш:** `ctrl+x q`

---

### [export](#export)

Экспортируйте текущий разговор в Markdown и откройте его в редакторе по умолчанию. Использует редактор, установленный в переменной среды `EDITOR`. [Подробнее](#editor-setup) .

```
/export
```

**Привязка клавиш:** `ctrl+x x`

---

### [help](#help)

Показать диалоговое окно помощи.

```
/help
```

**Привязка клавиш:** `ctrl+x h`

---

### [init](#init)

Создайте или обновите файл `AGENTS.md`. [Подробнее](/docs/rules) .

```
/init
```

**Привязка клавиш:** `ctrl+x i`

---

### [models](#models)

Перечислите доступные модели.

```
/models
```

**Привязка клавиш:** `ctrl+x m`

---

### [new](#new)

Начать новый сеанс. *Псевдоним*: `/clear`

```
/new
```

**Привязка клавиш:** `ctrl+x n`

---

### [redo](#redo)

Повторить ранее отмененное сообщение. Доступно только после использования `/undo`.

Совет

Любые изменения файлов также будут восстановлены.

Внутри это использует Git для управления изменениями файлов. Итак, ваш проект \*\* должен быть репозиторием Git\*\*.

```
/redo
```

**Привязка клавиш:** `ctrl+x r`

---

### [sessions](#sessions)

Составляйте список и переключайтесь между сеансами. *Псевдонимы*: `/resume`, `/continue`

```
/sessions
```

**Привязка клавиш:** `ctrl+x l`

---

### [share](#share)

Поделиться текущим сеансом. [Подробнее](/docs/share).

```
/share
```

**Привязка клавиш:** `ctrl+x s`

---

### [theme](#theme)

Список доступных тем.

```
/theme
```

**Привязка клавиш:** `ctrl+x t`

---

### [thinking](#thinking)

Переключить видимость блоков мышления/рассуждения в разговоре. Если этот параметр включен, вы можете увидеть процесс рассуждения модели для моделей, поддерживающих расширенное мышление.

Заметка

Эта команда только контролирует, будут ли **отображаться** блоки мышления, но не включает и не отключает возможности модели по рассуждению. Чтобы переключить фактические возможности рассуждения, используйте `ctrl+t` для циклического переключения вариантов модели.

```
/thinking
```

---

### [undo](#undo)

Отменить последнее сообщение в разговоре. Удаляет самое последнее сообщение пользователя, все последующие ответы и любые изменения файлов.

Совет

Любые внесенные изменения в файле также будут отменены.

Внутри это использует Git для управления изменениями файлов. Итак, ваш проект \*\* должен быть репозиторием Git\*\*.

```
/undo
```

**Привязка клавиш:** `ctrl+x u`

---

### [unshare](#unshare)

Отменить общий доступ к текущему сеансу. [Подробнее](/docs/share#un-sharing).

```
/unshare
```

---

## [Настройка редактора](#настройка-редактора)

Команды `/editor` и `/export` используют редактор, указанный в переменной среды `EDITOR`.

-   [Linux/macOS](#tab-panel-88)
-   [Windows (CMD)](#tab-panel-89)
-   [Windows (PowerShell)](#tab-panel-90)

Окно терминала

```
# Example for nano or vimexport EDITOR=nanoexport EDITOR=vim
# For GUI editors, VS Code, Cursor, VSCodium, Windsurf, Zed, etc.# include --waitexport EDITOR="code --wait"
```

Чтобы сделать его постоянным, добавьте это в свой профиль shell; `~/.bashrc`, `~/.zshrc` и т. д.

Окно терминала

```
set EDITOR=notepad
# For GUI editors, VS Code, Cursor, VSCodium, Windsurf, Zed, etc.# include --waitset EDITOR=code --wait
```

Чтобы сделать его постоянным, используйте **Свойства системы** > **Среда Переменные**.

Окно терминала

```
$env:EDITOR = "notepad"
# For GUI editors, VS Code, Cursor, VSCodium, Windsurf, Zed, etc.# include --wait$env:EDITOR = "code --wait"
```

Чтобы сделать его постоянным, добавьте его в свой профиль PowerShell.

Популярные варианты редактора включают в себя:

-   `code` — VS Code
-   `cursor` — Cursor
-   `windsurf` - Windsurf
-   `nvim` - Редактор Neovim
-   `vim` — редактор Vim
-   `nano` — Нано-редактор
-   `notepad` — Блокнот Windows
-   `subl` — Sublime Text

Заметка

Некоторые редакторы, такие как VS Code, необходимо запускать с флагом `--wait`.

Некоторым редакторам для работы в режиме блокировки необходимы CLI-аргументы. Флаг `--wait` блокирует процесс редактора до его закрытия.

---

## [Настройка](#настройка)

Вы можете настроить поведение TUI через `tui.json` (или `tui.jsonc`).

tui.json

```
{  "$schema": "https://opencode.ai/tui.json",  "theme": "opencode",  "leader_timeout": 2000,  "keybinds": {    "leader": "ctrl+x",    "command_list": "ctrl+p"  },  "scroll_speed": 3,  "scroll_acceleration": {    "enabled": false  },  "diff_style": "auto",  "mouse": true,  "attention": {    "enabled": true,    "notifications": true,    "sound": true,    "volume": 0.4,    "sound_pack": "opencode.default",    "sounds": {      "error": "./sounds/error.mp3"    }  }}
```

Это отдельный файл от `opencode.json`, который настраивает поведение сервера/выполнения.

`keybinds` объединяется со встроенными значениями по умолчанию, поэтому достаточно настроить только те сочетания клавиш, которые вы хотите изменить.

### [Параметры](#параметры)

-   `theme` — Устанавливает тему пользовательского интерфейса. [Подробнее](/docs/themes).
-   `keybinds` — Настраивает сочетания клавиш. [Подробнее](/docs/keybinds).
-   `leader_timeout` — Управляет тем, как долго OpenCode ждёт после нажатия leader key. По умолчанию `2000`.
-   `scroll_acceleration.enabled` — включите ускорение прокрутки в стиле macOS для плавной и естественной прокрутки. Если этот параметр включен, скорость прокрутки увеличивается при быстрой прокрутке и остается точной при более медленных движениях. **Этот параметр имеет приоритет над `scroll_speed` и переопределяет его, если он включен.**
-   `scroll_speed` — контролирует скорость прокрутки TUI при использовании команд прокрутки (минимум: `0.001`, поддерживает десятичные значения). По умолчанию `3`. **Примечание. Это игнорируется, если для `scroll_acceleration.enabled` установлено значение `true`.**
-   `diff_style` — Управляет отображением различий. `"auto"` адаптируется к ширине терминала, `"stacked"` всегда показывает одноколоночный макет.
-   `mouse` — Включает или отключает захват мыши в TUI (по умолчанию `true`). Если отключено, сохраняется нативное поведение терминала для выделения мышью и прокрутки.
-   `attention` — Настраивает уведомления рабочего стола и звуки TUI. По умолчанию отключено.

Используйте `OPENCODE_TUI_CONFIG` для загрузки пользовательского пути конфигурации TUI.

### [Attention](#attention)

Attention позволяет TUI уведомлять вас, когда OpenCode ждёт ответа, требует подтверждения разрешения, сообщает об ошибке сеанса или завершает сеанс. Включите это с помощью `attention.enabled`; встроенные события воспроизводят звук при срабатывании. Уведомления рабочего стола отправляются только тогда, когда окно терминала не в фокусе, и не используются для событий subagent.

-   `enabled` — Включает все уведомления и звуки Attention. По умолчанию `false`.
-   `notifications` — Когда Attention включён, разрешает TUI отправлять уведомления рабочего стола через терминал. По умолчанию `true`.
-   `sound` — Когда Attention включён, разрешает воспроизводить звуковые оповещения. По умолчанию `true`.
-   `volume` — Громкость звуковых оповещений по умолчанию от `0` до `1`. По умолчанию `0.4`.
-   `sound_pack` — ID sound pack для использования. По умолчанию `opencode.default`.
-   `sounds` — Задаёт пользовательские звуковые файлы для `default`, `question`, `permission`, `error`, `done` или `subagent_done`. Пути могут быть абсолютными, `file://` URL или относительными к `tui.json`.

---

## [Кастомизация](#кастомизация)

Вы можете настроить различные аспекты представления TUI, используя палитру команд (`ctrl+x h` или `/help`). Эти настройки сохраняются после перезапуска.

---

#### [Отображение имени пользователя](#отображение-имени-пользователя)

Включите, будет ли ваше имя пользователя отображаться в сообщениях чата. Доступ к этому через:

-   Палитра команд: поиск «имя пользователя» или «скрыть имя пользователя».
-   Настройка сохраняется автоматически и будет запоминаться во время сеансов TUI.

[Редактировать страницу](https://github.com/anomalyco/opencode/edit/dev/packages/web/src/content/docs/ru/tui.mdx)[Found a bug? Open an issue](https://github.com/anomalyco/opencode/issues/new)[Join our Discord community](https://opencode.ai/discord) Выберите язык EnglishالعربيةBosanskiDanskDeutschEspañolFrançaisItaliano日本語한국어Norsk BokmålPolskiPortuguês (Brasil)РусскийไทยTürkçe简体中文繁體中文 

© [Anomaly](https://anoma.ly)

Последнее обновление: 30 мая 2026 г.
