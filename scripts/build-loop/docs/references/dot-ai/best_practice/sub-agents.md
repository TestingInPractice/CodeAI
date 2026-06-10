# Sub-agents — эффективность делегирования

> **Дата:** 2026-05-07
> **Версия:** 1.0
> **Источник:** [ai-agent-mechanisms-review.md](ai-agent-mechanisms-review.md)
> **Библиография:** [summary.md](summary.md#54-библиография)

---

Sub-agents (субагенты) — механизм делегирования подзадач независимым агентам с собственным контекстным окном. В отличие от skills (упакованные промпты в том же контексте), субагенты получают чистое контекстное окно и изолированы от родительской беседы. Это создаёт уникальные trade-offs: чистый фокус vs потеря высокоуровневого понимания.

## 3.1 Изоляция контекста

Изоляция контекста субагента — одновременно главное преимущество и главный риск механизма. Ключевая аналогия: субагент — это «fresh heap» (чистая куча). Агент порождает изолированный процесс, позволяя ему обрабатывать объём «грязных» данных (чтение 20 файлов, grep, анализ логов), затем извлекает компактную сводку, а весь промежуточный контекст уничтожается (garbage collection). Родительский агент никогда не видит «мусор» `[L3]`.

**Что видит субагент** (Claude Code) `[L2]`:
- Собственный system prompt (markdown-тело навыка или explicit prompt)
- Рабочую директорию
- Разрешённые инструменты
- Предзагруженные навыки
- Первые 200 строк своего MEMORY.md

**Что НЕ видит субагент** `[L2]`:
- Историю беседы родителя
- System prompt родителя
- CLAUDE.md родителя
- Auto memory родителя
- Результаты других субагентов (если не переданы через родителя)

**Преимущества изоляции** `[L1]` `[L2]`:
- **Чистое контекстное окно** — нет «шума» от многоходовой беседы, больше budget внимания на задачу
- **Избежание Lost in the Middle** — короткий, сфокусированный контекст в sweet spot (500–2,000 токенов) `[L1]`
- **Сложные задачи становятся простыми** — complexity cliff не наступает, задача в low-to-medium regime
- **Защита от context rot** — деградация производительности при заполнении контекстного окна (tool call accumulation, stale state, debug loop residue) предотвращается архитектурно: субагент завершает работу до того, как noise накапливается `[L3]`
- **Anthropic: «Суть поиска — сжатие»** — субагенты обеспечивают сжатие, работая параллельно в собственных контекстных окнах, исследуя разные аспекты вопроса перед конденсацией наиболее важных токенов для ведущего агента `[L2]`

**Количественные данные об изоляции** `[L2]`:
- Anthropic Research (мультиагентная система): мультиагентная система с Claude Opus 4 как ведущий агент и Claude Sonnet 4 субагенты превзошли одиночного Claude Opus 4 на **90.2%** на внутреннем eval при breadth-first запросах (пример: поиск board members всех IT-компаний S&P 500) `[L2]` `[vendor]` `[Evidence Scope: Claude Opus 4 + Sonnet 4, дата: 2025, benchmark: BrowseComp (breadth-first research queries), source: vendor]`
- Три фактора объясняют **95% дисперсии** производительности на BrowseComp eval: token usage (80% дисперсии), количество tool calls, выбор модели `[L2]` `[vendor]` `[Evidence Scope: BrowseComp eval, дата: 2025, source: vendor]`
- Агенты используют примерно **4x** больше токенов, чем чат-взаимодействие; мультиагентные системы — примерно **15x** больше `[L2]` `[vendor]` `[Evidence Scope: Claude, дата: 2025, benchmark: internal Anthropic measurements, source: vendor]`

**Токеновые границы: input и output субагента** `[L2]` `[L3]`:

Субагент получает **собственное контекстное окно** полного размера модели — 200K токенов (Sonnet) или до 1M токенов (Opus 4.6) `[L2]`.

| Параметр | Значение | Обоснование |
|---|---|---|
| **Input (prompt при спавне)** | ~188K токенов (Sonnet) / ~988K (Opus) | Prompt становится первым user-сообщением в свежем контекстном окне. Минус ~12K накладных расходов на системный промпт и конфигурацию `[L2]` `[L3]` `[Evidence Scope: Claude Code, дата: 2025, benchmark: internal measurement, source: vendor + community]` |
| **Output (возврат в основной контекст)** | **Без жёсткого лимита** | Результат субагента возвращается целиком как tool result. Механизм не обрезает и не суммаризирует автоматически `[L2]` `[L3]` |
| **Minimum overhead per call** | ~12K токенов | Системный промпт + базовая конфигурация агента, независимо от объёма полезной работы `[L3]` `[community]` `[Evidence Scope: Claude Code, дата: 2025, benchmark: community measurement (token counting), source: community]` |

Ключевой риск: при возврате от нескольких параллельных субагентов их результаты **суммируются** в родительском контексте. Задокументированный кейс: 7 параллельных субагентов вернули 150 511 символов (~40–50K токенов), что переполнило родительский контекст и вызвало permanent `"Prompt is too long"` crash без возможности восстановления `[L3]`.

Практический вывод: ограничивать возврат через инструкцию в prompt (например, `"Report in under 200 words"`) — единственный способ контроля output на данный момент `[L3]`.

**Риски изоляции** `[L2]` `[L3]`:
- **Потеря стратегического контекста** — субагент не знает глобальных целей, ограничений проекта, предпочтений
- **Дублирование работы** — субагент может исследовать то, что родитель уже знает
- **Ошибка в передаче контекста** — неполный prompt субагенту → неполный результат
- **«Telephone game»** — информация искажается при прохождении через цепочку parent → sub-agent → parent. Anthropic mitigates это через файловую систему: субагенты записывают результаты в артефакты и передают lightweight references, не полные тексты `[L2]`
- **Sub-agents excel at research (90% better) но могут уступать в coding из-за context isolation** — кодирование часто требует shared working memory, которую изоляция разрушает `[L3]`

**Исключение — Forks** `[L2]`:
- Fork наследует **всю беседу** (system prompt, инструменты, модель, историю сообщений)
- Forks разделяют prompt cache с родителем
- Trade-off: fork сохраняет контекст, но несёт overhead полной беседы

## 3.2 Параллелизация

Параллельные субагенты могут ускорить работу, но не всегда. Ключевой инсайт: **субагенты — это не механизм параллельного ускорения. Это механизм сборки мусора в контексте** (context garbage collection). Цель — выбросить noise, а не разделить мышление `[L3]`.

**Когда параллелизация ускоряет** `[L2]`:
- **Независимые исследования** — Explore-агенты для параллельного сбора информации по разным аспектам
- **Валидация** — параллельная проверка нескольких гипотез
- **Read-only операции** — поиск файлов, чтение документации, анализ кода
- Claude Code: background subagents выполняются параллельно, пока пользователь продолжает работу
- Anthropic Research: параллелизация сократила время исследования до **90%** для сложных запросов (ведущий агент порождает 3–5 субагентов одновременно, каждый субагент использует 3+ инструмента параллельно) `[L2]`

**Когда параллелизация добавляет overhead** `[L2]` `[L3]`:
- **Зависимые задачи** — если задача B требует результат задачи A, параллелизация бессмысленна
- **Overhead агрегации** — родитель должен синтезировать результаты всех субагентов (стоимость синтеза)
- **Token overhead** — каждый субагент потребляет ~12K токенов на запуск; 5 параллельных = 60K токенов overhead `[L3]`
- **Конкуренция за ресурсы** — при множестве background агентов могут быть rate limits и throttling
- **52 controlled benchmarks: Agent Teams стоят на 73–124% больше токенов, чем последовательное выполнение, при нулевом улучшении качества** `[Evidence Scope: unspecified models, дата: 2026, benchmark: 52 controlled benchmarks, source: community measurement]`. Каждый агент загружает собственный контекст, token consumption масштабируется линейно с числом параллельных агентов `[L3]` `[community]`
- **Мультиагентные системы деградируют на 39–70% на задачах последовательного reasoning** — параллелизация полезна только для параллелизуемых задач `[L3]` `[community]` `[Evidence Scope: unspecified models, дата: 2026, benchmark: sequential reasoning tasks, source: community measurement]`
- **Agent drift (Rath, 2026)** `[L1]` `[peer-reviewed]`: 67–81% эскалация ошибок в поведении мультиагентных LLM-систем при продолжительных взаимодействиях `[Evidence Scope: мультиагентные LLM-системы, дата: 2026, benchmark: prolonged interaction analysis, source: peer-reviewed]`. Без mitigation (episodic memory, drift-aware routing, behavioral contracts) производительность систематически деградирует

**Количественные данные о параллелизации** `[L1]` `[L2]` `[L3]`:

| Метрика | Значение | Источник |
|---|---|---|
| Agent Teams: рост стоимости | 73–124% vs sequential | 52 benchmarks, Reddit 2026 `[L3]` `[community]` |
| Agent Teams: улучшение качества | 0% (ноль) | 52 benchmarks, Reddit 2026 `[L3]` `[community]` |
| CONTRACT.md: снижение стоимости | 54% | 52 benchmarks, Reddit 2026 `[L3]` `[community]` |
| CONTRACT.md: улучшение качества | 5/10 → 9/10 | 52 benchmarks, Reddit 2026 `[L3]` `[community]` |
| Мультиагент vs single: breadth-first | +90.2% на research eval | Anthropic Research `[L2]` `[vendor]` |
| Деградация sequential reasoning | 39–70% | Openlayer Guide, 2026 `[L3]` `[community]` |
| Agent drift: error escalation | 67–81% | Rath, arXiv:2601.04170 `[L1]` `[peer-reviewed]` |
| Время исследования (parallel) | –90% для сложных запросов | Anthropic Research `[L2]` `[vendor]` |
| Token overhead per sub-agent | ~12K токенов | Community measurements `[L3]` `[community]` |

**Паттерны параллелизации** `[L2]`:

| Паттерн | Когда использовать | Модель |
|---|---|---|
| Map-reduce | Независимые подзадачи, сведение результатов | Haiku для map, Opus для reduce |
| Параллельный поиск | Исследование разных аспектов кодовой базы | Explore (Haiku, read-only) |
| Валидация гипотез | Параллельная проверка нескольких подходов | General-purpose (наследует модель) |
| Background processing | Длительные операции, не блокирующие пользователя | General-purpose в background |

## 3.3 Стоимость делегирования

Каждый вызов субагента имеет фиксированную стоимость, независимо от сложности задачи. Breakeven point: примерно **10,000 input токенов** на вызов `[heuristic]` `[Evidence Scope: Claude Code, дата: 2025, расчёт: ~12K overhead / ~2K полезной работы, source: community estimation]`. Если субагент выполняет только 2,000 токенов полезной работы, overhead превышает саму работу `[L3]` `[community]`.


## 3.4 Ограничение вложенности

**Одноуровневые субагенты — практический максимум** `[L1]` `[L2]`:

- Claude Code: субагенты **не могут порождать другие субагенты** — ограничение одного уровня вложенности `[L2]`
- Это не техническое ограничение, а архитектурное решение: многоуровневая вложенность порождает exponential overhead

**Почему многоуровневая вложенность нежелательна:**

- **Exponential overhead**: каждый уровень добавляет ~12K токенов. 2 уровня = 12K x 2 + результаты промежуточного
- **Information loss на каждом уровне**: «telephone game» — информация искажается при передаче между уровнями
- **Complexity cliff на уровне orchestration**: координация многоуровневых субагентов — сама по себе сложная задача
- **Debugging impossible**: ошибка в 3-м уровне вложенности практически недиагностируема
- **Agent drift compound**: 67–81% error escalation усугубляется с каждым уровнем вложенности — промежуточные агенты накапливают drift, передавая его далее `[L1]`
- **Emergent behaviour**: малые изменения в ведущем агенте непредсказуемо меняют поведение субагентов, что ещё более выражено при вложенности. Anthropic: «Multi-agent systems have emergent behaviors which arise without specific programming» `[L2]`

**Anthropic: emergent behavior и single-level safety** `[L2]`:
- Ранние версии Research feature порождали **50 субагентов для простых запросов**, бесконечно искали несуществующие источники, и distract'или друг друга чрезмерными обновлениями
- Решение: встроенные в промпты scaling rules: simple fact-finding = 1 agent / 3–10 tool calls; direct comparisons = 2–4 subagents / 10–15 calls; complex research = 10+ subagents
- Вывод: без explicit guardrails субагенты склонны к over-spawning — ограничение вложенности — один из таких guardrails

**«When Does Divide and Conquer Work»** применительно к субагентам `[L1]`:
- Декомпозиция работает, когда шаг синтеза — низкой сложности
- Одноуровневая модель: parent → N sub-agents → parent синтезирует (один шаг синтеза)
- Многоуровневая модель: parent → sub1 → sub-sub1 → sub1 → parent (много шагов синтеза = деградация)
- Мультиагентные системы превосходят одиночных агентов на **параллелизуемых задачах**, но деградируют на **39–70% на задачах последовательного reasoning** `[L3]`

## 3.5 Модели субагентов

Выбор модели для субагента — оптимизация стоимости vs качества. Ключевой принцип: **маршрутизация по decision complexity, не по input volume** `[L3]`.

**Claude Code: три уровня моделей** `[L2]`:

| Тип субагента | Модель | Стоимость | Назначение |
|---|---|---|---|
| Explore | Haiku (быстрый, дешёвый) | Низкая | Поиск файлов, grep, чтение кода |
| Plan | Наследует от родителя | Средняя/высокая | Исследование для планирования |
| General-purpose | Наследует от родителя | Средняя/высокая | Сложные многошаговые задачи |
| claude-code-guide | Haiku | Низкая | Ответы на вопросы о Claude Code |

**Обоснование Haiku для поиска** `[L2]`:
- Read-only операции не требуют reasoning — достаточно retrieval capabilities
- Haiku значительно быстрее и дешевле — оптимально для mass file scanning
- Качество поиска файлов и чтения кода сопоставимо с более мощными моделями

**Обоснование наследования модели для Plan/General-purpose** `[L2]`:
- Планирование и реализация требуют reasoning capabilities родительской модели
- Если родитель — Opus, субагент для сложной задачи тоже должен быть Opus
- Override через frontmatter: `model: haiku` для простых задач, `model: opus` для критичных

**Routing table: Opus / Sonnet / Haiku по типу задачи** `[L2]` `[L3]`:

| Задача | Input complexity | Decision complexity | Модель | Обоснование |
|---|---|---|---|---|
| Grep/search files | Низкая | Низкая | Haiku | Retrieval, не reasoning |
| Log classification (100K → 200 tokens) | Высокая | Низкая | Haiku | High input, low output, stateless |
| Code review | Средняя | Средняя | Sonnet | Баланс speed/quality |
| Test writing | Средняя | Средняя | Sonnet | Pattern-based, moderate reasoning |
| Architecture planning | Низкая | Высокая | Opus | Judgment compounds |
| Security audit | Высокая | Высокая | Opus | Complex reasoning required |
| Final report generation | Средняя | Высокая | Opus | Quality-critical synthesis |

**Aider: Architect/Editor split — эмпирические данные** `[L2]` `[vendor]`:
- Разделение «code reasoning» (Architect) и «code editing» (Editor) обеспечивает SOTA результаты
- o1-preview Architect + o1-mini Editor: **85.0%** на code editing benchmark (SOTA) `[Evidence Scope: Aider benchmark, дата: 2024, benchmark: code editing (SWE-bench), source: vendor]`
- o1-preview Architect + DeepSeek Editor: **85.0%** (аналогично) `[Evidence Scope: там же]`
- o1-preview Architect + Claude 3.5 Sonnet Editor: **82.7%** `[Evidence Scope: там же]`
- Claude 3.5 Sonnet как Architect+Editor: **80.5%** (vs 77.4% baseline = +3.1pp от split) `[Evidence Scope: там же]`
- GPT-4o как Architect+Editor: **75.2%** (vs 71.4% baseline = +3.8pp от split) `[Evidence Scope: там же]`
- GPT-4o-mini как Architect+Editor: **60.2%** (vs 55.6% baseline = +4.6pp от split) `[Evidence Scope: там же]`
- Вывод: даже идентичная модель показывает улучшение при Architect/Editor split (3–5 процентных пунктов)

**Anthropic Research: model-as-efficiency-multiplier** `[L2]`:
- Переход с Claude Sonnet 3.7 на Claude Sonnet 4 даёт больший прирост производительности, чем удвоение token budget
- Это обосновывает архитектуру: Haiku для массового поиска + Sonnet/Opus для synthesis, а не дешёвая модель везде

## 3.6 Сравнение субагентных архитектур

| Инструмент | Субагентный механизм | Уровни вложенности | Моделирование | Ключевая особенность |
|---|---|---|---|---|
| **Claude Code** | Explore/Plan/General-purpose субагенты через инструмент Agent. До 6 встроенных типов: Explore, Plan, General-purpose, Bash, Claude Code Guide + кастомные `[L2]` | 1 уровень (субагент не порождает субагентов) | Haiku (Explore), inherit (Plan/General-purpose) `[L2]` | Истинная изоляция контекста, каждый субагент = собственное контекстное окно |
| **Cursor** | Subagents (v2.4+), async subagents (v2.5), Background/Cloud Agents (v3.0) `[L2]` | 1 уровень | Context Window: стандартный ~128-150K, Max Mode до 1M `[L2]` `[L3]` | Параллельные независимые агенты с собственными контекстными окнами; seamless handoff между агентами в v3.0 |
| **Aider** | Architect/Editor split (разные роли, одна или две модели) `[L2]` | 0 уровней (role split, не изоляция) | Две модели: Architect (reasoning) + Editor (editing). SOTA 85% `[L2]` | Разделение reasoning и editing, модели могут быть разными; share context |
| **Copilot** | Agent mode, custom agents с scoped tools/prompts, sub-agent orchestration через SDK `[L2]` | 1 уровень (coding agent) | Модель Copilot, task-level orchestration. Mission control для multi-agent `[L2]` | Orchestrator делегирует специализированным sub-agents; VS Code нативная интеграция |

**Ключевое различие: изоляция vs role split** `[L2]`:
- Claude Code: **истинная изоляция** — субагент имеет собственное контекстное окно, не видит родителя
- Aider: **role split** — architect и editor разделяют контекст, но играют разные роли в одном окне
- Cursor: **context management** — Agent mode использует полный контекст, Cmd-K — короткий; v3.0 добавляет seamless handoff
- Copilot: **orchestrated delegation** — primary orchestrator делегирует specialized sub-agents (logic, testing, docs), но sub-agents могут наследовать orchestrator context вместо собственных инструкций `[L3]`
- Trade-off: изоляция даёт фокус, role split даёт полноту контекста

**Сходимость архитектур** `[L2]` `[L3]`:
- Все основные инструменты движутся к одной модели: orchestrator + специализированные workers
- Anthropic: orchestrator-worker pattern как рекомендуемый для complex tasks `[L2]`
- Cursor: эволюция от agent mode → subagents → async background → cloud agents with handoff
- Copilot: Mission control pattern для координации множества агентов
- Общий паттерн: **single-level flat hierarchy** с orchestrator наверху и специализированными workers

## 3.7 Предопределённая команда vs. динамическое создание

Два фундаментальных подхода к формированию субагентной команды: **предопределённые роли** (predefined agents — фиксированный набор агентов с заданными промптами, инструментами и зонами ответственности) и **динамическое создание на лету** (dynamic spawning — орхестратор порождает субагенты в рантайме, определяя их количество, задачи и конфигурацию на основе входного запроса).

**Предопределённая команда (predefined agents)**:

Преимущества:
- Предсказуемость поведения и легче отладка — каждый агент имеет стабильный промпт и инструментарий `[L2]`
- Каждый агент получает специализированный промпт, инструменты и границы ответственности → выше точность на известных типах задач `[L2]`
- Меньше оверхед на координацию и расход токенов — фиксированный набор агентов не требует runtime-решений о порождении `[L1]`

Недостатки:
- Не адаптируется к задачам, не предусмотренным при проектировании — система «слепа» к задачам вне предопределённых ролей `[L1]`
- Риск дублирования работы или пробелов при расплывчатых инструкциях — Anthropic: *"subagents performed the exact same searches as other agents... without an effective division of labor"* `[L2]`

**Динамическое создание «на лету» (dynamic spawning)**:

Преимущества:
- Оркестратор адаптирует количество и тип субагентов под сложность конкретного запроса `[L2]`
- Для открытых задач (исследование, кодинг в неизвестном репо) — непредсказуемость подзадач делает динамический подход единственным жизнеспособным: *"you can't hardcode a fixed path for exploring complex topics"* `[L2]`
- Мультиагентная система с динамическим порождением превосходит одиночного агента на **90.2%** в бенчмарке BrowseComp `[L2]`
- Динамическое назначение ролей демонстрирует лучшие результаты, чем статическое, в задачах multi-agent debate `[L1]`

Недостатки:
- Расход токенов: мультиагентные системы потребляют ~15x больше токенов, чем обычный чат `[L2]`
- Выше риск эмерджентного нежелательного поведения — *"small changes to the lead agent can unpredictably change how subagents behave"* `[L2]`
- Сложнее отладка и тестирование — непредсказуемые пути выполнения `[L2]`

**Сравнительная таблица** `[L1]` `[L2]`:

| Критерий | Предопределённая команда | Динамическое создание |
|---|---|---|
| Тип задачи | Структурированные, повторяющиеся | Открытые, непредсказуемые |
| Отладка | Простая (детерминированные пути) | Сложная (непредсказуемые пути) |
| Расход токенов | Умеренный (фиксированный набор) | Высокий (15x vs чат) |
| Адаптивность | Низкая | Высокая |
| Параллелизм | Ограничен известными ролями | Масштабируется под задачу |
| Риск over-spawning | Низкий | Высокий (50 агентов для простых запросов) `[L2]` |

**Оптимальный паттерн — гибрид** `[L2]`:
Anthropic Research использует предопределённые роли (LeadResearcher, Subagent, CitationAgent), но динамическое количество и конфигурацию субагентов, определяемую оркестратором на лету. Это даёт стабильность предопределённых ролей + адаптивность динамического масштабирования. Anthropic формулирует принцип: workflow-паттерны (predefined) — для предсказуемых задач, агенты (dynamic) — для открытых `[L2]`.

**Количественные данные** `[L1]` `[L2]`:

| Метрика | Значение | Источник |
|---|---|---|
| Динамический мультиагент vs single agent (research) | +90.2% | Anthropic Research `[L2]` |
| Token usage объясняет дисперсию производительности | 80% | BrowseComp eval `[L2]` |
| Agent drift при динамической координации | 67–81% error escalation | Rath, arXiv:2601.04170 `[L1]` |
| AOrchestra: динамическое порождение vs predefined team | +12–18% на открытых задачах | arXiv:2602.03786 `[L1]` |
| AgentSpawn: адаптивное порождение по сложности | Снижение token waste на 34% | arXiv:2602.07072 `[L1]` |
| Dynamic role assignment vs static (debate) | +8.3% на argument quality | arXiv:2601.17152 `[L1]` |

## 3.8 Предопределённые агенты со структурированным output

Ключевой инсайт: **предопределённые агенты с жёстким форматом возврата превосходят ad-hoc Explore-агентов со свободным текстом**. Anthropic: *"each subagent needs an objective, an output format, guidance on the tools and sources to use, and clear task boundaries"* `[L2]`. Это реализует AOrchestra 4-кортеж `(Instruction, Context, Tools, Model)` на практике `[L1]`.

### Проблема: ad-hoc Explore-агенты

Текущий подход в implement-spec-stage (Фаза 2): два Explore-агента с inline-описанием роли:
- **Code Mapper** — «читает все файлы этапа»
- **Data Flow Tracer** — «трассирует потоки данных»

Explore-агент — универсальный поиск. Output — свободный текст без гарантии структуры. При сложных этапах основной агент теряет информацию при интерпретации неструктурированного результата `[L3]`.

### Решение: предопределённые агенты в `.claude/agents/`

Каждый агент — одна ответственность, один формат возврата, фиксированный набор инструментов.

Агенты в `.claude/agents/*.md` загружаются **один раз при старте сессии** `[L2]` `[L3]`. Для dot_ai workflow это не проблема — агенты известны заранее и устанавливаются при init. Workaround для runtime: **Impersonator-паттерн** — промежуточный агент читает `.claude/agents/*.md` и имитирует ещё не загруженного агента `[L3]`.

**Шаблон: code-mapper**

```yaml
# .claude/agents/code-mapper.md
---
name: code-mapper
description: >
  Карта структуры кода для файлов/модулей этапа.
  Структурированный output: таблицы файлов, импортов, DTO, зависимостей.
  Вызывать перед реализацией каждого этапа ТЗ.
tools: Read, Glob, Grep
model: haiku
---

## Цель
Собрать полную карту кода для указанных целевых файлов.

## Обязательный формат output

## Code Map: {название этапа}

### Файлы
| Файл | Класс/модуль | Назначение |
|---|---|---|
| ... | ... | ... |

### Импорты
| Откуда | Что | Куда |
|---|---|---|
| ... | ... | ... |

### DTO/Контракты
| Имя | Поля | Используется в |
|---|---|---|
| ... | ... | ... |

### Зависимости
- {файл} зависит от: {список}
- {файл} используется в: {список}

### Образец
Файл-образец: {путь}
Причина: {почему подходит как шаблон}

## Правила
- Читай КАЖДЫЙ целевой файл полностью
- Если файл не найден — явно укажи
- Не пропускай импорты и type hints
- Образец не найден — напиши явно
```

**Шаблон: data-flow-tracer**

```yaml
# .claude/agents/data-flow-tracer.md
---
name: data-flow-tracer
description: >
  Трассировка потоков данных между модулями этапа.
  Структурированный output: Input → Transform → Output цепочка.
  Вызывать параллельно с code-mapper.
tools: Read, Grep, Glob
model: haiku
---

## Обязательный формат output

## Data Flow: {название этапа}

### Входные данные
| Источник | Тип данных | Формат |
|---|---|---|
| ... | ... | ... |

### Трансформации
Шаг 1: {описание} — {файл}:{функция}
Шаг 2: {описание} — {файл}:{функция}

### Выходные данные
| Приёмник | Тип данных | Формат |
|---|---|---|

### Аналогичный поток
Файл: {путь}
Сходство: {описание}

## Правила
- Начинай от entry point этапа
- Трассируй до storage/API/выхода
- Цепочка обрывается — укажи где
```

**Сравнение** `[L2]` `[L3]`:

| Критерий | Ad-hoc Explore | Предопределённый агент |
|---|---|---|
| Формат output | Свободный текст | Структурированные таблицы |
| Воспроизводимость | Разный результат | Стабильный формат |
| Проверяемость | Сложно проверить полноту | Пробелы видны в таблице |
| Промпт | Inline в skill | Отдельный, оттестированный |
| Overhead | 0 (уже есть) | +2 файла агентов при init |
| Проверка достаточности | 5 критериев вручную | Таблица → автоматически видно |

**Справочно: механизмы Claude Code для агентов** `[L2]` `[L3]`:

| Механизм | Когда создаётся | Контекст | Применимость для dot_ai |
|---|---|---|---|
| `.claude/agents/*.md` | При старте сессии | Изолированный | Основной — агенты-трассировщики |
| `--agents` CLI flag | При старте CLI | Изолированный | Для скриптов/CI |
| Impersonator | В runtime (workaround) | Через impersonator | Если нужен runtime agent |
| Fork | В runtime | Полный клон родителя | Когда нужен shared context |
| Agent Teams (эксп.) | В runtime | Inter-agent SendMessage | Пока экспериментальный |
| `general-purpose` + prompt | В runtime | Изолированный, custom prompt | Эквивалент динамического агента |

## 3.9 Анти-паттерны

**1. Делегирование тривиальных задач** `[L2]` `[L3]`:
- Запуск субагента для задачи «найди файл X» — overhead 12K токенов для ~200-токенной задачи
- Если overhead_ratio > 0.3, субагент не окупается `[L3]`
- Решение: тривиальные задачи выполнять в основном контексте через Glob/Grep/Read

**2. Ожидание знания контекста родителя** `[L2]` `[L3]`:
- Субагент не знает историю беседы, CLAUDE.md, memory родителя
- Анти-паттерн: «сделай X так, как мы обсуждали ранее» — субагент не знает, что обсуждалось
- Copilot: sub-agents склонны следовать orchestrator prompt, даже когда их собственный description говорит обратное `[L3]`
- Решение: передавать ВСЮ необходимую информацию в prompt субагента

**3. Чрезмерная параллелизация** `[L2]` `[L3]`:
- 10+ параллельных субагентов → rate limits, throttling, сложность агрегации
- Каждый субагент = ~12K токенов overhead + стоимость ответа
- Agent Teams: 73–124% больше токенов, нулевое улучшение качества — structured prompting (CONTRACT.md) эффективнее `[L3]`
- «Too many chefs»: длинный список агентов dilutes relevance signals, delegating model тратит cycles на выбор агентов вместо продуктивной работы `[L3]`
- Решение: ограничить параллелизацию 3–5 независимыми задачами

**4. Вложенные субагенты** `[L1]` `[L2]`:
- Многоуровневая вложенность → exponential overhead, information loss, debugging impossible
- Решение: строго одноуровневая модель, сложные задачи — декомпозировать через workflow, не через nesting

**5. Over-spawning** `[L2]`:
- Без explicit guardrails субагенты склонны к over-spawning: Anthropic Research отмечал 50 субагентов для простых запросов в ранних версиях `[L2]`
- Решение: embedded scaling rules в промптах (1 agent для simple, 2–4 для medium, 10+ только для complex)

**6. Tool-scope confusion** `[L3]`:
- Предоставление всех инструментов каждому агенту создаёт noise: модель выбирает неподходящий инструмент или не может решить, какой использовать
- Решение: ограничивать инструменты по роли агента (Explore = read-only, General-purpose = full tools)

**7. Opaque inner workings** `[L3]`:
- Внутренние tool calls и промежуточные мысли субагента скрыты. При потреблении 50K+ токенов нет incremental visibility, что делает debugging невозможным
- Решение: production tracing на уровне субагентов, observability decision patterns

**8. Inconsistent activation** `[L3]`:
- Субагенты часто игнорируются моделью, если не названы явно. Auto-selection работает только иногда, «fire-and-forget» delegation ненадёжна
- Решение: explicit naming + конкретные триггеры в description

## 3.10 Multi-Agent Systems: фреймворки и бенчмарки

### AgentBench: оценка LLM-as-Agent

**AgentBench** (Liu et al., Tsinghua/THUDM, ICLR 2024) `[L1]` `[peer-reviewed]`:
- Первый бенчмарк для оценки LLM-as-Agent **в нескольких реальных средах**: ОС, база данных, knowledge graph, web browsing
- Разные среды используют разные метрики: success rate для OS/БД, accuracy для QA
- Ключевой вывод: frontier-модели показывают высокие результаты в controlled settings, но производительность значительно варьируется между средами
- Подтверждает: способность модели следовать инструкциям в одной среде не гарантирует аналогичную производительность в другой `[Evidence Scope: frontier-модели, дата: 2024, benchmark: multi-environment agent tasks, source: peer-reviewed]`

### ChatDev: коммуникативные агенты для разработки ПО

**ChatDev** (Chen et al., ACL 2024) `[L1]` `[peer-reviewed]`:
- Фреймворк «виртуальной софтверной компании»: специализированные LLM-агенты (CTO, programmer, tester, art designer) общаются через structured multi-turn dialogues
- Моделирует waterfall-процесс через чат: requirements → design → coding → testing
- Практические ограничения: коммуникационные overhead, error propagation через chain of agents, качество зависит от полноты ролей
- ChatDev 2.0 (DevAll): эволюция в zero-code multi-agent platform `[L2]` `[vendor]`

**AgentVerse** (OpenBMB/Tsinghua) `[L1]` `[peer-reviewed]`:
- Инфраструктурный фреймворк для ChatDev: предоставляет multi-agent runtime
- Поддерживает определение ролей, инструментов и протоколов коммуникации

### MetaGPT и CAMEL: collaborative agents

**MetaGPT** (Hong et al., ICLR 2024) `[L1]` `[peer-reviewed]`:
- Meta-programming фреймворк: присваивает агентам роли (Product Manager, Architect, Engineer) с SOP (Standard Operating Procedures)
- Ключевой инсайт: **structured collaboration protocols** (SOP) критичны для предотвращения хаоса в multi-agent системах
- Показывает: добавление даже простых organizational constraints (определённый порядок коммуникации, формат output) значительно повышает качество результата

**CAMEL** (Li et al., NeurIPS 2023) `[L1]` `[peer-reviewed]`:
- Communicative Agents for Mind Exploration of Large Language Model Society
- Исследует cooperative role-playing: два агента с разными ролями общаются для решения задачи
- Показывает: role assignment через prompting (без fine-tuning) создаёт emergent collaboration

### AutoGen (Microsoft)

**AutoGen** (Wu et al., 2023) `[L2]` `[vendor]`:
- Multi-agent framework от Microsoft Research: гибрид human-in-the-loop + autonomous agents
- Поддерживает customizable agents, flexible conversation patterns, code execution
- Ключевой паттерн: **multi-agent conversation** как primary abstraction
- Auto-SLURP (EMNLP 2025 Findings) `[L1]` `[peer-reviewed]`: бенчмарк для оценки multi-agent frameworks в контексте intelligent personal assistants

### Single-agent vs Role split vs Isolated subagents

Сравнение трёх архитектурных подходов:

| Критерий | Single-agent (monolith) | Role split (Aider) | Isolated subagents (Claude Code) |
|---|---|---|---|
| Контекст | Полный, но шумный | Общий, разделение ролей | Изолированный, чистый |
| Coordination overhead | Минимальный | Низкий | Средний-высокий |
| Адаптивность | Низкая | Средняя | Высокая |
| Отладка | Простая | Средняя | Сложная |
| Token cost | Низкий | Средний | Высокий (~12K per agent) `[L3]` |
| Качество на известных задачах | Среднее | Высокое (+3–5pp от split) `[L2]` | Высокое (+90% на breadth-first) `[L2]` |
| Качество на неизвестных | Низкое | Среднее | Высокое |

**Эмпирическое сравнение** `[L1]` `[L2]`:
- Aider Architect/Editor split: +3–5 процентных пунктов на code editing при идентичной модели `[L2]` `[vendor]` `[Evidence Scope: o1-preview/o1-mini/GPT-4o, дата: 2024, benchmark: code editing (Aider), source: vendor]`
- Claude Code мультиагент: +90.2% на breadth-first research vs single agent `[L2]` `[vendor]` `[Evidence Scope: Claude Opus 4 + Sonnet 4, дата: 2025, benchmark: BrowseComp, source: vendor]`
- Agent Teams (52 benchmarks): 73–124% больше токенов, 0% улучшение качества на непараллелизуемых задачах `[L3]` `[community]` `[Evidence Scope: unspecified models, дата: 2026, benchmark: 52 controlled benchmarks, source: community measurement]`

### Практический вывод для dot_ai

1. **Structured SOP (MetaGPT)** — подтверждает dot_ai подход: определённый порядок workflow с ENTRY/EXIT условиями эффективнее хаотичной координации `[hard]` `[L1]` `[peer-reviewed]`
2. **Isolated subagents превосходят на research-задачах**, но не на coding — dot_ai правильно использует subagents для исследования (Explore), не для генерации кода `[hard]` `[L2]` `[vendor]`
3. **Role split (Aider)** — более экономичный паттерн чем изоляция: +3–5pp при 0 дополнительного overhead на контекст `[heuristic]` `[L2]` `[vendor]`
4. **Multi-agent overhead** реален: для непараллелизуемых задач (coding, sequential reasoning) мультиагентность добавляет стоимость без улучшения `[hard]` `[L1]` `[L3]`

## 3.11 Практические рекомендации

1. **Делегируй, когда задача >5 логических операций** — чистый контекст избегает complexity cliff `[hard]` `[L1]` `[peer-reviewed]`
2. **Не делегируй тривиальные задачи** — overhead 12K токенов неоправдан для <2 шагов `[heuristic]` `[L3]` `[community]`
3. **Передавай полный контекст в prompt** — субагент не знает ничего, кроме того, что ему передали `[hard]` `[L2]` `[vendor]`
4. **Haiku для поиска, Opus/Sonnet для reasoning** — match модели к сложности задачи `[heuristic]` `[L2]` `[vendor]`
5. **Ограничь параллелизацию 3–5 агентами** — больше → overhead агрегации и rate limits `[heuristic]` `[L2]` `[vendor]`
6. **Строго одноуровневая вложенность** — декомпозиция через workflow, не через nesting `[hard]` `[L1]` `[peer-reviewed]`
7. **Субагент возвращает сводку ~1,000–2,000 токенов** — не полный output `[heuristic]` `[L2]` `[vendor]`
