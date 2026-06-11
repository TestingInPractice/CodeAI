# Среда разработки Claude Code: архитектура, ограничения, паттерны

> **Дата:** 2026-05-07
> **Версия:** 1.0
> **Цель:** Понимание границ Claude Code для проектирования эффективных навыков и workflow в dot_ai

---

## 1. Архитектура Claude Code

### Модель взаимодействия: agentic harness

Claude Code — "agentic harness" вокруг LLM. Предоставляет инструменты, управление контекстом и среду выполнения, превращая языковую модель в способного coding-агента `[L2]`.

**Agentic Loop** — цикл `while(true)` с тремя фазами:
1. **Gather context** — поиск файлов, чтение кода, анализ git-истории
2. **Take action** — редактирование файлов, выполнение команд, создание коммитов
3. **Verify results** — запуск тестов, проверка ошибок, подтверждение изменений

Цикл однопоточный, но некоторые read-only инструменты выполняются параллельно. Адаптируется к задаче: вопрос по кодовой базе может потребовать только контекст, а исправление бага — все три фазы многократно `[L2]` `[L3]`.

### Жизненный цикл сессии

**Init:**
- Claude Code обходит дерево директорий, загружая CLAUDE.md файлы, auto memory (первые 200 строк / 25KB MEMORY.md), settings.json, описания навыков, MCP-серверы и правила из `.claude/rules/`
- Сессии независимы — каждая начинается с чистого контекстного окна `[L2]`

**Tool calls:**
- Модель рассуждает, выбирает инструменты, наблюдает результаты, итерирует
- Каждый tool use возвращает информацию, питающую обратную связь цикла `[L2]`

**Context compression:**
- Автоматическая компакция при приближении к лимиту контекстного окна (подробнее в разделе 6)

**Exit/cleanup:**
- Сессии сохраняются как JSONL в `~/.claude/projects/`
- Снепшоты файлов создаются перед редактированием для checkpoint/undo `[L2]`

**Среды выполнения:** Local (машина разработчика, default), Cloud (Anthropic-managed VMs), Remote Control (машина управляется из браузера). Agentic loop идентичен во всех средах `[L2]`.

### Механизм context window management: compaction, summarization

**Server-side compaction** — API-механизм:
1. Определяет, когда входные токены превышают порог (default: 150,000 токенов; минимум: 50,000)
2. Генерирует сводку текущей беседы
3. Создаёт `compaction`-блок с summary
4. Продолжает ответ с компактным контекстом
5. На последующих запросах все блоки до `compaction` автоматически удаляются

Поддерживается на Opus 4.7, Opus 4.6, Sonnet 4.6, Mythos Preview `[L2]`.

**Поведение в Claude Code CLI:**
- Автоматически очищает старые tool outputs, затем суммаризует беседу
- Запросы пользователя и ключевые фрагменты кода сохраняются; детальные инструкции из начала беседы могут теряться
- Если единичный файл или tool output настолько велик, что контекст заполняется сразу после summary — Claude Code прекращает auto-compact после нескольких попыток и показывает ошибку ("thrashing error") `[L2]`
- CLAUDE.md корневого каталога проекта переживает compaction (перечитывается с диска). Вложенные CLAUDE.md в подкаталогах НЕ переинжектируются автоматически `[L2]`

**Prompt caching:**
- Кеширует полный prefix до cache breakpoint (порядок: `tools` → `system` → `messages`)
- Максимум 4 cache breakpoints на запрос
- TTL: 5 минут (default, 1.25x запись, 0.1x чтение) или 1 час (2x запись, 0.1x чтение) `[L2]`
- Пауза >5 минут = cache miss = полная стоимость записи на следующем вызове `[L3]`
- Forks (субагенты) разделяют prompt cache с родителем; именованные субагенты — нет `[L2]`

---

## 2. Инструменты (Tools)

### Полный перечень инструментов

