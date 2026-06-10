# Rules — эффективность инструкций и правил

> **Дата:** 2026-05-07
> **Версия:** 1.0
> **Источник:** [ai-agent-mechanisms-review.md](ai-agent-mechanisms-review.md)
> **Библиография:** [summary.md](summary.md#54-библиография)

---

Rules (правила) — самый распространённый механизм управления AI-агентами. Каждая инструкция в system prompt, CLAUDE.md или .cursorrules — это попытка вероятностного управления поведением модели. Эмпирические данные показывают как возможности, так и фундаментальные ограничения этого подхода.

## 1.1 Instruction following compliance

Модели не следуют инструкциям с абсолютной точностью. Это не баг конкретной реализации, а следствие архитектуры Transformer и методологии RLHF-обучения.

**«Curse of Instructions»** (Harada et al., ICLR 2025) `[L1]` `[peer-reviewed]`:
- LLM не способны одновременно следовать множеству инструкций — добавление правил ухудшает compliance по каждому индивидуальному правилу
- Эффект наблюдается у всех протестированных моделей, не зависит от размера модели
- Практическое следствие: файл с 20+ поведенческими правилами покажет ухудшение compliance по сравнению с 5-7 приоритизированными

**«The Instruction Hierarchy»** (Wallace, Xiao et al., OpenAI, NeurIPS 2024) `[L1]` `[peer-reviewed]`:
- Без специального обучения LLM не соблюдают иерархию приоритетов между system prompt, developer instructions и user messages
- Пользовательские промпты могут переопределять системные инструкции безопасности
- Разработчики AI-coding-ассистентов должны закладывать enforcement не на уровне инструкций, а на уровне архитектуры (hooks, permissions)

**«The Failure of Instruction Hierarchies in Large Language Models»** (AAAI) `[L1]` `[peer-reviewed]`:
- Даже с целенаправленным обучением, разделение system/user prompt **не обеспечивает надёжной иерархии инструкций**
- Модели демонстрируют сильные внутренние смещения (internal biases), подрывающие предполагаемую структуру приоритетов
- Вывод: даже хорошо спроектированные workflow-системы не могут гарантировать соблюдение высокоприоритетных инструкций через prompt engineering один

**«The Instruction Gap»** (Tripathi et al., 2025) `[L1]` `[peer-reviewed]`:
- Оценка 13 ведущих LLM показала драматическую вариацию в instruction compliance
- Модели демонстрируют высокие результаты на общих задачах, но struggle с точным следованием инструкциям
- Claude-Sonnet-4 и GPT-5 показали наивысшие результаты compliance, но ни одна модель не достигла >95% на строгих бенчмарках
- «Instruction gap» — фундаментальный разрыв между способностью модели понимать инструкцию и способностью её выполнять

**«When Thinking Fails: The Pitfalls of Reasoning for Instruction-Following in LLMs»** (Amazon Science, 2025) `[L1]` `[peer-reviewed]`:
- Первое систематическое исследование reasoning-induced failures в instruction following
- Расширенный reasoning (chain-of-thought) может **ухудшать** точность следования инструкциям
- Reasoning-усиление одной стороны задачи (например, точности ответа) может снижать compliance по другим измерениям (формат, длина, стиль)

**ReasonIF benchmark** (Together AI, 2025) `[L1]` `[preprint]`:
- Frontier Large Reasoning Models не следуют reasoning-инструкциям в >75% случаев
- Протестировано across languages, formatting и другие размерности
- Подтверждает паттерн: reasoning-модели не получают автоматически лучший instruction compliance

## 1.2 Формат и структура инструкций

Формат, в котором правила представлены модели, влияет на compliance. Однако эффект нелинеен и зависит от контекста.

**«How You Prompt Matters!» (EMNLP 2024 Findings)** `[L1]` `[peer-reviewed]`:
- Ограничения, добавленные для улучшения одного измерения (например, точности), часто ухудшают другое (например, compliance с форматом)
- Минимальные вариации в формулировках системного промпта влияют на многоходовые диалоги
- Вывод: «оптимальный» набор инструкций — это не максимум правил, а баланс между ними

**Структурирование секций** `[L2]` `[vendor]`:
- XML-теги (`<rule>...</rule>`) и Markdown-заголовки (`## Правило N`) помогают модели парсить границы секций
- Anthropic рекомендует найти «наименьший набор высокосигнальных токенов, максимизирующих вероятность желаемого результата»
- Структурированный формат вывода (markdown/XML) снижает форматные галлюцинации

**Progressive disclosure** `[L2]` `[vendor]`:
- Размещение критичного контента первым, справочного — по запросу
- Lazy loading (загрузка по мере необходимости) предпочтительнее eager loading (всё сразу)
- Навыки в Claude Code поддерживают этот паттерн: frontmatter-описание загружается всегда, тело навыка — при активации

## 1.3 Размер vs точность

Ключевая закономерность: больше инструкций ≠ лучше compliance. Существует «sweet spot» после которого добавление правил ухудшает результат.

**Curse of Instructions (подтверждение)** `[L1]`:
- Комpliance деградирует с ростом числа одновременных инструкций
- Феномен модельно-независимый — наблюдается у всех протестированных моделей

**Зоны производительности по размеру промпта** `[L2]` `[L3]`. **Примечание:** численные границы — community measurement, не универсальные пороги `[heuristic]`:

| Зона | Токены | Поведение |
|------|--------|-----------|
| Sweet spot | 500–2,000 | Оптимальная производительность, наивысшая точность |
| Убывающая отдача | 2,000–4,000 | На 40-80% медленнее `[Evidence Scope: unspecified model, дата: 2025, benchmark: single project Q&A, source: community measurement]`, 2-3% прирост при удвоении |
| Активная деградация | 4,000+ | Измеримое снижение качества, пропущенные детали |

**Оптимизация правил — количественные данные** `[L3]` `[community]`:
- Arize AI (SWE-bench Lite, Claude Code): by-repo split (general coding) — **+5.19%** accuracy от оптимизации CLAUDE.md; in-repo split (repo-specific) — **+10.87%** `[Evidence Scope: SWE-bench Lite, Claude Code, модель/дата не указаны, benchmark: SWE-bench Lite (code generation), source: community measurement]`. Без изменений архитектуры или fine-tuning, чистая prompt-оптимизация
- Ключевой фактор — не количество правил, а их приоритизация и отсутствие противоречий

**Оптимальное количество правил** `[heuristic]` `[L2]` `[L3]`:
- Anthropic: «context — конечный ресурс с убывающей отдачей»
- Практический консенсус: 5–7 ключевых поведенческих правил на один навык/контекст `[Evidence Scope: frontier-модели, дата: 2025, benchmark: Curse of Instructions ICLR 2025, source: peer-reviewed]`
- При превышении — каждое новое правило снижает compliance по остальным

## 1.4 Позиционирование критичного контента

**Lost in the Middle** (Liu et al., 2023, TACL 2024) `[L1]` `[peer-reviewed]`:
- U-образная кривая recall: наивысшая точность в начале и конце контекста, провал в середине
- Феномен модельно-независимый — GPT-3.5-Turbo, Claude, MPT, Falcon
- Деградация усиливается с ростом длины контекста

**Anthropic «Prompt Engineering for Long Context» (2023)** `[L2]` `[vendor]`:
- Инструкции в **конце промпта** дают наивысший recall
- Для Claude Instant: монотонная обратная зависимость между расстоянием до релевантного фрагмента и точностью
- Для Claude 2: провал в середине на 95K токенов
- Добавление цитат в scratchpad перед ответом улучшает точность во всех случаях

**Рекомендации по позиционированию:**

1. **Начало промпта** (первые 200 токенов): критичные правила, entry/exit условия, обязательные шаги
2. **Середина**: рабочий контент, алгоритмы, справочные данные
3. **Конец промпта** (последние 200 токенов): критичные напоминания, примеры, формат вывода

## 1.5 Instruction Following Benchmarks

### Ключевые бенчмарки

**FollowBench** (Jiang et al., ACL 2024) `[L1]` `[peer-reviewed]`:
- Multi-level, fine-grained benchmark для оценки следования инструкциям с нарастающей сложностью ограничений
- Тестирование 13 closed-source и open-source LLM на инструкциях с несколькими уровнями вложенности constraints
- Выявляет: модели показывают значительную деградацию при увеличении числа одновременных ограничений — каждый новый constraint снижает compliance по остальным `[Evidence Scope: 13 LLM, дата: 2024, benchmark: multi-level constraint following, source: peer-reviewed]`
- Расширение: **ComplexBench** (NeurIPS 2024) — оценивает сложные инструкции из нескольких constraints `[L1]` `[peer-reviewed]`

**IFEval** (Zhou et al., arXiv:2311.07911, 2023) `[L1]` `[peer-reviewed]`:
- Instruction-Following Evaluation: набор ~541 prompts с 25 типами автоматически верифицируемых инструкций
- Примеры constraints: длина ответа, наличие ключевых слов, формат вывода (JSON, markdown), регистр
- Полностью автоматизированная оценка без участия человека — objective, reproducible
- Широко используется как standard benchmark для instruction compliance

**SIFo** (EMNLP 2024 Findings, arXiv:2406.19999) `[L1]` `[peer-reviewed]`:
- Sequential Instruction Following Benchmark: оценивает способность моделей следовать **цепочке** последовательных инструкций
- 4 типа задач: text modification, question answering, mathematics, security rules
- Ключевое отличие от IFEval: тестирует compliance на **последовательности** инструкций, а не на отдельных
- Билингвальный: English и Chinese

**ManyIFEval** (из Curse of Instructions, ICLR 2025) `[L1]` `[peer-reviewed]`:
- Large-scale benchmark: task prompts с до 10 объективно верифицируемыми наборами инструкций
- Показывает **экспоненциальный спад** success rate при росте числа одновременных инструкций
- Математическая модель деградации: `overall_success_rate ≈ product(individual_constraint_rates)` `[Evidence Scope: frontier-модели, дата: 2025, benchmark: ManyIFEval (up to 10 constraints), source: peer-reviewed]`
- Вывод: нет «безопасного порога» — деградация начинается с первой дополнительной инструкции

### Конфликтующие инструкции

**«The Failure of Instruction Hierarchies in Large Language Models»** (AAAI) `[L1]` `[peer-reviewed]`:
- Даже с целенаправленным обучением модели **не обеспечивают надёжной иерархии** между system/user/developer instructions
- Сильные внутренние смещения (internal biases) подрывают предполагаемую структуру приоритетов
- Практическое следствие: конфликтующие правила в CLAUDE.md и навыке не разрешаются детерминированно

**«How You Prompt Matters!»** (EMNLP 2024 Findings) `[L1]` `[peer-reviewed]`:
- Минимальные вариации формулировок влияют на многоходовые диалоги
- Ограничения для одного измерения часто ухудшают другое
- Вывод: «оптимальный» набор инструкций — это не максимум правил, а баланс

### Практический вывод для dot_ai

1. **IFEval и SIFo подтверждают:** инструкции должны быть атомарными и верифицируемыми `[hard]` `[L1]` `[peer-reviewed]`
2. **FollowBench и ManyIFEval:** больше constraints = экспоненциальный спад compliance — это не линейная, а кумулятивная деградация `[hard]` `[L1]` `[peer-reviewed]`
3. **Конфликтующие инструкции:** нет надёжного механизма приоритизации — устранять противоречия до минимального набора `[hard]` `[L1]` `[peer-reviewed]`
4. **Для правил и навыков:** каждая инструкция должна быть проверяема автоматически (аналог IFEval verification) `[heuristic]` `[L1]` `[peer-reviewed]`

## 1.6 Механизмы rules в разных AI-ассистентах

**Эмпирическое исследование Cursor Rules** (Jiang & Nam, 2025) `[L1]`:
- Качественный анализ 401 open-source репозитория с Cursor Rules
- Таксономия контента: Conventions, Guidelines, Project Information, LLM Directives, Examples
- Варьируется по типу проекта и языку программирования

| Инструмент | Файлы правил | Загрузка | Приоритизация |
|---|---|---|---|
| **Claude Code** | `CLAUDE.md` (иерархия директорий + `@import`), `.claude/rules/` (с `paths:` frontmatter), `settings.json` | Eager (CLAUDE.md), conditional (rules с paths) | Enterprise > CLI args > project > user. Корневой CLAUDE.md переживает compaction `[L2]` |
| **Cursor** | `.cursorrules` (deprecated), `.cursor/rules/*.mdc`, User Rules | Always / Auto (glob) / Agent-Requested / Manual (@ruleName) | Тип правила: Always > Auto > Agent-Requested. Frontmatter: `description`, `globs`, `alwaysApply`. Рекомендация: <500 строк `[L2]` |
| **GitHub Copilot** | `.github/copilot-instructions.md`, `.github/instructions/*.instructions.md` (с `applyTo:`), `AGENTS.md` | Всегда (repo-wide), при совпадении glob (path-specific) | Personal > Repository > Organization. Конфликты разрешаются non-deterministically `[L2]` |
| **Aider** | `CONVENTIONS.md` (через `--read`), `.aider.conf.yml` | При старте сессии (все глобально) | Нет иерархии. Конвенции — read-only файлы в контексте, нет path-gated loading `[L2]` |
| **Windsurf** | `.windsurfrules`, `.windsurf/rules/` (recursive), Memories (auto) | Всегда (workspace rules), auto-generated (Memories) | Workspace > Global. Лимит 6,000 символов/файл. Cascade-интеграция `[L2]` |
| **Cline** | `.clinerules/*.md` (с `paths:` frontmatter), auto-detect `.cursorrules`, `.windsurfrules`, `AGENTS.md` | Всегда или conditional (`paths:`) | Workspace > Global. Каждое правило имеет toggle вкл/выкл. Кросс-инструментальная совместимость `[L2]` |

**Ключевые тренды** `[L2]`:
- **Path-gated rules** — доминирующий подход: Claude Code, Cursor, Copilot, Cline поддерживают условную загрузку по glob-паттернам
- **Кросс-инструментальная совместимость** — Copilot и Cline автоматически обнаруживают файлы правил других инструментов (`AGENTS.md`, `CLAUDE.md`, `.cursorrules`)
- **Нет формальных merge-семантик** — большинство инструментов комбинируют все совпадающие правила без чёткого разрешения конфликтов. GitHub Copilot явно предупреждает о non-deterministic разрешении `[L2]`
- **Контекстный бюджет** — primary constraint для всех инструментов. Больше правил → больше токенов → potential instruction dilution `[L2]` `[L3]`

**Ключевое наблюдение:** Все инструменты загружают rules как часть контекста, но ни один не обеспечивает гарантированный compliance. Разница между инструментами — в механизме загрузки и scope, не в фундаментальной способности модели следовать правилам `[L2]` `[L3]`.

## 1.7 Анти-паттерны

Подтверждённые исследованиями паттерны, которые **ухудшают** instruction compliance:

**1. Длинные списки правил** `[L1]` `[L2]`:
- Curse of Instructions: каждый новое правило снижает compliance по остальным
- Практический предел: ~7 правил для стабильного compliance
- Анти-паттерн: CLAUDE.md с 50+ строками поведенческих инструкций

**2. Противоречивые правила** `[L1]`:
- Instruction Hierarchy: модель не имеет надёжного механизма разрешения конфликтов
- Противоречивые инструкции приводят к непредсказуемому поведению
- Решение: устранять противоречия до минимального набора непротиворечивых правил

**3. Ожидание абсолютного compliance** `[L1]`:
- Instruction Gap: ни одна модель не достигает >95% compliance на строгих бенчмарках
- Критичные ограничения должны enforcement'иться детерминированно (hooks, permissions), не вероятностно (инструкции)
- Правило: если нарушение инструкции недопустимо — используй hook

**4. Monolithic prompts** `[L3]`:
- Гигантский единый промпт — единственная точка отказа
- Отладка ошибок в massive prompt практически невозможна
- Решение: модульная декомпозиция (навыки, rules с glob, lazy loading)

**5. Reasoning-нагрузка поверх правил** `[L1]`:
- Chain-of-thought может ухудшать instruction following
- Анти-паттерн: требование «подумай шаг за шагом» + строгие форматные правила
- Reasoning-модели не следуют reasoning-инструкциям в >75% случаев (ReasonIF benchmark)

**6. Vague instructions** `[L2]`:
- «Будь осторожен с кодом» vs «Не удаляй существующие тесты без явного подтверждения»
- Конкретные, измеримые правила эффективнее абстрактных
- Anthropic: «найти наименьший набор высокосигнальных токенов»

## 1.8 Практические рекомендации

На основе эмпирических данных:

1. **Минимизируй количество правил** — 5–7 ключевых правил на навык/контекст `[hard]` `[L1]` `[L2]`
2. **Структурируй через XML/Markdown** — чёткие границы секций помогают модели парсить `[heuristic]` `[L2]` `[vendor]`
3. **Критичное — первым и последним** — Lost in the Middle U-образная кривая `[hard]` `[L1]` `[peer-reviewed]`
4. **Не рассчитывай на иерархию** — instruction hierarchy ненадёжна, enforcement через hooks `[hard]` `[L1]` `[peer-reviewed]`
5. **Устраняй противоречия** — противоречивые правила дают непредсказуемое поведение `[hard]` `[L1]` `[peer-reviewed]`
6. **Конкретность > абстрактность** — измеримые, специфичные правила `[heuristic]` `[L2]` `[vendor]`
7. **Если нарушение недопустимо — используй hooks** — вероятностные инструкции не заменяют детерминированный enforcement `[hard]` `[L1]` `[L2]`
