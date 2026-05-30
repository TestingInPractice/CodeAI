Введение | OpenCode     [Перейти к содержимому](#_top)

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
-   [Установка](#установка)
-   [Настроить](#настроить)
-   [Инициализация](#инициализация)
-   [Использование](#использование)
    -   [Задавайте вопросы](#задавайте-вопросы)
    -   [Добавление функций](#добавление-функций)
    -   [Внесение изменений](#внесение-изменений)
    -   [Отмена изменений](#отмена-изменений)
-   [Общий доступ](#общий-доступ)
-   [Настроить](#настроить-1)

## На этой странице

-   [Обзор](#_top)
-   [Установка](#установка)
-   [Настроить](#настроить)
-   [Инициализация](#инициализация)
-   [Использование](#использование)
    -   [Задавайте вопросы](#задавайте-вопросы)
    -   [Добавление функций](#добавление-функций)
    -   [Внесение изменений](#внесение-изменений)
    -   [Отмена изменений](#отмена-изменений)
-   [Общий доступ](#общий-доступ)
-   [Настроить](#настроить-1)

# Введение

Начните работу с opencode.

[**opencode**](/) — это агент кодирования искусственного интеллекта с открытым исходным кодом. Он доступен в виде интерфейса на базе терминала, настольного приложения или расширения IDE.

![opencode TUI с темой opencode](/docs/_astro/screenshot.CQjBbRyJ_1dLadc.webp)

Давайте начнем.

---

#### [Системные требования](#системные-требования)

Чтобы использовать opencode в вашем терминале, вам понадобится:

1.  Современный эмулятор терминала, например:
    
    -   [WezTerm](https://wezterm.org), кроссплатформенный
    -   [Alacritty](https://alacritty.org), кроссплатформенный
    -   [Ghostty](https://ghostty.org), Linux и macOS
    -   [Kitty](https://sw.kovidgoyal.net/kitty/), Linux и macOS
2.  Ключи API для поставщиков LLM, которых вы хотите использовать.
    

---

## [Установка](#установка)

Самый простой способ установить opencode — через сценарий установки.

Окно терминала

```
curl -fsSL https://opencode.ai/install | bash
```

Вы также можете установить его с помощью следующих команд:

-   **Использование Node.js**
    
    -   [npm](#tab-panel-84)
    -   [Bun](#tab-panel-85)
    -   [pnpm](#tab-panel-86)
    -   [Yarn](#tab-panel-87)
    
    Окно терминала
    
    ```
    npm install -g opencode-ai
    ```
    
    Окно терминала
    
    ```
    bun install -g opencode-ai
    ```
    
    Окно терминала
    
    ```
    pnpm install -g opencode-ai
    ```
    
    Окно терминала
    
    ```
    yarn global add opencode-ai
    ```
    
-   **Использование Homebrew в macOS и Linux**
    
    Окно терминала
    
    ```
    brew install anomalyco/tap/opencode
    ```
    
    > Мы рекомендуем использовать tap opencode для получения самых последних версий. Официальная формула `brew install opencode` поддерживается командой Homebrew и обновляется реже.
    
-   **Использование Paru в Arch Linux**
    
    Окно терминала
    
    ```
    sudo pacman -S opencode           # Arch Linux (Stable)paru -S opencode-bin              # Arch Linux (Latest from AUR)
    ```
    

#### [Windows](#windows)

Рекомендуется: используйте WSL

Для наилучшей работы в Windows мы рекомендуем использовать [Подсистема Windows для Linux (WSL)](/docs/windows-wsl). Он обеспечивает лучшую производительность и полную совместимость с функциями opencode.

-   **Используя Chocolatey**
    
    Окно терминала
    
    ```
    choco install opencode
    ```
    
-   **Использование Scoop**
    
    Окно терминала
    
    ```
    scoop install opencode
    ```
    
-   **Использование NPM**
    
    Окно терминала
    
    ```
    npm install -g opencode-ai
    ```
    
-   **Использование Mise**
    
    Окно терминала
    
    ```
    mise use -g github:anomalyco/opencode
    ```
    
-   **Использование Docker**
    
    Окно терминала
    
    ```
    docker run -it --rm ghcr.io/anomalyco/opencode
    ```
    

В настоящее время добавляется поддержка установки opencode в Windows с помощью Bun.

Вы также можете получить двоичный файл в разделе [Releases](https://github.com/anomalyco/opencode/releases).

---

## [Настроить](#настроить)

С opencode вы можете использовать любого поставщика LLM, настроив его ключи API.

Если вы новичок в использовании поставщиков LLM, мы рекомендуем использовать [OpenCode Zen](/docs/zen). Это тщательно подобранный список моделей, протестированных и проверенных opencode.

1.  Запустите команду `/connect` в TUI, выберите opencode и перейдите по адресу [opencode.ai/auth](https://opencode.ai/auth).
    
    ```
    /connect
    ```
    
2.  Войдите в систему, добавьте свои платежные данные и скопируйте ключ API.
    
3.  Вставьте свой ключ API.
    
    ```
    ┌ API key││└ enter
    ```
    

Альтернативно вы можете выбрать одного из других поставщиков. [Подробнее](/docs/providers#directory).

---

## [Инициализация](#инициализация)

Теперь, когда вы настроили поставщика, вы можете перейти к проекту, который над которым вы хотите работать.

Окно терминала

```
cd /path/to/project
```

И запустите opencode.

Окно терминала

```
opencode
```

Затем инициализируйте opencode для проекта, выполнив следующую команду.

```
/init
```

Это позволит opencode проанализировать ваш проект и создать файл `AGENTS.md` в корень проекта.

Совет

Вам следует зафиксировать файл `AGENTS.md` вашего проекта в Git.

Это помогает opencode понять структуру проекта и шаблоны кодирования. использовал.

---

## [Использование](#использование)

Теперь вы готовы использовать opencode для работы над своим проектом. Не стесняйтесь спрашивать о чем угодно!

Если вы новичок в использовании агента кодирования ИИ, вот несколько примеров, которые могут вам помочь.

---

### [Задавайте вопросы](#задавайте-вопросы)

Вы можете попросить opencode объяснить вам кодовую базу.

Совет

Используйте ключ `@` для нечеткого поиска файлов в проекте.

```
How is authentication handled in @packages/functions/src/api/index.ts
```

Это полезно, если есть часть кодовой базы, над которой вы не работали.

---

### [Добавление функций](#добавление-функций)

Вы можете попросить opencode добавить новые функции в ваш проект. Хотя мы сначала рекомендуем попросить его создать план.

1.  **Составьте план**
    
    opencode имеет *режим планирования*, который отключает возможность вносить изменения и вместо этого предложите *как* реализовать эту функцию.
    
    Переключитесь на него с помощью клавиши **Tab**. Вы увидите индикатор этого в правом нижнем углу.
    
    ```
    <TAB>
    ```
    
    Теперь давайте опишем, что мы хотим от него.
    
    ```
    When a user deletes a note, we'd like to flag it as deleted in the database.Then create a screen that shows all the recently deleted notes.From this screen, the user can undelete a note or permanently delete it.
    ```
    
    Вы хотите предоставить opencode достаточно подробностей, чтобы понять, чего вы хотите. Это помогает поговорить с ним так, как будто вы разговариваете с младшим разработчиком в своей команде.
    
    Совет
    
    Дайте opencode много контекста и примеров, чтобы помочь ему понять, что вы хотеть.
    
2.  **Итерация плана**
    
    Как только он предоставит вам план, вы можете оставить ему отзыв или добавить более подробную информацию.
    
    ```
    We'd like to design this new screen using a design I've used before.[Image #1] Take a look at this image and use it as a reference.
    ```
    
    Совет
    
    Перетащите изображения в терминал, чтобы добавить их в подсказку.
    
    opencode может сканировать любые изображения, которые вы ему предоставляете, и добавлять их в командную строку. Вы можете сделать это, перетащив изображение в терминал.
    
3.  **Создайте функцию**
    
    Как только вы почувствуете себя комфортно с планом, вернитесь в *режим сборки*, снова нажав клавишу **Tab**.
    
    ```
    <TAB>
    ```
    
    И попросить его внести изменения.
    
    ```
    Sounds good! Go ahead and make the changes.
    ```
    

---

### [Внесение изменений](#внесение-изменений)

Для более простых изменений вы можете попросить opencode создать их напрямую. без необходимости предварительного рассмотрения плана.

```
We need to add authentication to the /settings route. Take a look at how this ishandled in the /notes route in @packages/functions/src/notes.ts and implementthe same logic in @packages/functions/src/settings.ts
```

Убедитесь, что предоставили достаточно деталей, чтобы opencode внес корректные изменения.

---

### [Отмена изменений](#отмена-изменений)

Допустим, вы просите opencode внести некоторые изменения.

```
Can you refactor the function in @packages/functions/src/api/index.ts?
```

Но вы понимаете, что это не то, чего вы хотели. Вы **можете отменить** изменения с помощью команды `/undo`.

```
/undo
```

opencode отменит внесенные вами изменения и покажет исходное сообщение. снова.

```
Can you refactor the function in @packages/functions/src/api/index.ts?
```

Отсюда вы можете настроить подсказку и попросить opencode повторить попытку.

Совет

Вы можете запустить `/undo` несколько раз, чтобы отменить несколько изменений.

Или вы **можете повторить** изменения с помощью команды `/redo`.

```
/redo
```

---

## [Общий доступ](#общий-доступ)

Разговорами, которые вы ведете с opencode, можно [поделиться с вашей командой](/docs/share).

```
/share
```

Это создаст ссылку на текущий разговор и скопирует ее в буфер обмена.

Заметка

По умолчанию общий доступ к беседам не предоставляется.

Вот [пример диалога](https://opencode.ai/s/4XP1fce5) с opencode.

---

## [Настроить](#настроить-1)

И все! Теперь вы профессионал в использовании opencode.

Чтобы создать свою собственную, мы рекомендуем [выбрать тему](/docs/themes), [настроить привязки клавиш](/docs/keybinds), [настроить средства форматирования кода](/docs/formatters), [создать собственные команды](/docs/commands) или поиграться с файлом [opencode config](/docs/config).

[Редактировать страницу](https://github.com/anomalyco/opencode/edit/dev/packages/web/src/content/docs/ru/index.mdx)[Found a bug? Open an issue](https://github.com/anomalyco/opencode/issues/new)[Join our Discord community](https://opencode.ai/discord) Выберите язык EnglishالعربيةBosanskiDanskDeutschEspañolFrançaisItaliano日本語한국어Norsk BokmålPolskiPortuguês (Brasil)РусскийไทยTürkçe简体中文繁體中文 

© [Anomaly](https://anoma.ly)

Последнее обновление: 30 мая 2026 г.