| Инструмент | Описание | Требует разрешение |
|---|---|---|
| `Agent` | Запуск субагента с собственным контекстом | Нет |
| `AskUserQuestion` | Вопросы с вариантами ответа | Нет |
| `Bash` | Выполнение shell-команд | Да |
| `CronCreate/Delete/List` | Планирование повторяющихся/разовых промптов | Нет |
| `Edit` | Целевые правки файлов | Да |
| `EnterPlanMode/ExitPlanMode` | Переключение в режим планирования | Exit — Да |
| `EnterWorktree/ExitWorktree` | Изолированные git worktree | Нет |
| `Glob` | Поиск файлов по паттерну | Нет |
| `Grep` | Поиск по содержимому с regex | Нет |
| `LSP` | Интеллектуальный анализ кода | Нет |
| `NotebookEdit` | Редактирование Jupyter notebooks | Да |
| `PowerShell` | PowerShell-команды на Windows (preview) | Да |
| `Read` | Чтение файлов (до 2000 строк по умолчанию) | Нет |
| `Skill` | Вызов навыка | Да |
| `TaskCreate/Get/List/Update/Stop` | Управление задачами сессии | Нет |
| `ToolSearch` | Поиск и загрузка отложенных инструментов | Нет |
| `WebFetch` | Загрузка контента по URL | Да |
| `WebSearch` | Веб-поиск | Да |
| `Write` | Создание/перезапись файлов | Да |

Источник: `[L2]` code.claude.com/docs/en/tools-reference

### Механизм разрешения (permissions)

**Типы правил:** allow, ask, deny. Порядок оценки: **deny → ask → allow**. Первое совпавшее правило побеждает; deny всегда имеет приоритет `[L2]`.

**Режимы разрешений** (через `defaultMode` или Shift+Tab):
- `default` — запрашивает разрешение при первом использовании каждого инструмента
- `acceptEdits` — автоматически принимает редактирования и файловые операции
- `plan` — только read-only инструменты
- `auto` — авто-одобрение с фоновыми проверками безопасности (research preview)
- `dontAsk` — auto-deny без предварительного одобрения
- `bypassPermissions` — пропускает все промпты (кроме circuit breaker для `rm -rf /`)

**Приоритет настроек** (от высшего к низшему):
1. Managed settings (нельзя переопределить)
2. Аргументы командной строки
3. Local project settings (`.claude/settings.local.json`)
4. Shared project settings (`.claude/settings.json`)
5. User settings (`~/.claude/settings.json`)

Если инструмент denied на любом уровне, ни один другой уровень не может его разрешить `[L2]`.

### Ограничения инструментов

- **Read**: до 2000 строк по умолчанию, с опциональными offset/limit. Для PDF — максимум 20 страниц за запрос
- **Bash**: таймаут по умолчанию 2 минуты (120,000ms), максимум 10 минут (600,000ms)
- **Grep/Glob**: возвращают до 250 записей по умолчанию
- **Edit**: заменяемая строка (`old_string`) должна быть уникальна в файле
- **WebFetch/WebSearch**: могут быть ограничены доменными фильтрами
- **Bash read-only команды** без промптов: `ls`, `cat`, `head`, `tail`, `grep`, `find`, `wc`, `diff`, `stat`, `du`, `cd`, read-only git. Набор не конфигурируется `[L2]`

---

## 3. Системный промпт и скрытые инструкции

### Что входит в system prompt по умолчанию

Системный промпт начинается с: *"You are Claude Code, Anthropic's official CLI for Claude. You are an interactive CLI tool that helps users with software engineering tasks."* `[L3]`

Полный промпт живёт в `constants/prompts.ts` исходного кода Claude Code `[L3]`. Отслеживается по версиям на cchistory.mariozechner.at `[L3]`. Установка `CLAUDE_CODE_SIMPLE=1` коллапсирует многосекционный промпт до базовой строки идентичности `[L3]`.

