IDE | OpenCode     [Перейти к содержимому](#_top)

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
-   [Установка](#установка)
    -   [Ручная установка](#ручная-установка)
    -   [Устранение неполадок](#устранение-неполадок)

## На этой странице

-   [Обзор](#_top)
-   [Использование](#использование)
-   [Установка](#установка)
    -   [Ручная установка](#ручная-установка)
    -   [Устранение неполадок](#устранение-неполадок)

# IDE

Расширение opencode для VS Code, Cursor и других IDE.

opencode интегрируется с VS Code, Cursor или любой IDE, поддерживающей терминал. Просто запустите `opencode` в терминале, чтобы начать.

---

## [Использование](#использование)

-   **Быстрый запуск**: используйте `Cmd+Esc` (Mac) или `Ctrl+Esc` (Windows/Linux), чтобы открыть opencode в разделенном представлении терминала, или сфокусируйтесь на существующем сеансе терминала, если он уже запущен.
-   **Новый сеанс**: используйте `Cmd+Shift+Esc` (Mac) или `Ctrl+Shift+Esc` (Windows/Linux), чтобы начать новый сеанс терминала opencode, даже если он уже открыт. Вы также можете нажать кнопку opencode в пользовательском интерфейсе.
-   **Осведомленность о контексте**: автоматически делитесь своим текущим выбором или вкладкой с помощью opencode.
-   **Шорткаты ссылок на файлы**: Используйте `Cmd+Option+K` (Mac) или `Alt+Ctrl+K` (Linux/Windows) для вставки ссылок на файлы. Например, `@File#L37-42`.

---

## [Установка](#установка)

Чтобы установить opencode на VS Code и популярные форки, такие как Cursor, Windsurf, VSCodium:

1.  Откройте VS Code
2.  Откройте встроенный терминал
3.  Запустите `opencode` — расширение установится автоматически.

С другой стороны, если вы хотите использовать собственную IDE при запуске `/editor` или `/export` из TUI, вам необходимо установить `export EDITOR="code --wait"`. [Подробнее](/docs/tui/#editor-setup).

---

### [Ручная установка](#ручная-установка)

Найдите **opencode** в магазине расширений и нажмите **Установить**.

---

### [Устранение неполадок](#устранение-неполадок)

Если расширение не устанавливается автоматически:

-   Убедитесь, что вы используете `opencode` во встроенном терминале.
-   Убедитесь, что CLI для вашей IDE установлен:
    -   Для Code: команда `code`.
    -   Для Cursor: команда `cursor`.
    -   Для Windsurf: команда `windsurf`.
    -   Для VSCodium: команда `codium`.
    -   Если нет, запустите `Cmd+Shift+P` (Mac) или `Ctrl+Shift+P` (Windows/Linux) и найдите “Shell Command: Install ‘code’ command in PATH” (или эквивалент для вашей IDE).
-   Убедитесь, что у VS Code есть разрешение на установку расширений.

[Редактировать страницу](https://github.com/anomalyco/opencode/edit/dev/packages/web/src/content/docs/ru/ide.mdx)[Found a bug? Open an issue](https://github.com/anomalyco/opencode/issues/new)[Join our Discord community](https://opencode.ai/discord) Выберите язык EnglishالعربيةBosanskiDanskDeutschEspañolFrançaisItaliano日本語한국어Norsk BokmålPolskiPortuguês (Brasil)РусскийไทยTürkçe简体中文繁體中文 

© [Anomaly](https://anoma.ly)

Последнее обновление: 30 мая 2026 г.
