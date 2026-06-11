# Skills — эффективность упакованных промптов

> **Дата:** 2026-05-13
> **Версия:** 1.3
> **Источник:** [ai-agent-mechanisms-review.md](ai-agent-mechanisms-review.md)
> **Библиография:** [summary.md](summary.md#54-библиография)

---

Skills (навыки) — второй уровень управления AI-агентами после rules. Если rules определяют постоянные ограничения, то skills — это упакованные процедуры, активируемые по запросу. Паттерн «packaged prompts» (навыки, slash-команды, custom commands, workflow-шаблоны) представляет собой структурированный подход к декомпозиции сложных задач.

## 2.1 Lazy loading vs eager loading

Загрузка контента навыка может происходить двумя способами: **eager** (всегда, при старте сессии) и **lazy** (по запросу, при активации навыка). Выбор стратегии влияет на качество ответов и стоимость контекста.

**Контекст — конечный ресурс** `[L2]`:
- Anthropic «Effective Context Engineering for AI Agents» (2025): контекст имеет убывающую отдачу (diminishing returns). Каждый токен расходует «бюджет внимания»
- Квадратичная сложность self-attention (`O(n²)`) означает: при росте контекста способность модели фиксировать парные отношения растягивается

**Claude Code: двухуровневая загрузка** `[L2]`:
- **Eager**: CLAUDE.md, `.claude/rules/` (с glob), settings.json — загружаются при каждой сессии
- **Lazy**: SKILL.md body — загружается только при активации навыка через trigger или `/skill-name`
- Frontmatter навыка (name, description, when_to_use) доступен модели всегда для автодискавери
- Prompt caching: статический контент (CLAUDE.md, skills frontmatter) попадает в cache, динамический — нет

**Cursor: трёхуровневая модель** `[L2]`:
- **Always**: загружаются при каждом запросе (аналог CLAUDE.md)
- **Auto**: загружаются при совпадении условия (glob-паттерн файла)
- **Agent-Requested**: загружаются, когда агент считает нужным (аналог skill body)
- Agent-Requested правила имеют наименьший приоритет compliance

**Эмпирическое обоснование lazy loading:**
- Lost in the Middle `[L1]`: больше контекста → больше областей с низкой плотностью внимания → деградация recall
- Zones of performance `[L3]` `[community]`: sweet spot 500–2,000 токенов `[Evidence Scope: unspecified model, дата: 2025, benchmark: Q&A юридические документы (Particula Tech), source: community measurement]`, активная деградация >4,000
- Вывод: навык, загружающий 1,500 токенов «про запас», расходует бюджет внимания, даже если не используется

**Практическое правило:** Eager — только для критичных ограничений (5–7 правил) `[hard]` `[Evidence Scope: frontier-модели, дата: 2025, benchmark: Curse of Instructions ICLR 2025, source: peer-reviewed]`. Всё остальное — lazy.

### Интерпретация лимита 500 строк

Официальная рекомендация Claude Code `Keep SKILL.md under 500 lines` — это инженерная эвристика стоимости и управляемости, а не доказанный универсальный порог качества `[L2]`. Причина: после активации тело навыка остаётся в контексте до конца сессии, поэтому каждая лишняя строка становится recurring token cost и увеличивает риск Lost in the Middle.

Исследования long context и instruction following поддерживают **направление риска**, но не фиксируют магическое число строк:
- Lost in the Middle: качество зависит от позиции релевантной информации и длины контекста; важное лучше размещать в начале/конце `[L1]`
- FollowBench / SIFo / Curse of Instructions: качество падает прежде всего от числа одновременно обязательных ограничений и последовательных инструкций, а не от строк как таковых `[L1]`
- Anthropic long-context prompting: длинный релевантный контекст может улучшать результат, если он структурирован, снабжён примерами и модель сначала извлекает опорные цитаты `[L2]`

**Практический вывод:** ограничение по строкам — soft review threshold. Длинный навык допустим, если он проходит eval лучше короткой версии, решает одну измеримую задачу, содержит высокую плотность релевантного контекста, держит критичные правила в начале/конце и выносит справку в supporting files.

## 2.2 Декомпозиция сложных процедур

Когда одношаговый промпт эффективнее многошагового workflow, и наоборот — ключевой вопрос для проектирования навыков.

**«When Does Divide and Conquer Work for Long Context LLMs»** (arXiv:2506.16411, 2025) `[L1]` `[preprint]`:
- Декомпозиция **работает**, когда чанки семантически независимы, а шаг синтеза — низкой сложности
- Декомпозиция **вредит**, когда подзадачи сильно связаны (ошибка в одной каскадно распространяется)
- Оптимальный размер чанка для обработки: 200–500 строк кода или 600–3,000 токенов `[Evidence Scope: long-context LLMs, дата: 2025, benchmark: divide-and-conquer tasks, source: preprint]`

**«Decomposed Prompting»** (Khot et al., 2023) `[L1]` `[peer-reviewed]`:
- Структурированная декомпозиция сложных задач в специализированные подзадачи
- Каждый sub-prompt может использовать разные модели и стратегии
- Ключевой критерий: подзадачи должны быть проще исходной (complexity reduction)
- Error propagation: ошибка на раннем этапе распространяется через pipeline

**«Least-to-Most Prompting»** (Zhou et al., 2022) `[L1]` `[peer-reviewed]`:
- Декомпозиция от простого к сложному: модель сначала решает простейшую подзадачу, затем использует результат
- Эффективно для compositional generalization
- Ограничение: требует, чтобы модель умела декомпозировать корректно (не всегда так)

**Complexity cliff и декомпозиция** `[L1]` `[peer-reviewed]`:
- «Reasoning Models Reason Well, Until They Don't» (IJCNLP 2025) `[peer-reviewed]`: задачи либо работают, либо катастрофически проваливаются
- Декомпозиция переводит задачу из зоны «complexity cliff» в зону «low-to-medium complexity»
- Правило dot_ai «один шаг за сессию» выровнено с этим finding: каждый навык — individually simple задача

**Матрица «один промпт vs workflow»**:

| Характеристика задачи | Один промпт | Многошаговый workflow |
|---|---|---|
| Простая, <5 логических операций | ✅ Оптимально | ❌ Избыточный overhead |
| Составная, >5 операций | ❌ Complexity cliff | ✅ Декомпозиция |
| Семантически независимые подзадачи | ❌ Трата контекста | ✅ Параллельная обработка |
| Сильно связанные подзадачи | ✅ Общий контекст | ⚠️ Риск error propagation |
| Требует разных инструментов/моделей | ❌ Невозможно | ✅ Специализация |

## 2.3 Progressive disclosure

Progressive disclosure (прогрессивное раскрытие) — паттерн размещения критичного контента первым, справочного — по запросу. Применяется на двух уровнях: внутри навыка (структура SKILL.md) и между навыками (frontmatter → body).

**Внутри навыка** `[L2]`:
```
SKILL.md
├── Frontmatter (name, description, when_to_use, allowed-tools)
├── Workflow Contract (entry/exit) — критично, в начале
├── Алгоритм работы — основной контент
├── Правила и ограничения — справочный материал
└── Примеры — в конце (для recall)
```

Обоснование: Lost in the Middle (U-образная кривая) — entry/exit условия и примеры в позициях высокого recall. Алгоритм и правила — в середине, где внимание ниже `[L1]`.

**Между навыками** `[L2]`:
- Frontmatter навыка всегда в контексте модели → определяет, когда активировать навык
- Body загружается при активации → полный алгоритм доступен только при необходимости
- Навыки могут ссылаться друг на друга через `next_skill` → цепочка progressive disclosure

**«Примеры важнее правил»** `[L2]`:
- Anthropic рекомендация: 2–3 канонических примера эффективнее исчерпывающего списка edge cases
- Few-shot examples в конце навыка работают как «якорь» для recall в конце контекста
- Сочетается с Lost in the Middle: примеры в конце = высокая позиция recall

### Supporting files как второй слой контекста

Официальная модель Agent Skills описывает навык как каталог: `SKILL.md` + опциональные `scripts/`, `references/`, `assets/` `[L2]` `[vendor/spec]`. OpenAI Help Center также фиксирует, что skill может включать инструкции, supporting resources, examples и code, а OpenAI skills поддерживаются в Codex и API и следуют Agent Skills open standard `[L2]` `[vendor]`. Anthropic формулирует тот же паттерн как progressive disclosure: метаданные доступны при старте, `SKILL.md` читается после активации, дополнительные файлы читаются или исполняются только при необходимости `[L2]` `[vendor]`.

**Практический вывод:** supporting files — не «приложение к длинному навыку», а отдельный слой контекста. `SKILL.md` должен работать как маршрутизатор: кратко объяснить задачу, дать быстрый алгоритм и явно указать, какой вспомогательный файл читать или какой скрипт запускать в конкретной ситуации.

**Типология supporting files** `[heuristic]` `[L2]`:

| Тип | Назначение | Когда использовать | Контекстный эффект |
|---|---|---|---|
| `references/*.md` | Подробная справка, критерии качества, edge cases, доменные правила | Материал нужен не каждому запуску или зависит от подтипа задачи | Читается по требованию; файл должен быть сфокусированным |
| `scripts/*` | Детерминированные операции, валидаторы, конвертеры, генераторы | Операция хрупкая, повторяемая или требует точности выше prompt-following | Скрипт можно исполнить без загрузки полного кода в контекст; в контекст попадает в основном вывод |
| `assets/*` / `templates/*` | Шаблоны, схемы, примеры артефактов, статические ресурсы | Нужен canonical output или неизменяемый ресурс | Используется как источник истины, не как инструкция |
| `EVALS.md` | Regression cases и критерии успеха | Нужно проверить, улучшает ли изменение навыка качество | Связывает self-improvement с eval gate |
| `LEARNINGS.md` | Сжатые reusable lessons после запусков | Нужна память навыка без прямого раздувания `SKILL.md` | Требует retrieval только релевантных записей |

**Структурные правила** `[heuristic]` `[L2]`:
- Все важные supporting files должны быть напрямую перечислены в `SKILL.md`; избегать цепочек `SKILL.md -> advanced.md -> details.md`, потому что промежуточное чтение повышает риск неполной загрузки.
- Файлы длиннее ~100 строк должны иметь оглавление в начале `[Evidence Scope: Claude Skills docs, дата: 2026, source: vendor recommendation]`.
- Имена файлов должны описывать содержимое (`requirements-quality.md`, `merge-safety.md`), а не порядок (`doc1.md`, `notes.md`).
- Для скриптов нужно явно различать намерение: «запусти скрипт» vs «прочитай скрипт как reference». По умолчанию повторяемые проверки лучше исполнять.
- Dependencies, platform assumptions и required tools должны быть указаны рядом с точкой запуска; нельзя предполагать, что окружение уже содержит нужный пакет.

**Применение к dot_ai:** для основного workflow оптимальная форма — `SKILL.md` как тонкий контракт и `references/` как богатая база релевантного контекста. Например, `plan-release` может ссылаться на файлы с вопросами scope и критериями требований, `implement-spec-stage` — на паттерны трассировки и stage execution, `write-tests` — на test strategy, `integrate-release` — на merge-safety checklist, `deploy-release` — на runbook и rollback. Это прямо поддерживает формулу: маленькая измеримая задача + богатый релевантный контекст.

## 2.4 Frontmatter и метаданные

Frontmatter навыка — точка входа для автодискавери. Качество описания напрямую влияет на то, выберет ли модель правильный навык для задачи.

**Claude Code skill frontmatter** `[L2]`:

| Поле | Назначение | Лимит |
|---|---|---|
| `name` | Уникальный идентификатор | Строка |
| `description` | Когда использовать (определяет автодискавери) | 1,536 символов |
| `when_to_use` | Trigger-фразы пользователя | Строка |
| `allowed-tools` | Пред-одобрённые инструменты | Список |
| `model` | Override модели (sonnet, opus, haiku) | Строка |
| `context` | fork (изоляция) или inherit | Строка |

**Влияние description на автодискавери** `[L2]`:
- Description — основа для решения модели: «какой навык активировать?»
- Расплывчатое описание → неправильная активация → потеря контекста
- Конкретные триггеры («создай ТЗ», «new feature», «implement spec») → точная активация
- Лимит 1,536 символов: не более ~300 токенов — достаточно для concise описания

**Сравнение подходов к метаданным:**

| Инструмент | Механизм метаданных | Автодискавери |
|---|---|---|
| **Claude Code** | SKILL.md frontmatter (YAML) | Да — модель видит description всех навыков |
| **Cursor** | .mdc frontmatter (description, globs, alwaysApply) | Да — Agent-Requested правила выбираются моделью |
| **Aider** | .aider.conf.yml + architect/editor personas | Нет — режимы выбираются пользователем |
| **Copilot** | custom instructions, prompts (preview) | Частично — custom modes в preview |

## 2.5 Сравнение механизмов skills

| Инструмент | Механизм навыков | Загрузка | Специализация |
|---|---|---|---|
| **Claude Code** | SKILL.md, `.claude/commands/`, custom commands | Lazy (по trigger), frontmatter — eager | Модель, инструменты, контекст — через frontmatter |
| **Cursor** | Custom Modes, Agent Rules, .cursor/rules/*.mdc | Always/Auto/Agent-Requested | Режимы (Ask/Agent/Edit) + правила с globs |
| **Aider** | Architect/Editor mode, personas, convention files | При старте режима | Architect (планирование) vs Editor (реализация) |
| **Copilot** | Prompts, custom modes (preview) | При активации режима | Agent mode vs Edit mode, task orchestration |

**Ключевое различие: architect vs editor** `[L2]`:
- Aider первым реализовал разделение: architect (читает, планирует) vs editor (пишет, модифицирует)
- Claude Code использует аналогичный паттерн через типы субагентов: Explore (read-only) vs General-purpose (full tools)
- Cursor разделяет через режимы: Ask (только ответы) vs Agent (действия) vs Edit (правки)
- Общий паттерн: разделение «понимания» и «модификации» снижает риск unintended changes

## 2.6 Самоэволюция навыков

Инструкция в `SKILL.md` сама по себе не создаёт эволюцию. Она может только заставить модель выполнять learning step. Для реального изменения нужен persistent target: `LEARNINGS.md`, `EVALS.md`, `CHANGELOG.md`, supporting file или сам `SKILL.md`, плюс разрешение на запись `[L2]`.

**Базовая архитектура:**

```
skill/
├── SKILL.md        ← стабильный контракт и алгоритм
├── LEARNINGS.md    ← накопленные наблюдения после запусков
├── EVALS.md        ← regression cases и критерии успеха
└── CHANGELOG.md    ← история изменений навыка
```

**Техники инструкций:**

1. **End-of-run reflection block** — в конце каждого запуска классифицировать результат: `no_change`, `memory_update`, `skill_patch_proposal`, `eval_case_needed`.
2. **Skill learning log** — сначала писать наблюдения в `LEARNINGS.md`, а не мутировать `SKILL.md`. Навык на старте читает только релевантные записи.
3. **Eval-first evolution** — новый edge case сначала становится regression case в `EVALS.md`; инструкция меняется только если короткая версия навыка этот case проваливает.
4. **Patch proposal before patch application** — модель готовит diff к `SKILL.md`, но применяет его только при выполнении gate: повторяемая проблема, конкретный пример, снижение неоднозначности, проходящий eval.
5. **Replace, do not append** — каждое добавление должно заменить более слабую инструкцию, удалить устаревший текст или вынести справку в supporting file.
6. **Canonical examples instead of rules** — при ошибке предпочтительно добавить пример `input → expected behavior`, а не новое абстрактное правило.
7. **Start-of-run retrieval** — в начале запуска прочитать `LEARNINGS.md`, но использовать только наблюдения, релевантные текущей задаче.
8. **Autonomous maintenance gate** — без человека автоматически писать только в `LEARNINGS.md`, `EVALS.md`, `CHANGELOG.md`; `SKILL.md` менять только при проходящем eval.

**Шаблон блока для SKILL.md:**

```markdown
## Continuous Improvement

At the end of each run, perform Improvement Triage:

1. If the task succeeded without ambiguity, output `no_change`.
2. If a reusable lesson was discovered, append a concise entry to `LEARNINGS.md`.
3. If the skill instructions caused a failure or ambiguity, create an eval case first.
4. Propose a `SKILL.md` patch only when the same issue is likely to recur.
5. Prefer replacing or deleting stale guidance over appending new rules.
6. Do not update `SKILL.md` unless the relevant eval passes.
```

**Практическое правило:** самоэволюционирующий навык должен учиться через отдельные файлы и eval gate. Прямая автомутация `SKILL.md` без теста быстро приводит к накоплению противоречий и росту контекста.

## 2.7 Skill Evolution / Memory

### Reflexion: вербальное reinforcement learning

**Reflexion** (Shinn et al., NeurIPS 2023) `[L1]` `[peer-reviewed]`:
- Фреймворк для «reinforcement learning» языковых агентов без обновления весов — через **лингвистическую обратную связь**, хранимую как episodic memory
- Агент совершает действие → получает вербальный feedback от evaluator → сохраняет reflexion в memory → использует при следующей попытке
- Превосходит baseline-агенты на задачах decision-making, программирования и reasoning
- Ключевой инсайт: policy агента параметризуется **memory encoding + LLM parameters**, не только весами модели

### Проблема prompt bloat

Рост memory при reflexion-подходе — фундаментальная проблема:

**«What Deserves Memory: Adaptive Memory Distillation for LLM Agents»** (arXiv:2508.03341, 2025) `[L1]` `[preprint]`:
- Адресует вопрос: **какие опыты заслуживают хранения**?
- Предлагает Episodic Memory Integration module — трансформирует сырые взаимодействия в когерентные эпизодические нарративы
- Semantic Memory component для обобщённых знаний
- Показывает: нефильтрованное накопление reflexion-записей деградирует производительность из-за context window overflow `[Evidence Scope: LLM agents, дата: 2025, benchmark: agent tasks with episodic memory, source: preprint]`

**AgentCore Memory (AWS)** `[L2]` `[vendor]`:
- Решает context bloat: хранит каждый turn как raw event через внешний API, а не в prompt window
- Прямое решение проблемы: остановить «раздувание» system prompts edge cases и вместо этого использовать external episodic memory

### Eval-gated self-modification

Паттерн эволюции навыков через eval gate — ключевой подход к безопасной самоэволюции:

**Архитектура из раздела 2.6** `[L2]` `[vendor]`:
- Eval-first evolution: новый edge case → regression case в `EVALS.md` → инструкция меняется только если короткая версия навыка case проваливает
- Patch proposal before patch application: diff к `SKILL.md` применяется только при gate (повторяемая проблема + конкретный пример + снижение неоднозначности)
- Start-of-run retrieval: в начале запуска прочитать `LEARNINGS.md`, но использовать только релевантные наблюдения
- Replace, do not append: каждое добавление должно заменить более слабую инструкцию

**Практические паттерны** `[L2]` `[L3]`:

| Подход | Механизм | Проблема | Решение |
|---|---|---|---|
| Memory distillation | Сжатие сырых эпизодов в нарративы | Prompt bloat от нефильтрованных reflexion | Хранить summaries, не raw logs |
| External memory store | Векторная БД или API за пределами prompt | Context window overflow | Retrieve только релевантное |
| Reflection vs Episodic separation | «Уроки» отдельно от «хронологии» | Смешение абстракций | Episodic → Semantic → Reflection |
| Eval-gated mutation | `SKILL.md` меняется только при проходящем eval | Prompt bloat от бесконтрольных правок | LEARNINGS.md → EVALS.md → SKILL.md gate |

### Практический вывод для dot_ai

1. **Reflexion-подход применим** для навыков: reflexion loop через LEARNINGS.md, не через прямую модификацию SKILL.md `[heuristic]` `[L1]` `[peer-reviewed]`
2. **Prompt bloat — реальный риск** при бесконтрольной самоэволюции: каждый reflexion-запись увеличивает контекст `[hard]` `[L1]` `[preprint]`
3. **Eval-gated self-modification** — единственный безопасный паттерн: SKILL.md обновляется только при проходящем eval `[hard]` `[L2]` `[vendor]`
4. **Memory distillation** — перспективное направление: сжимать LEARNINGS.md периодически, не накапливая бесконечно `[hypothesis]` `[L1]` `[preprint]`

## 2.8 Анти-паттерны

**1. Слишком длинные навыки** `[L2]` `[L3]`:
- SKILL.md > 1,500 токенов: выход за sweet spot → нужен eval или обоснование `[heuristic]` `[Evidence Scope: community measurements + vendor recommendation, модель/дата: 2025, benchmark: unspecified, source: community + vendor]`
- Тело навыка > 500 строк: не автоматический дефект, а сигнал ревизии плотности контекста, структуры и recurring token cost `[heuristic]`
- Решение: вынести справочный контент в отдельные файлы, загружать через Read

**2. Отсутствие чётких триггеров** `[L2]`:
- Description без trigger-фраз → модель не понимает, когда активировать навык
- «Помощь с кодом» vs «реализуй ТЗ, implement spec, продолжи работу» — второе конкретнее
- Решение: явно перечислить trigger-фразы в when_to_use

**3. Дублирование с rules** `[L2]`:
- Правила, уже присутствующие в CLAUDE.md, повторённые в навыке → противоречия, рост контекста
- Навык должен дополнять rules, не дублировать
- Решение: навык ссылается на CLAUDE.md, не копирует его содержимое

**4. Отсутствие entry/exit условий** `[L2]`:
- Без чётких entry/exit модель не знает, когда навык применим, а когда завершён
- Решение: explicit workflow contract в начале навыка

**5. Бесконтрольная самоэволюция** `[L2]`:
- Навык сам дописывает правила в `SKILL.md` после каждого запуска → prompt bloat, противоречия, деградация compliance
- Решение: `LEARNINGS.md` для наблюдений, `EVALS.md` для regression cases, `SKILL.md` обновлять только через gate

## 2.9 Практические рекомендации

1. **Lazy loading по умолчанию** — eager только для критичных ограничений (5–7 правил) `[hard]` `[L2]` `[vendor]`
2. **Декомпозиция при complexity >5 операций** — каждый навык = одна simple задача `[hard]` `[L1]` `[peer-reviewed]`
3. **Progressive disclosure** — frontmatter (автодискавери) → body (алгоритм) → examples (recall) `[heuristic]` `[L2]` `[vendor]`
4. **Конкретные триггеры в description** — модель выбирает навык по описанию, не по содержимому `[hard]` `[L2]` `[vendor]`
5. **Разделение architect/editor** — понимание и модификация должны быть разделены `[heuristic]` `[L2]` `[vendor]`
6. **<1,500 токенов на навык** — default sweet spot; превышение допустимо только при измеримом выигрыше на eval `[heuristic]` `[L2]` `[L3]` `[Evidence Scope: community measurements + vendor recommendation, дата: 2025, source: community + vendor]`
7. **500 строк — soft review threshold** — проверять плотность релевантного контекста, число обязательных правил и структуру, а не резать механически `[heuristic]` `[L2]` `[vendor]`
8. **Примеры важнее правил** — 2-3 canonical examples в конце навыка `[heuristic]` `[L2]` `[vendor]`
9. **Supporting files как второй слой контекста** — `SKILL.md` маршрутизирует к `references/`, `scripts/`, `assets/`, `EVALS.md`, `LEARNINGS.md`; ссылки держать one-level deep, файлы делать сфокусированными `[heuristic]` `[L2]` `[vendor/spec]`
10. **Скрипты для хрупких повторяемых операций** — валидаторы и конвертеры лучше исполнять, чем каждый раз генерировать код заново; инструкции должны задавать input/output и ошибки `[heuristic]` `[L2]` `[vendor]`
11. **Самоэволюция через gate** — learning log и eval cases можно обновлять автоматически; `SKILL.md` менять только при проходящем eval `[heuristic]` `[L2]` `[vendor]`