Системный промпт содержит: идентичность, описание инструментов, поведенческие инструкции (tone, style, safety), инструкции по commit/PR, правила контекстного управления.

### Какие инструкции нельзя переопределить через CLAUDE.md

**CLAUDE.md доставляется как user message после системного промпта, не как часть system prompt.** Claude читает и пытается следовать, но гарантии строгого compliance нет, особенно для размытых или конфликтующих инструкций `[L2]`.

Для инструкций уровня system prompt — использовать `--append-system-prompt`, но этот флаг нужно передавать при каждом вызове `[L2]`.

Поведенческие инструкции из system prompt (tone, safety, commit style) встроены в harness и не могут быть полностью переопределены через CLAUDE.md или навыки.

### Механизм подстановки CLAUDE.md, settings.json, memory

**CLAUDE.md** загружается обходом дерева директорий снизу вверх от CWD. Все обнаруженные файлы конкатенируются (не переопределяются). Содержимое упорядочено от корня файловой системы к CWD — инструкции ближе к точке запуска читаются последними. Подкаталог CLAUDE.md загружается on-demand при чтении файлов в этих подкаталогах `[L2]`.

**settings.json** — конфигурация на нескольких уровнях:
- `~/.claude/settings.json` — пользователь, все проекты
- `.claude/settings.json` — проект, shared (committed)
- `.claude/settings.local.json` — проект, personal (gitignored)

**Auto memory** — `~/.claude/projects/<project>/memory/MEMORY.md`. Первые 200 строк или 25KB загружаются при старте сессии. Тематические файлы — по запросу `[L2]`.

**HTML-комментарии** (`<!-- -->`) в CLAUDE.md вырезаются перед инжекцией для экономии токенов. `@path/to/file` импорты раскрываются при загрузке (макс. 5 уровней рекурсии) `[L2]`.

### Приоритет источников инструкций

Контекст собирается в следующем порядке:

1. **System prompt** — зашит Anthropic, включает определения инструментов, идентичность, поведенческие инструкции
2. **Managed policy CLAUDE.md** — организационный, нельзя исключить
3. **User-level CLAUDE.md** (`~/.claude/CLAUDE.md`) — личные предпочтения
4. **User-level rules** (`~/.claude/rules/`)
5. **Project CLAUDE.md** (`./CLAUDE.md` или `./.claude/CLAUDE.md`) — командные инструкции
6. **Project rules** (`.claude/rules/`) — модульные, с опциональным path-scoping через YAML frontmatter
7. **Local CLAUDE.md** (`./CLAUDE.local.md`) — персональные проектные, gitignored
8. **Auto memory** — первые 200 строк / 25KB
9. **Skill descriptions** — при старте сессии; полное содержимое — по запросу

Более специфичные расположения имеют приоритет над более общими. Содержимое конкатенируется `[L2]`.

---

## 4. Навыки (Skills)

### Механизм активации и подстановки skill content

Навыки — упакованные промпты: markdown-файлы с инструкциями, обучающими Claude новой процедуре. Каждый навык — директория с `SKILL.md` как entry point `[L2]`.

**Пути активации:**
- **Автоматический**: При старте сессии Claude получает имена и описания навыков. При получении задачи Claude автономно решает вызвать навык, если описание совпадает. Управляется полями `description` и `when_to_use` в frontmatter
- **Ручной**: Пользователь вызывает через `/skill-name`
- **Программный**: Субагенты могут обнаруживать и использовать навыки

**Загрузка ленивая (lazy):** При старте загружаются только описания (потребляя бюджет контекста). Полное содержимое SKILL.md загружается только при вызове. После загрузки содержимое входит в беседу как единое сообщение и остаётся до конца сессии `[L2]`.

### Ограничения на размер навыка и количество одновременно загруженных

