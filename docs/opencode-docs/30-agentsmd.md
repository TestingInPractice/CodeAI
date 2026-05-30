# AGENTS.md — открытый формат инструкций для AI-агентов

**AGENTS.md** — это простой открытый формат для управления AI-агентами программирования. Используется более чем в **60 000 open-source проектах** и поддерживается всеми основными агентами: opencode, OpenAI Codex, Cursor, GitHub Copilot, Google Jules, JetBrains Junie, Zed и другими.

Формат развивается под управлением [Agentic AI Foundation](https://aaif.io) (Linux Foundation).

---

## Проблема

`README.md` создан для людей: описание проекта, быстрый старт, гайды по контрибьюции.

AGENTS.md дополняет его, содержа контекст, который нужен AI-агентам, но излишен для человека:
- Команды сборки и тестирования
- Соглашения о коде
- Особенности окружения
- Инструкции для PR и коммитов
- Безопасность и специфичные нюансы

**Разделение** даёт:
- Агенту — понятное предсказуемое место с инструкциями
- README — лаконичность и фокус на человеке
- Экосистеме — единый формат поверх всех инструментов

---

## Как использовать

### 1. Добавить AGENTS.md

Создайте `AGENTS.md` в корне репозитория. Большинство агентов умеют сгенерировать его по команде `/init`.

### 2. Наполнить нужными секциями

Популярные разделы:
- **Project overview** — краткое описание проекта
- **Build & test commands** — как собрать и протестировать
- **Code style** — соглашения о коде
- **Testing instructions** — как запускать и писать тесты
- **Security considerations** — особенности безопасности
- **PR instructions** — формат PR и коммитов
- **Dev environment** — особенности окружения

### 3. Пример

```markdown
# AGENTS.md

## Dev environment tips
- Используй `pnpm dlx turbo run where <project_name>` для навигации
- Запускай `pnpm install --filter <project_name>` для установки зависимостей в workspace
- Используй `pnpm create vite@latest <project_name> -- --template react-ts` для нового пакета

## Testing instructions
- CI-план в .github/workflows
- Запускай `pnpm turbo run test --filter <project_name>` для полного прогона
- Для одного теста: `pnpm vitest run -t "<test name>"`
- Все тесты должны быть зелёными перед мержем
- После перемещения файлов запусти `pnpm lint --filter <project_name>`

## PR instructions
- Формат заголовка: [<project_name>] <Title>
- Всегда запускай `pnpm lint` и `pnpm test` перед коммитом
```

---

## Монорепозитории: вложенные AGENTS.md

В монорепозитории можно разместить `AGENTS.md` в каждом пакете. Агент автоматически читает ближайший к редактируемому файлу — так каждый подпроект получает свои инструкции.

Например, в основном репозитории OpenAI используется **88 AGENTS.md** файлов для разных подпроектов.

```
monorepo/
├── AGENTS.md                  # общие инструкции для всего репозитория
├── packages/
│   ├── frontend/
│   │   ├── AGENTS.md          # инструкции для фронтенда
│   │   └── ...
│   └── api/
│       ├── AGENTS.md          # инструкции для API
│       └── ...
```

**Принцип приоритета:** ближайший AGENTS.md к редактируемому файлу имеет высший приоритет; явные инструкции пользователя в чате переопределяют всё.

---

## Настройка агентов

### opencode

OpenCode автоматически использует `AGENTS.md` после инициализации (`/init`). Файл создаётся в корне проекта и фиксируется в Git. Документация: [opencode.ai/docs/rules](https://opencode.ai/docs/rules/)

### Aider

В `.aider.conf.yml`:

```yaml
read: AGENTS.md
```

### Gemini CLI

В `.gemini/settings.json`:

```json
{
  "context": {
    "fileName": "AGENTS.md"
  }
}
```

### Другие агенты

Cursor, GitHub Copilot, VS Code, Windsurf, Augment Code, Factory, goose, Zed, Warp и другие — все поддерживают AGENTS.md из коробки.

---

## Миграция с других форматов

Переименуйте существующий файл и создайте символическую ссылку для обратной совместимости:

```bash
mv AGENT.md AGENTS.md && ln -s AGENTS.md AGENT.md
```

Для `.cursorrules`:

```bash
mv .cursorrules AGENTS.md && ln -s AGENTS.md .cursorrules
```

---

## FAQ

### Есть ли обязательные поля?

Нет. AGENTS.md — это стандартный Markdown. Используйте любые заголовки; агент просто парсит предоставленный текст.

### Что делать при конфликте инструкций?

Ближайший AGENTS.md к редактируемому файлу побеждает; явные промпты пользователя переопределяют всё.

### Будет ли агент автоматически запускать команды из AGENTS.md?

Да, если они перечислены. Агент попытается выполнить релевантные проверки и исправить ошибки до завершения задачи.

### Можно ли обновлять файл?

Да. Воспринимайте AGENTS.md как живую документацию — меняйте её по мере развития проекта.

---

## Ссылки

- [Официальный сайт AGENTS.md](https://agents.md/)
- [Репозиторий на GitHub](https://github.com/agentsmd/agents.md)
- [Agentic AI Foundation](https://aaif.io)
- [60k+ примеров AGENTS.md на GitHub](https://github.com/search?q=path%3AAGENTS.md+NOT+is%3Afork+NOT+is%3Aarchived&type=code)
- [Документация opencode по правилам](https://opencode.ai/docs/rules/)
