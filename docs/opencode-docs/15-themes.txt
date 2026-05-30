Темы | OpenCode     [Перейти к содержимому](#_top)

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
-   [Требования к терминалу](#требования-к-терминалу)
-   [Встроенные темы](#встроенные-темы)
-   [Системная тема](#системная-тема)
-   [Использование темы](#использование-темы)
-   [Пользовательские темы](#пользовательские-темы)
    -   [Иерархия](#иерархия)
    -   [Создание темы](#создание-темы)
    -   [Формат JSON](#формат-json)
    -   [Определения цвета](#определения-цвета)
    -   [Настройки терминала по умолчанию](#настройки-терминала-по-умолчанию)
    -   [Пример](#пример)

## На этой странице

-   [Обзор](#_top)
-   [Требования к терминалу](#требования-к-терминалу)
-   [Встроенные темы](#встроенные-темы)
-   [Системная тема](#системная-тема)
-   [Использование темы](#использование-темы)
-   [Пользовательские темы](#пользовательские-темы)
    -   [Иерархия](#иерархия)
    -   [Создание темы](#создание-темы)
    -   [Формат JSON](#формат-json)
    -   [Определения цвета](#определения-цвета)
    -   [Настройки терминала по умолчанию](#настройки-терминала-по-умолчанию)
    -   [Пример](#пример)

# Темы

Выберите встроенную тему или определите свою собственную.

С помощью opencode вы можете выбрать одну из нескольких встроенных тем, использовать тему, которая адаптируется к теме вашего терминала, или определить свою собственную тему.

По умолчанию opencode использует нашу собственную тему `opencode`.

---

## [Требования к терминалу](#требования-к-терминалу)

Чтобы темы корректно отображались в полной цветовой палитре, ваш терминал должен поддерживать **truecolor** (24-битный цвет). Большинство современных терминалов поддерживают это по умолчанию, но вам может потребоваться включить его:

-   **Проверьте поддержку**: запустите `echo $COLORTERM` — должен появиться `truecolor` или `24bit`.
-   **Включить truecolor**: установите переменную среды `COLORTERM=truecolor` в профиле shell.
-   **Совместимость терминала**: убедитесь, что ваш эмулятор терминала поддерживает 24-битный цвет (большинство современных терминалов, таких как iTerm2, Alacritty, Kitty, Windows Terminal и последние версии GNOME Terminal, поддерживают).

Без поддержки truecolor темы могут отображаться с пониженной точностью цветопередачи или вернуться к ближайшему приближению к 256 цветам.

---

## [Встроенные темы](#встроенные-темы)

opencode поставляется с несколькими встроенными темами.

Имя

Описание

`system`

Адаптируется к фоновому цвету терминала

`tokyonight`

Based on the [tokyonight](https://github.com/folke/tokyonight.nvim) theme

`everforest`

Based on the [Everforest](https://github.com/sainnhe/everforest) theme

`ayu`

Based on the [Ayu](https://github.com/ayu-theme) dark theme

`catppuccin`

Based on the [Catppuccin](https://github.com/catppuccin) theme

`catppuccin-macchiato`

Based on the [Catppuccin](https://github.com/catppuccin) theme

`gruvbox`

Based on the [Gruvbox](https://github.com/morhetz/gruvbox) theme

`kanagawa`

Based on the [Kanagawa](https://github.com/rebelot/kanagawa.nvim) theme

`nord`

Based on the [Nord](https://github.com/nordtheme/nord) theme

`matrix`

Хакерская тема: зеленый на черном

`one-dark`

Based on the [Atom One](https://github.com/Th3Whit3Wolf/one-nvim) Dark theme

И более того, мы постоянно добавляем новые темы.

---

## [Системная тема](#системная-тема)

Тема `system` автоматически адаптируется к цветовой схеме вашего терминала. В отличие от традиционных тем, использующих фиксированные цвета, тема *system*:

-   **Создает шкалу серого**: создает пользовательскую шкалу серого на основе цвета фона вашего терминала, обеспечивая оптимальный контраст.
-   **Использует цвета ANSI**: использует стандартные цвета ANSI (0–15) для подсветки синтаксиса и элементов пользовательского интерфейса, которые соответствуют цветовой палитре вашего терминала.
-   **Сохраняет настройки терминала по умолчанию**: использует `none` для цветов текста и фона, чтобы сохранить естественный вид вашего терминала.

Системная тема предназначена для пользователей, которые:

-   Хотите, чтобы opencode соответствовал внешнему виду их терминала
-   Используйте пользовательские цветовые схемы терминала
-   Предпочитайте единообразный вид для всех терминальных приложений.

---

## [Использование темы](#использование-темы)

Вы можете выбрать тему, вызвав выбор темы с помощью команды `/theme`. Или вы можете указать это в файле [tui.json](/docs/config#tui).

tui.json

```
{  "$schema": "https://opencode.ai/tui.json",  "theme": "tokyonight"}
```

---

## [Пользовательские темы](#пользовательские-темы)

opencode поддерживает гибкую систему тем на основе JSON, которая позволяет пользователям легко создавать и настраивать темы.

---

### [Иерархия](#иерархия)

Темы загружаются из нескольких каталогов в следующем порядке: более поздние каталоги переопределяют предыдущие:

1.  **Встроенные темы** — они встроены в двоичный файл.
2.  **Каталог конфигурации пользователя** — определяется в `~/.config/opencode/themes/*.json` или `$XDG_CONFIG_HOME/opencode/themes/*.json`.
3.  **Корневой каталог проекта** — определено в `<project-root>/.opencode/themes/*.json`.
4.  **Текущий рабочий каталог** — определено в `./.opencode/themes/*.json`.

Если несколько каталогов содержат тему с одинаковым именем, будет использоваться тема из каталога с более высоким приоритетом.

---

### [Создание темы](#создание-темы)

Чтобы создать собственную тему, создайте файл JSON в одном из каталогов темы.

Для глобальных тем:

Окно терминала

```
mkdir -p ~/.config/opencode/themesvim ~/.config/opencode/themes/my-theme.json
```

Для тем проекта:

Окно терминала

```
mkdir -p .opencode/themesvim .opencode/themes/my-theme.json
```

---

### [Формат JSON](#формат-json)

В темах используется гибкий формат JSON с поддержкой:

-   **Шестнадцатеричные цвета**: `"#ffffff"`
-   **Цвета ANSI**: `3` (0–255).
-   **Ссылки на цвета**: `"primary"` или пользовательские определения.
-   **Темный/светлый варианты**: `{"dark": "#000", "light": "#fff"}`
-   **Нет цвета**: `"none"` — используется цвет терминала по умолчанию или прозрачный.

---

### [Определения цвета](#определения-цвета)

Раздел `defs` является необязательным и позволяет вам определять повторно используемые цвета, на которые можно ссылаться в теме.

---

### [Настройки терминала по умолчанию](#настройки-терминала-по-умолчанию)

Специальное значение `"none"` можно использовать для любого цвета, чтобы наследовать цвет терминала по умолчанию. Это особенно полезно для создания тем, которые органично сочетаются с цветовой схемой вашего терминала:

-   `"text": "none"` — использует цвет переднего плана терминала по умолчанию.
-   `"background": "none"` — использует цвет фона терминала по умолчанию.

---

### [Пример](#пример)

Вот пример пользовательской темы:

my-theme.json

```
{  "$schema": "https://opencode.ai/theme.json",  "defs": {    "nord0": "#2E3440",    "nord1": "#3B4252",    "nord2": "#434C5E",    "nord3": "#4C566A",    "nord4": "#D8DEE9",    "nord5": "#E5E9F0",    "nord6": "#ECEFF4",    "nord7": "#8FBCBB",    "nord8": "#88C0D0",    "nord9": "#81A1C1",    "nord10": "#5E81AC",    "nord11": "#BF616A",    "nord12": "#D08770",    "nord13": "#EBCB8B",    "nord14": "#A3BE8C",    "nord15": "#B48EAD"  },  "theme": {    "primary": {      "dark": "nord8",      "light": "nord10"    },    "secondary": {      "dark": "nord9",      "light": "nord9"    },    "accent": {      "dark": "nord7",      "light": "nord7"    },    "error": {      "dark": "nord11",      "light": "nord11"    },    "warning": {      "dark": "nord12",      "light": "nord12"    },    "success": {      "dark": "nord14",      "light": "nord14"    },    "info": {      "dark": "nord8",      "light": "nord10"    },    "text": {      "dark": "nord4",      "light": "nord0"    },    "textMuted": {      "dark": "nord3",      "light": "nord1"    },    "background": {      "dark": "nord0",      "light": "nord6"    },    "backgroundPanel": {      "dark": "nord1",      "light": "nord5"    },    "backgroundElement": {      "dark": "nord1",      "light": "nord4"    },    "border": {      "dark": "nord2",      "light": "nord3"    },    "borderActive": {      "dark": "nord3",      "light": "nord2"    },    "borderSubtle": {      "dark": "nord2",      "light": "nord3"    },    "diffAdded": {      "dark": "nord14",      "light": "nord14"    },    "diffRemoved": {      "dark": "nord11",      "light": "nord11"    },    "diffContext": {      "dark": "nord3",      "light": "nord3"    },    "diffHunkHeader": {      "dark": "nord3",      "light": "nord3"    },    "diffHighlightAdded": {      "dark": "nord14",      "light": "nord14"    },    "diffHighlightRemoved": {      "dark": "nord11",      "light": "nord11"    },    "diffAddedBg": {      "dark": "#3B4252",      "light": "#E5E9F0"    },    "diffRemovedBg": {      "dark": "#3B4252",      "light": "#E5E9F0"    },    "diffContextBg": {      "dark": "nord1",      "light": "nord5"    },    "diffLineNumber": {      "dark": "nord2",      "light": "nord4"    },    "diffAddedLineNumberBg": {      "dark": "#3B4252",      "light": "#E5E9F0"    },    "diffRemovedLineNumberBg": {      "dark": "#3B4252",      "light": "#E5E9F0"    },    "markdownText": {      "dark": "nord4",      "light": "nord0"    },    "markdownHeading": {      "dark": "nord8",      "light": "nord10"    },    "markdownLink": {      "dark": "nord9",      "light": "nord9"    },    "markdownLinkText": {      "dark": "nord7",      "light": "nord7"    },    "markdownCode": {      "dark": "nord14",      "light": "nord14"    },    "markdownBlockQuote": {      "dark": "nord3",      "light": "nord3"    },    "markdownEmph": {      "dark": "nord12",      "light": "nord12"    },    "markdownStrong": {      "dark": "nord13",      "light": "nord13"    },    "markdownHorizontalRule": {      "dark": "nord3",      "light": "nord3"    },    "markdownListItem": {      "dark": "nord8",      "light": "nord10"    },    "markdownListEnumeration": {      "dark": "nord7",      "light": "nord7"    },    "markdownImage": {      "dark": "nord9",      "light": "nord9"    },    "markdownImageText": {      "dark": "nord7",      "light": "nord7"    },    "markdownCodeBlock": {      "dark": "nord4",      "light": "nord0"    },    "syntaxComment": {      "dark": "nord3",      "light": "nord3"    },    "syntaxKeyword": {      "dark": "nord9",      "light": "nord9"    },    "syntaxFunction": {      "dark": "nord8",      "light": "nord8"    },    "syntaxVariable": {      "dark": "nord7",      "light": "nord7"    },    "syntaxString": {      "dark": "nord14",      "light": "nord14"    },    "syntaxNumber": {      "dark": "nord15",      "light": "nord15"    },    "syntaxType": {      "dark": "nord7",      "light": "nord7"    },    "syntaxOperator": {      "dark": "nord9",      "light": "nord9"    },    "syntaxPunctuation": {      "dark": "nord4",      "light": "nord0"    }  }}
```

[Редактировать страницу](https://github.com/anomalyco/opencode/edit/dev/packages/web/src/content/docs/ru/themes.mdx)[Found a bug? Open an issue](https://github.com/anomalyco/opencode/issues/new)[Join our Discord community](https://opencode.ai/discord) Выберите язык EnglishالعربيةBosanskiDanskDeutschEspañolFrançaisItaliano日本語한국어Norsk BokmålPolskiPortuguês (Brasil)РусскийไทยTürkçe简体中文繁體中文 

© [Anomaly](https://anoma.ly)

Последнее обновление: 30 мая 2026 г.