- **SKILL.md body**: рекомендуется до 500 строк. Каждая строка — повторяющаяся токенная стоимость
- **Combined description + when_to_use**: обрезается до **1,536 символов** в listing навыков
- **Бюджет контекста для всех описаний навыков**: масштабируется динамически как 1% от контекстного окна, с fallback 8,000 символов. Настраивается через `SLASH_COMMAND_TOOL_CHAR_BUDGET`
- **После compaction**: первые 5,000 токенов каждого вызванного навыка сохраняются, с общим бюджетом 25,000 токенов для всех навыков

Источник: `[L2]` code.claude.com/docs/en/skills

**Интерпретация лимита 500 строк:** это soft limit для стоимости и сопровождения, а не доказанный универсальный порог качества. Официальная документация объясняет механизм: тело навыка после вызова остаётся в контексте, а supporting files позволяют держать `SKILL.md` сфокусированным `[L2]`. Исследования long context и instruction following подтверждают риски роста контекста и количества ограничений, но указывают на причинные факторы — релевантность, позицию информации, плотность инструкций, структуру и измеримую сложность задачи — а не на число строк само по себе `[L1]` `[L2]`.

**Гипотеза для dot_ai:** длинный навык может быть эффективнее короткого, если он даёт модели много релевантного контекста для маленькой измеримой задачи. Валидировать нужно через regression eval: task success rate, соблюдение обязательных правил, отсутствие пропусков в середине, стоимость токенов и устойчивость после compaction.

### Взаимодействие навыков друг с другом

Навыки независимы и не координируются по умолчанию. Могут ссылаться друг на друга (progressive disclosure). Субагенты могут использовать навыки. Навыки могут включать дополнительные файлы и скрипты. Custom commands (`.claude/commands/`) объединены с навыками — оба механизма работают одинаково, но навыки поддерживают дополнительные возможности `[L2]`.

### Лучшие практики структурирования навыков

- **Лаконичность**: до 500 строк SKILL.md по умолчанию; превышение — повод для eval и ревизии, не автоматический дефект
- **Чёткий description + when_to_use**: определяют автодискавери; ограничены 1,536 символов
- **Структурированные секции**: Markdown-заголовки для парсинга границ
- **Frontmatter**: `allowed-tools` для пред-одобрения инструментов, `context: fork` для изоляции, `model` для override модели
- **Progressive disclosure**: критичные инструкции в начале, справочный материал — ниже
- **Примеры важнее правил**: 2-3 канонических примера эффективнее исчерпывающих списков

---

## 5. Hooks и автоматизация

### Типы хуков

Claude Code поддерживает **30+ lifecycle hook events** `[L2]`:

| Событие | Когда срабатывает | Блокирующее? |
|---|---|---|
| `SessionStart` | Начало/возобновление сессии | Нет (показывает ошибку) |
| `UserPromptSubmit` | Перед обработкой промпта | Да |
| `PreToolUse` | Перед выполнением инструмента | Да |
| `PostToolUse` | После успешного выполнения | Нет (feedback only) |
| `PostToolBatch` | После завершения параллельного batch | Нет |
| `Stop` | Claude завершает ответ | Да (может продолжить) |
| `Notification` | Claude отправляет уведомление | Нет |
| `SubagentStart/Stop` | Запуск/завершение субагента | Нет |
| `PreCompact/PostCompact` | До/после compaction | Нет / Нет |
| `InstructionsLoaded` | CLAUDE.md или rules загружены | Нет |
| `ConfigChange` | Конфиг изменился во время сессии | Да |
| `PermissionRequest` | Диалог разрешения | Возвращает решение |
| `FileChanged` | Watched файл изменился | Нет |

### Типы хуков

Пять типов хуков:
- **`command`** — shell-команда (default). Коммуникация через stdin/stdout/stderr и exit codes
- **`http`** — POST данных события на URL endpoint
- **`mcp_tool`** — вызов инструмента на подключённом MCP-сервере
- **`prompt`** — однотурная LLM-оценка (Haiku по умолчанию)
- **`agent`** — многоходовая верификация с доступом к инструментам (экспериментальный)

### Что можно/нельзя делать в хуках

**Можно** `[L2]`:
- Блокировать выполнение инструментов (PreToolUse → deny)
- Модифицировать ввод инструментов (PreToolUse → updatedInput)
- Добавлять feedback после выполнения (PostToolUse)
- Управлять разрешениями (PermissionRequest → allow/deny)
- Заставлять Claude продолжать работу (Stop → продолжить)
- Выполнять детерминированные действия (линтинг, форматирование)

**Нельзя** `[L2]`:
- `PostToolUse` не может отменить уже выполненное действие
- Хуки не могут запускать `/`-команды или tool calls
- Несколько `PreToolUse` с `updatedInput` — последний завершившийся побеждает (недетерминированный порядок, т.к. хуки выполняются параллельно)
- `PermissionRequest` хуки не срабатывают в non-interactive режиме (`-p`)
- Хуки могут **ужесточать** ограничения, но не **ослаблять**: `deny` работает даже в `bypassPermissions`, но `allow` не отменяет deny-правила из settings

### Интеграция хуков с навыками и workflow

Хуки могут быть scoped к жизненному циклу навыка через поле `hooks` в frontmatter. Это позволяет детерминированные действия (например, линтинг после правок) только когда конкретный навык активен. Хуки обеспечивают соблюдение поведения, не зависящее от compliance модели `[L2]`.

**Конфигурация хуков** может размещаться в:
- `~/.claude/settings.json` (user scope)
- `.claude/settings.json` (project scope, shared)
- `.claude/settings.local.json` (project scope, personal)
- Managed policy settings (org-wide)
- Plugin `hooks/hooks.json`
- Skill/agent frontmatter

Default timeout: 10 минут на хук, конфигурируется через `timeout` `[L2]`.

---

## 6. Memory и персистентность

### Как работает memory: файлы, индекс, подстановка

**Два механизма memory** `[L2]`:

| | CLAUDE.md | Auto Memory |
|---|---|---|
| **Кто пишет** | Пользователь | Claude |
| **Содержимое** | Инструкции и правила | Наблюдения и паттерны |
| **Область** | Project, user, org | Per working tree (git repo) |
| **Загрузка** | Каждая сессия, полностью | Первые 200 строк / 25KB MEMORY.md |
| **Назначение** | Стандарты кода, workflow, архитектура | Команды сборки, debug-инсайты, предпочтения |

**Auto memory детали:**
- Хранение: `~/.claude/projects/<project>/memory/`
- `MEMORY.md` — индекс директории memory
- Первые 200 строк или 25KB загружаются при старте сессии
- Тематические файлы — по запросу, не при старте
- Machine-local — все worktrees одного git repo разделяют одну директорию auto memory
- Переключается через `/memory`, `autoMemoryEnabled` в settings, или `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`

### Ограничения memory

- **CLAUDE.md доставляется как user message**, не system prompt — нет гарантии строгого compliance `[L2]`
- **После `/compact`**: project-root CLAUDE.md переживает, вложенные — нет `[L2]`
- Конфликтующие инструкции между файлами — Claude выбирает произвольно `[L2]`
- **MEMORY.md**: только 200 строк / 25KB при старте. Строки после 200 truncate `[L2]`
- Тематические файлы загружаются по запросу — не входят в стартовый бюджет

### Стратегия использования memory vs CLAUDE.md vs skills

| Механизм | Лучше всего для | Токенная стоимость |
|---|---|---|
| CLAUDE.md | Постоянные инструкции, каждая сессия | Всегда загружен |
| `.claude/rules/` с paths | Условные инструкции по типу файлов | Только при совпадении |
| Auto memory | Накопленные наблюдения | 200 строк / 25KB |
| Skills | Многошаговые процедуры, workflow | По запросу |
| Hooks (SessionStart compact) | Реинжекция после compaction | Только после compact |

---

## 7. Agent (субагенты)

### Механизм запуска субагентов

Субагенты запускаются через инструмент `Agent` с собственным контекстным окном. Каждый субагент получает `[L2]`:
- Пользовательский system prompt (markdown-тело субагента)
- Специфичный список доступа к инструментам
- Независимые разрешения

### Типы субагентов

| Тип | Модель | Инструменты | Назначение |
|---|---|---|---|
| **Explore** | Haiku (быстрый) | Read-only (без Write/Edit) | Поиск кода, обнаружение файлов |
| **Plan** | Наследует от родителя | Read-only | Исследование кодовой базы для планирования |
| **General-purpose** | Наследует от родителя | Все инструменты | Сложные многошаговые задачи |
| **claude-code-guide** | Haiku | Read-only | Вопросы о Claude Code |
| **statusline-setup** | Sonnet | — | Конфигурация statusline |

Explore поддерживает уровни thoroughness: `quick`, `medium`, `very thorough`.

### Изоляция контекста: что видит субагент, а что нет

**Видит:** Собственный system prompt, рабочую директорию, разрешённые инструменты, предзагруженные навыки, первые 200 строк своего MEMORY.md `[L2]`.

**НЕ видит:** Историю беседы родителя, system prompt родителя, CLAUDE.md родителя, auto memory родителя, результаты других субагентов (если не переданы через родителя) `[L2]`.

**Исключение — Forks:** Fork наследует **всю беседу** (system prompt, инструменты, модель, историю сообщений). Forks разделяют prompt cache с родителем `[L2]`.

### Ограничения

- **Субагенты не могут порождать другие субагенты** (предотвращение бесконечной вложенности) `[L2]`
- **Потеря высокоуровневого контекста**: субагент может упустить стратегические цели или ограничения, известные родителю `[L3]`
- **Minimum overhead**: ~12K токенов на каждый вызов субагента (tradeoff стоимости) `[L3]`
- **Ограниченный контекст**: нет полной осведомлённости о кодовой базе `[L1]`
- Auto-compaction триггерится при ~95% ёмкости по умолчанию
- `maxTurns` ограничивает agentic turns перед принудительной остановкой

### Паттерны использования субагентов для параллелизации

- **Background subagents**: выполняются параллельно, пока пользователь продолжает работу. Пред-одобренные permissions перед запуском `[L2]`
- **Multiple research subagents**: независимые Explore-агенты для параллельного исследования `[L2]`
- **Fork mode** (`CLAUDE_CODE_FORK_SUBAGENT=1`): каждый spawn работает в background; forks разделяют prompt cache с родителем `[L2]`
- **Agent teams** (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`): workers с независимыми контекстами для устойчивого параллелизма `[L2]`

**Конфигурация субагента** через frontmatter `[L2]`:

| Поле | Описание |
|---|---|
| `name` | Уникальный идентификатор |
| `description` | Когда делегировать |
| `tools` / `disallowedTools` | White-/blacklist инструментов |
| `model` | `sonnet`, `opus`, `haiku`, `inherit` |
| `maxTurns` | Максимум agentic turns |
| `skills` | Предзагружаемые навыки |
| `mcpServers` | MCP-серверы |
| `hooks` | Lifecycle hooks субагента |
| `memory` | Персистентность: `user`, `project`, `local` |
| `isolation` | `worktree` для изолированной git-копии |
| `background` | Всегда запускать в фоне |

---

## 8. Практические рекомендации для dot_ai

### Оптимальная структура навыка (размер, секции)

На основе исследования ограничений и архитектуры Claude Code:

**Размер:**
- SKILL.md body: 500-1,500 токенов (~60-120 строк) — в sweet spot зоны внимания
- 500 строк — soft review threshold из Claude Code docs; это не жёсткий предел качества
- Description + when_to_use: до 1,536 символов — лимит truncation
- После compaction: первые 5,000 токенов сохраняются — критичное содержимое в начале

**Когда длинный навык оправдан:**
- Задача маленькая и измеримая, но требует богатого доменного контекста
- Контекст релевантен текущему действию, а не является справочником «на всякий случай»
- Критичные entry/exit условия и ограничения находятся в начале; canonical examples — в конце
- Supporting files используются для справки, API-деталей, шаблонов и edge cases
- Eval показывает выигрыш против короткой версии навыка

**Структура:**
```
SKILL.md
├── Frontmatter (name, description, when_to_use, allowed-tools)
├── Workflow Contract (entry/exit условия) — критично, в начале
├── Алгоритм работы — основной рабочий контент
├── Правила и ограничения — справочный материал, в середине
└── Примеры — в конце (для recall)
```

**Почему:** Lost in the Middle (U-образная кривая) — entry/exit условия и примеры в позициях высокого recall. Алгоритм и правила — в середине, где внимание ниже, но объём рабочий контент компенсирует.

### Когда использовать навык vs хук vs memory

| Инструмент | Когда использовать | Не использовать когда |
|---|---|---|
| **Навык** | Многошаговая процедура, workflow с этапами | Простая автоматизация, единичная проверка |
| **Хук** | Детерминированные действия: линтинг, форматирование, валидация | Логика, зависящая от понимания контекста LLM |
| **Memory** | Накопленные наблюдения: debug-паттерны, предпочтения сборки | Постоянные правила workflow (→ CLAUDE.md) |
| **CLAUDE.md** | Постоянные инструкции для каждой сессии | Временные или conditional инструкции (→ rules с paths) |
| **Rules (с paths)** | Условные инструкции по типу файлов/директорий | Универсальные правила (→ CLAUDE.md) |

### Стратегия параллелизации через субагентов

1. **Исследование**: Независимые Explore-агенты (Haiku, read-only) для параллельного сбора информации по разным аспектам задачи
2. **Валидация**: General-purpose субагенты в background для параллельной проверки нескольких гипотез
3. **Сложные задачи**: Делегирование субагентам с чистым контекстом — избегать роста контекста основного агента
4. **Сводки**: Каждый субагент возвращает сжатую сводку (~1,000-2,000 токенов), не полный output

**Анти-паттерны:**
- Запуск субагента для тривиальной задачи (overhead ~12K токенов)
- Ожидание, что субагент знает контекст родителя (изоляция контекста)
- Вложенные субагенты (невозможно — ограничение одного уровня)

### Управление контекстом: что оставлять в навыке, что выносить в memory

**В навыке:**
- Алгоритм работы (шаги, условия, проверки)
- Критичные правила (entry/exit, обязательные шаги)
- Шаблоны вывода (структура артефактов)
- 2-3 канонических примера

**В memory:**
- Debug-инсайты и паттерны, обнаруженные в работе
- Предпочтения пользователя (стиль коммуникации, уровень детализации)
- История ошибок и обходных путей
- Ссылки на внешние ресурсы

**В CLAUDE.md:**
- Глобальные правила проекта (workflow, конвенции)
- Ссылки на архитектуру и документацию
- Структура проекта и ключевые технологии

### Чеклист для создания нового навыка в dot_ai

1. **Размер**: Навык < 1,500 токенов (body) или есть eval-обоснование превышения?
2. **Позиционирование**: Entry/exit условия в первых 200 токенах?
3. **Описание**: Description + when_to_use < 1,536 символов и содержит триггеры?
4. **Правила**: 5-7 или менее поведенческих правил?
5. **Примеры**: 2-3 канонических примера вместо исчерпывающих edge cases?
6. **Сложность**: Задача в low-to-medium regime (до complexity cliff)?
7. **Изоляция**: Навык декомпозирован в одну сфокусированную операцию?
8. **Контекст**: Дополнительный контент загружается динамически (субагенты, Read)?
9. **Compaction**: Критичное содержимое survives compaction (первые 5K токенов)?
10. **Frontmatter**: `allowed-tools` пред-одобряют необходимые инструменты?
11. **Hooks**: Детерминированные валидации вынесены в hooks?
12. **Naming**: Имя навыка совпадает с trigger-фразой пользователя?

---

## Библиография

### L1 — Рецензируемые статьи

1. "Dive into Claude Code: The Design Space of Today's and Future AI Coding Assistants." arXiv:2604.14228v1
2. Liu, N.F., Lin, K., Hewitt, J., et al. "Lost in the Middle: How Language Models Use Long Contexts." TACL 2024. arXiv:2307.03172
3. Jiang, Y., Wang, Y., Zeng, X., et al. "FollowBench: A Multi-level Fine-grained Constraints Following Benchmark for Large Language Models." ACL 2024
4. Chen, X., Liao, B., Qi, J., et al. "The SIFo Benchmark: Investigating the Sequential Instruction Following Ability of Large Language Models." EMNLP Findings 2024
5. Harada, K., Yamazaki, Y., et al. "Curse of Instructions: Large Language Models Cannot Follow Multiple Instructions at Once." ICLR 2025 submission
6. Khot, T., Trivedi, H., Finlayson, M., et al. "Decomposed Prompting: A Modular Approach for Solving Complex Tasks." ICLR 2023

### L2 — Официальная документация и блоги Anthropic

1. Anthropic. "How Claude Code works." code.claude.com/docs/en/how-claude-code-works
2. Anthropic. "Tools reference." code.claude.com/docs/en/tools-reference
3. Anthropic. "Configure permissions." code.claude.com/docs/en/permissions
4. Anthropic. "How Claude remembers your project." code.claude.com/docs/en/memory
5. Anthropic. "Extend Claude with skills." code.claude.com/docs/en/skills
6. Anthropic. "Automate with hooks." code.claude.com/docs/en/hooks
7. Anthropic. "Hooks guide." code.claude.com/docs/en/hooks-guide
8. Anthropic. "Subagents." code.claude.com/docs/en/subagents
9. Anthropic. "Settings." code.claude.com/docs/en/settings
10. Anthropic. "Compaction." platform.claude.com/docs/en/build-with-claude/compaction
11. Anthropic. "Prompt caching." platform.claude.com/docs/en/build-with-claude/prompt-caching
12. Anthropic. "Effective Context Engineering for AI Agents." 2025. anthropic.com/engineering/effective-context-engineering-for-ai-agents
13. Anthropic. "Prompt Engineering for Claude's Long Context Window." 2023. anthropic.com/news/prompting-long-context

### L3 — Блоги, статьи, сообщество

1. "Adventures in Claude Code Land." medium.com/@allohvk/adventures-in-claude-code-land-f9dd85f2e072
2. "Claude Code System Prompt (GitHub Gist)." gist.github.com/chigkim/1f37bb2be98d97c952fd79cbb3efb1c6
3. "System Prompt on ZeroTwo.ai." zerotwo.ai/prompts/system-prompts/anthropic/claude-code
4. "cchistory — Claude Code prompt version tracker." cchistory.mariozechner.at
5. "Claude Code's prompt cache TTL dropped from 1h to 5m." dev.to/gabrielanhaia/claude-codes-prompt-cache-ttl-dropped-from-1h-to-5m-35g
6. "Cache cost spike issue." github.com/anthropics/claude-code/issues/51218
7. "Scoped context for subagents." github.com/anthropics/claude-code/issues/4908
8. "Claude Code Internals: The Permission System." kotrotsos.medium.com/claude-code-internals-part-8-the-permission-system-624bd7bb66b7
9. "Peeking Under the Hood of Claude Code." medium.com/@outsightai/peeking-under-the-hood-of-claude-code-70f5a94a9a62
10. "CLAUDE_CODE_SIMPLE=1 (X/Twitter)." x.com/LiorOnAI/status/2039068248390688803
