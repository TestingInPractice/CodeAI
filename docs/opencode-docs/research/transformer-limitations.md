# Ограничения моделей-трансформеров: значение для проектирования AI-workflow

> **Дата:** 2026-05-09
> **Версия:** 1.1
> **Цель:** Эмпирическая база для принятия решений при проектировании навыков и workflow в dot_ai

---

## 1. Контекстное окно

### Физический предел и механизм внимания

Квадратичная сложность self-attention (`O(n²)`) — фундаментальное ограничение архитектуры Transformer, введённой в работе Vaswani et al. "Attention Is All You Need" (NeurIPS 2017) `[L1]`. Формула `softmax(QK^T / sqrt(d_k)) * V` порождает матрицу внимания размером `n × n`, где n — длина последовательности. Удвоение контекста учетверяет вычислительные затраты и потребление памяти.

На 128K токенов матрица внимания содержит ~16 млрд элементов. Это породило два направления исследований:

**Аппроксимации внимания** `[L1]`:
- **Linformer** (Wang et al., 2020) — проекция K и V в пространство меньшей размерности, `O(n)`
- **Performer** (Choromanski et al., 2021) — ядерные аппроксимации (FAVOR+), линейная сложность
- Обзор: "Efficient Attention Mechanisms for Large Language Models: A Survey" (2025, arXiv:2507.19595) `[L1]`

**Точная оптимизация I/O** `[L1]`:
- **FlashAttention** (Dao et al., NeurIPS 2022) `[L1]` `[peer-reviewed]` — точное внимание с tiling для снижения обращений к HBM. Ускорение 2-4x, экономия памяти 5-20x `[Evidence Scope: A100/H100 GPU, дата: 2022, benchmark: wall-clock + HBM reads, source: peer-reviewed]`. Сложность остаётся `O(n²)`, но wall-clock время существенно снижается
- **FlashAttention-2** (Dao, 2023) и **FlashAttention-3** (Shah et al., NeurIPS 2024) `[L1]` `[peer-reviewed]` — дальнейшая параллелизация

**Вывод для проектирования:** Даже с аппаратными оптимизациями, длинный контекст несёт значительную стоимость. Это создаёт экономический стимул для компактности инструкций даже при больших контекстных окнах.

### Эффективное использование контекста vs заявленное окно

Заявленный размер контекстного окна не равен эффективному. Модели используют контекст неравномерно.

**"Lost in the Middle"** (Liu et al., 2023, arXiv:2307.03172, TACL 2024) `[L1]` `[peer-reviewed]`:
- U-образная кривая: высокая точность в начале и конце контекста, деградация в середине
- Феномен модельно-независимый — наблюдается у GPT-3.5-Turbo, Claude, MPT, Falcon
- Деградация усиливается с ростом длины контекста

**Исследование Anthropic** "Prompt Engineering for Claude's Long Context Window" (2023) `[L2]` `[vendor]`:
- Claude Instant: монотонная обратная зависимость между расстоянием до релевантного фрагмента и точностью
- Claude 2: провал в середине на 95K токенов
- Инструкции в **конце промпта** дают наивысшую точность recall
- Добавление цитат в scratchpad перед ответом улучшает точность во всех случаях

**Anthropic "Effective Context Engineering for AI Agents" (2025) `[L2]` `[vendor]`:**
- Контекст — конечный ресурс с убывающей отдачей. Каждый токен расходует "бюджет внимания"
- `n²` означает: при росте контекста способность модели фиксировать парные отношения растягивается
- Модели имеют меньше обучающих данных с длинными последовательностями → меньше специализированных параметров
- Интерполяция позиционного кодирования (для расширения контекста за пределы обученной длины) деградирует понимание позиций токенов
- Характеристика: "градиент производительности, а не жёсткий обрыв"

**NoLiMa** (2025, arXiv:2502.05167) `[L1]` `[preprint]`: Оценка 12 моделей с заявленной поддержкой 128K+ показала значительные провалы на задачах non-literal matching при длинных контекстах.

### Количество контекста vs точность выполнения задач

Исследования показывают не монотонную зависимость "больше контекста → выше точность", а trade-off между релевантностью, шумом, позицией информации и сложностью операции над контекстом.

**"Context Length Alone Hurts LLM Performance Despite Perfect Retrieval"** (Du et al., EMNLP Findings 2025) `[L1]` `[peer-reviewed]`:
- Даже при идеальном retrieval качество падает при росте длины входа на math, QA и coding tasks
- Заявленная деградация: **13.9-85%** в зависимости от задачи и модели `[Evidence Scope: GPT-4, Claude, Gemini, дата: 2025, benchmark: math/QA/coding tasks с artificial context padding, source: peer-reviewed]`
- Эффект сохраняется, когда нерелевантные токены заменены whitespace, замаскированы, или когда вся релевантная evidence стоит прямо перед вопросом
- Митигация: заставить модель сначала повторить/выделить retrieved evidence, затем решать задачу

**"Large Language Models Can Be Easily Distracted by Irrelevant Context"** (Shi et al., ICML 2023) `[L1]` `[peer-reviewed]`:
- GSM-IC добавляет нерелевантные предложения в арифметические задачи
- Даже сильные prompting-техники резко теряют точность при наличии distractor context
- Self-consistency и явная инструкция игнорировать нерелевантное частично снижают эффект

**RULER** (Hsieh et al., 2024, arXiv:2404.06654) `[L1]` `[peer-reviewed]`:
- Needle-in-a-haystack завышает оценку long-context capabilities: простой retrieval не равен полноценному пониманию
- Бенчмарк измеряет разные типы long-context задач и показывает, что реальный usable context часто меньше заявленного окна

**LongBench** (Bai et al., 2023, arXiv:2308.14508) `[L1]` `[peer-reviewed]`:
- Мультитасковый long-context benchmark: QA, summarization, few-shot, code, synthetic tasks
- Long-context способность сильно зависит от типа задачи: retrieval проще, синтез и reasoning по длинному материалу сложнее

**NoLiMa** (Modarressi et al., 2025, arXiv:2502.05167) `[L1]` `[preprint]`:
- Проверяет retrieval без literal matching: вопрос и evidence не совпадают поверхностно
- Точность падает сильнее по мере роста контекста, если нужна семантическая привязка, а не поиск строки

**"On the Impacts of Contexts on Repository-Level Code Generation"** (Hai et al., 2024/2025) `[L1]` `[preprint]`:
- Для code generation репозиторный контекст полезен только если модель реально использует cross-file dependencies
- Просто дать много файлов недостаточно; нужны релевантные dependency contexts и метрики использования контекста

**Практический вывод для навыков:** оптимизировать не объём, а **плотность полезного контекста**. Рабочая формула: маленькая измеримая задача + богатый релевантный контекст + явное извлечение evidence перед решением. Длинный контекст оправдан, если он повышает eval success rate, а не только "покрывает больше информации".

### Эволюция контекстных окон (2020-2026)

| Год | Модель | Заявленное окно | Примечание |
|------|-------|----------------|-----------|
| 2020 | GPT-3 | 2K | Начало large-scale transformers |
| 2022 | GPT-3.5 | 4K | Запуск ChatGPT |
| 2023 | Claude 2 | 100K | Первый "book-length" контекст |
| 2023 | Claude 3 | 200K | Стандарт Anthropic |
| 2024 | Gemini 1.5 Pro | 1M (до 2M) | Recall >99.7% на needle-in-a-haystack `[L1]` `[Evidence Scope: Gemini 1.5 Pro, дата: 2024, benchmark: needle-in-a-haystack (synthetic retrieval), source: vendor]` |
| 2025 | GPT-5 | 200K | Актуальная модель OpenAI |
| 2025 | Claude 4 (Opus/Sonnet) | 200K | Текущее поколение Anthropic |
| 2025 | Llama 4 Scout | 10M (заявлено) | MoE, 109B параметров; эффективное ~1M `[L2]` `[L3]` `[Evidence Scope: Llama 4 Scout, дата: 2025, benchmark: community testing на реальных задачах, source: community]` |
| 2025-26 | Claude Opus 4.6 | 1M | Расширенный контекст Anthropic |

**Критическое различие:** Maximum Effective Context Window (MECW) значительно меньше заявленного. Gemini 1.5 Pro демонстрирует >99.7% recall на синтетических тестах `[L1]`, но деградирует на реальных задачах. Llama 4 Scout при заявленных 10M показывает эффективные ~1M `[L3]`.

**Лимит выходных токенов:** Отдельное ограничение — выход обычно 4K-16K токенов при входе до 200K+. Модель может прочитать длинный документ, но не может сгенерировать пропорционально длинный ответ `[Evidence Scope: GPT-4/Claude/Gemini, дата: 2025, source: vendor]`.

### Влияние на проектирование навыков и CLAUDE.md

- **Позиционирование критичного контента** — начало и конец промпта (U-образная кривая)
- **Инструкции в конце** — наивысший recall по данным Anthropic `[L2]`
- **Иерархическая загрузка** — лёгкие ссылки (пути файлов) вместо полного содержимого, данные загружаются on-demand через инструменты
- **Compaction** — при длинных сессиях состояние сохраняется внешне (specs, changelog), контекст сжимается
- **Evidence-first паттерн** — перед ответом извлекать опорные факты, цитаты, зависимости или строки кода; это превращает длинноконтекстную задачу в короткоконтекстную reasoning-задачу
- **Eval вместо лимита строк** — сравнивать короткую и длинную версию навыка по task success rate, соблюдению правил, latency/token cost и устойчивости после compaction

---

## 2. Галлюцинации (Hallucinations)

### Механизм возникновения: confabulation в autoregressive моделях

Autoregressive модели генерируют текст через next-token prediction, оптимизируя плавность и контекстуальную правдоподобность продолжения, а не фактическую корректность. Модель не имеет внутреннего механизма fact-checking — не отличает "статистически вероятное продолжение" от "истинного утверждения" `[L1]`.

Термин "confabulation" точнее, чем "hallucination": модель конструирует связные, но вымышленные ответы без намерения обмануть — заполняет пробелы в знаниях правдоподобным содержимым `[L1]` `[L3]`.

**Ключевые работы:**

- **Farquhar, Kossen et al. "Detecting Hallucinations in Large Language Models Using Semantic Entropy"** (Nature, Vol. 630, 2024) `[L1]` `[peer-reviewed]` — semantic entropy: когда генерации расходятся по смыслу (не по формулировке), высокая семантическая энтропия сигнализирует о confabulation
- **Kadavath et al. "Language Models (Mostly) Know What They Know"** (Anthropic, 2022) `[L1]` `[peer-reviewed]` — модели частично способны оценивать собственную корректность, но процесс генерации не надёжно использует эту способность
- **OpenAI "Why Language Models Hallucinate"** (2024) `[L2]` `[vendor]` — модели "догадываются, когда не уверены", генерируя правдоподобные, но неверные ответы

**Корневые причины:**
1. Шум и противоречия в обучающих данных — модель усваивает конфликтующие "факты"
2. Next-token парадигма — нет механизма глобальной проверки согласованности
3. Избыточная уверенность — модели выражают высокую уверенность даже при ошибке
4. Знания как распределённые паттерны — факты не хранятся как дискретные сущности, а как статистические распределения, что делает точный recall ненадёжным

### Типы галлюцинаций

Таксономия из **Huang, Yu et al. "A Survey on Hallucination in Large Language Models"** (arXiv:2311.05232, ACM Transactions, 2023) `[L1]` и **"A Comprehensive Taxonomy of Hallucinations in Large Language Models"** (arXiv:2508.01781, 2025) `[L1]`:

| Тип | Определение | Пример |
|---|---|---|
| **Фактуальная** | Выход противоречит реальным фактам или фабрикует знания | Несуществующая статья, неверные даты, вымышленные сущности |
| **Faithfulness** | Выход отклоняется от предоставленного источника/контекста | Игнорирование инструкций, противоречие исходному документу |
| **Reasoning** | Логические ошибки в цепочке рассуждений: невалидные выводы, пропущенные шаги, sycophantic reasoning | CoT-трассировка, достигающая верного ответа через невалидную логику |

Дополнительные измерения: **intrinsic** (искажение предоставленного контекста) vs **extrinsic** (фабрикация информации вне контекста).

**"Chain-of-Thought Prompting Obscures Hallucination Cues"** (arXiv:2506.17088, 2025) `[L1]` `[preprint]` — CoT может скрывать признаки галлюцинации, оборачивая вымышленные утверждения в логически выглядящие рассуждения.

### Эмпирические данные о частоте галлюцинаций

**Vectara HHEM Leaderboard** `[L2]` `[vendor]` — наиболее цитируемый бенчмарк:

| Модель | Частота галлюцинаций (прибл.) |
|---|---|
| GPT-4 | ~3% |
| Claude Sonnet | ~3-4% |
| Gemini Pro/Ultra | ~4-5% |
| GPT-3.5 Turbo | ~10% |

> **Evidence Scope:** Vectara HHEM Leaderboard, модель/дата: 2024, benchmark: summarization task, source: vendor `[L2]`. Частота зависит от типа задачи и может быть значительно выше на adversarial-вопросах.

**Stanford HAI AI Index (2024/2026)** `[L2]` `[vendor]` — frontier-модели галлюцинируют в **22-94%** случаев при ответах из памяти (AA-Omniscience benchmark, 26 моделей). С RAG частота снижается до **1.8-5.4%** `[Evidence Scope: 26 моделей, дата: 2024-2026, benchmark: AA-Omniscience (memory-based factual QA), source: vendor]`.

**TruthfulQA** (Lin et al., 2022) `[L1]` `[peer-reviewed]`: 58-88% галлюцинаций на adversarial-вопросах у тестированных моделей `[Evidence Scope: GPT-3/4 и другие, дата: 2022, benchmark: TruthfulQA (adversarial factual QA), source: peer-reviewed]`. GPT-4 с RLHF показал ~40% снижение фактических ошибок `[Evidence Scope: GPT-4, дата: 2022-2023, benchmark: TruthfulQA subset, source: peer-reviewed]`.

**Влияние на бизнес** `[L2]` `[vendor]`: Deloitte (2024) — 47% руководителей принимали крупные решения на основе непроверенного AI-контента `[Evidence Scope: Deloitte survey, дата: 2024, sample: enterprise executives, source: vendor]`. Оценочные потери предприятий от галлюцинаций AI — $67.4 млрд в 2024 году `[community measurement, методология оценки неизвестна, источник: industry estimate]`.

### Стратегии митигации

**RAG (Retrieval-Augmented Generation)** `[L1]` `[peer-reviewed]`:
- Lewis et al. "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks" (NeurIPS 2020, arXiv:2005.11401)
- Снижение галлюцинаций с 22-94% (память) до 1.8-5.4% (с retrieval) `[Evidence Scope: 26 моделей, дата: 2024-2026, benchmark: AA-Omniscience, source: vendor report on peer-reviewed + vendor data]`

**Chain-of-Thought + Self-Consistency** `[L1]` `[peer-reviewed]`:
- Wei et al. "Chain-of-Thought Prompting" (NeurIPS 2022, arXiv:2201.11903)
- Wang, Wei et al. "Self-Consistency" (ICLR 2023, arXiv:2203.11171) — сэмплирование нескольких путей рассуждений, выбор ответа большинством

**Chain-of-Verification (CoVe)** `[L1]` `[preprint]`:
- Dhuliawala et al. (Meta FAIR, arXiv:2311.07838, 2023) — четырёхшаговый пайплайн: (1) черновой ответ, (2) планирование проверочных вопросов, (3) независимая верификация, (4) финальный проверенный ответ

**Constrained Generation / Structured Output** `[L2]` `[L1]`:
- OpenAI Structured Outputs (2024) — JSON Schema compliance через constrained decoding
- Устраняет форматные галлюцинации и сужает пространство вывода, но не предотвращает содержательные галлюцинации внутри структурированных полей

**Промпт-инженерия** по Anthropic `[L2]`:
- Разрешить модели говорить "я не знаю"
- Использовать прямые цитаты для привязки к фактам
- Верификация с цитированием — требовать источники для каждого утверждения

### Влияние на проектирование навыков

- **Структурированный вывод** — constrain вывод через шаблоны (markdown-шаблоны spec-ов, commit message форматы)
- **Grounding в исходном материале** — навыки, анализирующие код, должны требовать прямых цитат/ссылок перед генерацией анализа
- **Разрешение на незнание** — системные промпты навыков: "если не можешь верифицировать утверждение из контекста, скажи об этом"
- **Многошаговая верификация** — навыки могут реализовывать лёгкие CoVe-паттерны внутри себя

---

## 3. Потеря информации в середине контекста (Lost in the Middle)

### U-shaped паттерн извлечения информации

**"Lost in the Middle: How Language Models Use Long Contexts"** (Liu et al., Stanford, arXiv:2307.03172, TACL 2024, Vol. 12, pp. 157-173) `[L1]`:

- Модели демонстрируют **U-образную кривую производительности**: высокая точность в начале и конце контекста, значительная деградация в середине
- Феномен модельно-независимый: GPT-3.5-Turbo, Claude, MPT-30B, Falcon
- Тестирование на multi-document QA и key-value retrieval
- Даже модели с 16K+ контекстом демонстрируют деградацию

**"Lost in the Middle: An Emergent Property from Information Retrieval Demands in LLMs"** (OpenReview, 2024/2025) `[L1]` — анализирует феномен как эмерджентное свойство, связанное с информационно-поисковыми требованиями, а не только с позиционным кодированием.

### Подтверждение от Anthropic

Из Anthropic "Effective Context Engineering" (2025) `[L2]`:
- Концепция **"context rot"**: при росте числа токенов способность модели точно вспоминать информацию снижается
- Модели "уделяют больше внимания информации в начале и конце промптов, а средние секции часто недовзвешиваются"

### Практическая количественная оценка

Тестирование Particula Tech (2025) `[L3]` `[community]`: система Q&A для юридических документов на промптах 6,000 токенов — 68% точность. После перестройки с semantic search (3-4 релевантных секции, промпты 1,800 токенов) — 87% точность `[Evidence Scope: unspecified model, дата: 2025, benchmark: Q&A юридические документы, sample: single project, source: community measurement]`.

### Рекомендации по структуре CLAUDE.md и навыков

- **Наиболее критичные инструкции** — в **начале** и **конце** файлов навыков
- **Справочный материал, примеры** — в **середине** (наименее посещаемая зона внимания)
- Для CLAUDE.md: правила workflow (переходы шагов, приоритеты) — наверх, инвентарь навыков и ссылки на документацию — вниз
- Минимизировать "середину": файлы до ~2,000 токенов `[heuristic]`, чтобы U-образная кривая имела минимальное влияние `[Evidence Scope: community measurement, модель не указана, дата: 2025, benchmark: Q&A юридические документы, source: community]`

---

## 4. Instruction Following и переопределение системного промпта

### Границы controllability

**"Curse of Instructions"** (Harada et al., ICLR 2025) `[L1]` `[peer-reviewed]`:
- При увеличении числа инструкций в одном промпте производительность по каждой инструкции прогрессивно деградирует — эффект не линейный, а кумулятивный
- Наблюдается у всех frontier-моделей (GPT-4, Claude и др.) — архитектурное ограничение
- Файл навыка с 20+ поведенческими правилами покажет ухудшение compliance по сравнению с 5-7 приоритизированными `[Evidence Scope: GPT-4, Claude и другие frontier-модели, дата: 2025, benchmark: multi-instruction following (ICLR 2025), source: peer-reviewed]`

**"The Instruction Hierarchy"** (Wallace, Xiao et al., OpenAI, NeurIPS 2024) `[L1]` `[peer-reviewed]`:
- Без специального обучения LLM не естественно соблюдают иерархию приоритетов между system prompt, developer instructions и user messages
- Пользовательские промпты могут переопределять системные инструкции безопасности

**"The Failure of Instruction Hierarchies in Large Language Models"** (AAAI) `[L1]` `[peer-reviewed]`:
- Даже с обучением, разделение system/user prompt **не обеспечивает надёжной иерархии инструкций**
- Модели демонстрируют сильные внутренние смещения, подрывающие предполагаемую структуру приоритетов
- Даже хорошо спроектированные workflow-системы не могут гарантировать соблюдение высокоприоритетных инструкций

### Механизмы priority в инструкциях

**Чувствительность к формулировкам:**
- "Probing LLMs' Limits on Multi-Turn Instruction Following" (2025) `[L1]` — даже GPT-5 чувствителен к минимальным вариациям в системных промптах при многоходовых диалогах
- "How You Prompt Matters!" (EMNLP 2024 Findings) `[L1]` — ограничения, добавленные для улучшения одного измерения, часто ухудшают другое

**Survey:** "Large Language Model Instruction Following: A Survey" (MIT Press / Computational Linguistics, 2024, Vol. 50, No. 3) `[L1]` — полная таксономия режимов отказа при следовании инструкциям.

### Влияние на дизайн навыков и правил

- Содержимое системного промпта — **конечный, истощаемый ресурс** `[L2]`
- Порядок инструкций имеет значение: начало и конец — приоритетные позиции `[L1]`
- Не существует надёжного механизма гарантировать, что системные инструкции переопределяют пользовательские `[hard]` `[L1]` `[peer-reviewed]`
- Каждый навык должен содержать минимально необходимый набор правил (5-7) `[hard]` `[Evidence Scope: frontier-модели, дата: 2025, benchmark: Curse of Instructions ICLR 2025, source: peer-reviewed]`
- Структурирование через XML-теги или Markdown-заголовки помогает модели парсить границы секций `[L2]`

---

## 5. Ограничения reasoning и планирования

### Сложность рассуждений — "complexity cliff"

**"Reasoning Models Reason Well, Until They Don't"** (Rameshkumar et al., IJCNLP 2025) `[L1]` `[peer-reviewed]`:
- Модели поддерживают высокую точность (~85%) на простых задачах, затем **резко коллапсируют** при превышении порога сложности `[Evidence Scope: reasoning models, дата: 2025, benchmark: NLGraph и другие structured reasoning tasks, source: peer-reviewed]`
- Деградация не плавная — катастрофический провал на пороге
- Существующие бенчмарки (NLGraph) имеют ограниченную сложность, маскируя этот отказ
- Большинство реальных примеров в зоне успеха, но "хвосты" обнаруживают существенный потенциал отказа

**"The Illusion of Thinking"** (Shojaee et al., Apple ML Research, июнь 2025) `[L1]` `[preprint]`:
- Frontier reasoning-модели демонстрируют **полный коллапс точности** за определённой сложностью
- Контринтуитивный лимит масштабирования: reasoning effort растёт с сложностью до точки, затем **снижается** несмотря на достаточный токенный бюджет
- Три режима производительности:
  1. **Низкая сложность:** стандартные LLM удивительно превосходят reasoning-модели
  2. **Средняя сложность:** reasoning-модели показывают преимущество
  3. **Высокая сложность:** оба типа — полный коллапс

**"An Information-Theoretic Bound on Closed-System Multi-Step LLM Reasoning"** (2025) `[L1]` `[preprint]` — формальный теоретический предел на многошаговые рассуждения в замкнутой системе.

### Reasoning ≠ Planning

**"Why Reasoning Fails to Plan"** `[L1]` `[preprint]`: сильная пошаговая reasoning-способность не транслируется в когерентное долгосрочное планирование. Модели решают отдельные шаги, но не могут поддерживать связные многошаговые планы.

### Компонентность задач и chunking стратегии

**"When Does Divide and Conquer Work for Long Context LLMs"** (2025) `[L1]` `[preprint]` — декомпозиция работает, когда чанки **семантически независимы**, а шаг синтеза — низкой сложности.

**Практические стратегии chunking** `[L2]` `[L3]`:
- Recursive chunking: 512-1024 токенов с 10-20% перекрытием `[L3]` `[heuristic]`
- Многостадийная обработка: извлечение (~800 токенов) → анализ (~1,200) → генерация (~1,000) превосходит один промпт на 3,000 токенов `[L3]` `[heuristic]` `[Evidence Scope: community observations, модель/дата не указаны, benchmark: unspecified, source: community]`

**Субагентная архитектура** (Anthropic, 2025) `[L2]` `[vendor]`: специализированные субагенты обрабатывают сфокусированные задачи с чистым контекстом, возвращая сжатую сводку (~1,000-2,000 токенов) `[heuristic]` `[Evidence Scope: Claude Code, дата: 2025, source: vendor recommendation]`.

### Рекомендации по декомпозиции этапов в workflow

- Каждый шаг workflow должен быть **индивидуально простым** (low-complexity regime)
- Не полагаться на модель для выполнения многошаговой reasoning-цепочки как единого шага
- Каждый навык (spec-creation, spec-implementer, merge-helper) должен соответствовать задаче low-to-medium сложности
- Избегать шагов, требующих от модели поддержания состояния более чем через ~5-7 логических операций `[heuristic]` `[Evidence Scope: reasoning models, дата: 2025, benchmark: complexity cliff observations, source: peer-reviewed]`
- "Complexity cliff" означает: задачи либо работают, либо катастрофически проваливаются — безопасной плавной деградации нет
- Правило "один шаг за сессию" в dot_ai workflow выровнено с findings о complexity cliff

---

## 6. Оптимальный размер файлов кода для AI-агентов

### Деградация понимания кода с ростом контекста

Lost in the Middle (Liu et al., 2024) `[L1]` применима и к коду: при длинных файлах релевантный код в середине теряется. Модели демонстрируют U-образную кривую recall — лучшее понимание в начале и конце, провал в середине. Феномен наблюдается у всех протестированных моделей (GPT-3.5-Turbo, Claude, MPT-30B, Falcon).

"Intelligence Degradation in Long-Context LLMs" (arXiv:2601.15300, 2025) `[L1]` показывает, что качество reasoning деградирует с длиной контекста даже при идеальном retrieval. Проблема не только в нахождении информации, но и в reasoning над ней.

"Context Length Alone Hurts LLM Performance Despite Perfect Retrieval" (Amazon Science, 2025) `[L1]`: даже когда retrieval идеален, более длинный контекст сам по себе снижает производительность LLM.

"On the Impacts of Contexts on Repository-Level Code Generation" (arXiv, 2024) `[L1]` напрямую исследует влияние длины контекста на генерацию кода на уровне репозитория. Подтверждает Lost in the Middle как ключевую проблему при предоставлении LLM больших фрагментов кодовой базы.

### Зоны AI-понимания кода

На основе исследований context degradation и community-бенчмарков `[L3]` `[community]`. **Примечание:** границы зон — эвристики, основанные на community measurements и согласованных vendor-рекомендациях, а не универсальные пороги. Конкретный порог зависит от модели, типа задачи и плотности релевантного контекста `[heuristic]`:

| Зона | Строки | Токены (~1 строка ≈ 6 токенов) | Поведение |
|---|---|---|---|
| Sweet spot | 100-300 | 600-1,800 | Оптимальное понимание, быстрый ответ |
| Допустимо | 300-500 | 1,800-3,000 | Хорошее понимание, начало деградации |
| Убывающая отдача | 500-800 | 3,000-5,000 | Пропуски деталей в середине файла |
| Активная деградация | >800 | >5,000 | Lost in the Middle, значительные пропуски |

### Стратегия AI-агента при работе с длинными файлами

- Claude Code Read по умолчанию загружает до 2,000 строк — но для файлов >500 строк эффективнее точечный поиск через Grep + Read с offset `[L2]`
- RAG chunking: 200-500 строк с 10-20% перекрытием между чанками `[L3]`
- Для repo-level генерации: обеспечить контекст в пределах sweet spot, остальное подгружать on-demand `[L1]`
- Anthropic рекомендует "найти наименьший набор высокосигнальных токенов, максимизирующих вероятность желаемого результата" `[L2]`

---

## 7. Context Engineering: RAG vs Long Context

### RAG vs длинное контекстное окно

Два подхода к предоставлению информации модели: **RAG** (retrieval-augmented generation — выборка релевантных фрагментов) и **long context** (загрузка полного документа в контекст). Сравнение показывает trade-off между стоимостью, качеством и типом задачи.

**«Retrieval Augmented Generation or Long-Context LLMs?»** (Li et al., EMNLP 2024) `[L1]` `[peer-reviewed]`:
- Комплексное сравнение RAG и long-context LLM на QA-задачах
- Long-context модели **последовательно превосходят RAG** при достаточных ресурсах `[Evidence Scope: GPT-4, Claude, дата: 2024, benchmark: QA tasks (Wikipedia-based), source: peer-reviewed]`
- Гибридный подход (RAG + long context) показывает лучшие результаты на задачах с большим объёмом документов
- RAG остаётся предпочтительным для: внешних данных в реальном времени, снижения inference-cost, случаев когда корпус не помещается в контекстное окно

**«Long Context vs. RAG for LLMs: An Evaluation and Revisits»** (arXiv:2501.01880, 2025) `[L1]` `[preprint]`:
- Long context превосходит RAG на Wikipedia-based QA, особенно при доступности всего релевантного контекста `[Evidence Scope: frontier-модели, дата: 2025, benchmark: QA (Wikipedia), source: preprint]`
- RAG сохраняет преимущество на задачах с динамически обновляемыми данными

**Уже цитированные данные о RAG и галлюцинациях** (Stanford HAI AI Index 2024/2026) `[L2]` `[vendor]`:
- RAG снижает частоту галлюцинаций с 22–94% (ответы из памяти) до 1.8–5.4% (с retrieval) `[Evidence Scope: 26 моделей, дата: 2024–2026, benchmark: AA-Omniscience, source: vendor]`

### Evidence-first и quote-before-answer паттерны

Практические паттерны повышения точности при работе с контекстом, подтверждённые исследованиями:

**Evidence-first** `[L2]` `[vendor]`:
- Anthropic рекомендует: перед генерацией ответа заставить модель извлечь и воспроизвести опорные факты из контекста
- Превращает длинноконтекстную задачу в короткоконтекстную reasoning-задачу: модель сначала выделяет релевантные цитаты, затем рассуждает над ними
- Подтверждено данными о деградации: «Context Length Alone Hurts LLM Performance Despite Perfect Retrieval» `[L1]` `[peer-reviewed]` — митигация через повторение evidence перед ответом снижает эффект деградации

**Quote-before-answer** `[L1]` `[L2]`:
- Требование прямых цитат из исходного материала перед каждым утверждением — снижает галлюцинации (Anthropic «Reduce Hallucinations») `[L2]` `[vendor]`
- Верификация с цитированием: каждый нетривиальный ответ должен сопровождаться ссылкой на фрагмент исходного текста `[L2]` `[vendor]`
- CoVe (Chain-of-Verification): четырёхшаговый пайплайн с независимой верификацией `[L1]` `[preprint]`

**Для навыков и правил dot_ai** `[L2]` `[vendor]`:
- Навыки, анализирующие код, должны требовать прямых цитат/ссылок перед генерацией анализа
- Evidence-first паттерн: в длинных навыках сначала извлечь релевантные факты/цитаты/dependencies, затем выполнять вывод `[hard]` `[L1]` `[L2]`

### Практический вывод для dot_ai

1. **Для задач анализа кода** — использовать RAG-like подход: точечный Grep + Read с offset вместо загрузки целых файлов `[heuristic]` `[L2]` `[vendor]`
2. **Evidence-first перед reasoning** — в навыках сначала извлечь evidence, затем рассуждать `[hard]` `[L1]` `[peer-reviewed]`
3. **Long context допустим** для задач, где весь документ релевантен (например, спецификации), но с eval-проверкой `[heuristic]`
4. **RAG не заменяет long context для reasoning** — retrieval помогает найти информацию, но reasoning над ней требует полного контекста `[L1]` `[peer-reviewed]`

---

## 8. Agentic Coding: бенчмарки и ограничения

### SWE-bench и его эволюция

**SWE-bench** (Jimenez et al., ICLR 2024) `[L1]` `[peer-reviewed]`:
- Бенчмарк для оценки способности AI-агентов решать реальные задачи из GitHub issues
- Модель должна: понять issue → навигировать по кодовой базе → создать корректный патч
- Оригинальный набор: 2,294 задачи из 12 Python-репозиториев

**SWE-bench Verified** `[L2]` `[vendor]`:
- Human-filtered поднабор из **500 задач**, валидированных реальными разработчиками (совместно с OpenAI Preparedness, 2024)
- Устраняет неоднозначные и нерешаемые instances оригинального SWE-bench
- Текущие frontier-модели достигают ~72–79% resolved rate `[Evidence Scope: Claude 4.5 Opus, дата: 2025, benchmark: SWE-bench Verified, source: vendor + community]`
- Критики отмечают: те же модели показывают лишь ~23% на более сложных вариантах бенчмарка, указывая на разрыв между benchmark scores и реальной продуктивностью

### RepoBench и RepoExec

**RepoBench** (Luo et al., ICLR 2024) `[L1]` `[peer-reviewed]`:
- Бенчмарк для оценки repository-level code auto-completion
- Измеряет способность модели дополнять код с учётом cross-file dependencies
- Python и Java: модель должна понимать и использовать межфайловые зависимости
- Заполняет пробел между file-level и repository-level оценкой

**RepoExec / ExecRepoBench** `[L1]` `[preprint]`:
- Execution-based оценка repository-level code completion
- Выходит за рамки статического matching: сгенерированный код **выполняется** для проверки корректности
- Подтверждает: статические метрики (BLEU, CodeBLEU) плохо коррелируют с runtime-корректностью

### Dependency utilization и контекст кода

**«On the Impacts of Contexts on Repository-Level Code Generation»** (Hai et al., 2024/2025) `[L1]` `[preprint]`:
- Репозиторный контекст полезен **только если модель реально использует cross-file dependencies**
- Простое предоставление большого количества файлов недостаточно
- Необходимы: релевантные dependency contexts + метрики использования контекста

**Практический вывод для dot_ai** `[L1]` `[L2]`:
- Навыки, генерирующие код, должны обеспечивать контекст в пределах sweet spot, остальное — on-demand через инструменты
- Spec-implementer использует субагентов-трассировщиков для выявления dependencies перед реализацией — этот паттерн выровнен с выводами RepoBench `[heuristic]`
- Высокие scores на SWE-bench ≠ гарантия продуктивности в реальном проекте — eval должен быть локальным, а не только benchmark-driven `[heuristic]` `[L1]` `[L3]`

---

## 9. Практические рекомендации для dot_ai

### Рекомендуемые размеры файлов

| Артефакт | Рекомендуемый размер | Обоснование |
|----------|---------------------|-------------|
| CLAUDE.md (основные правила) | 1,000-2,000 токенов (~200 строк) `[heuristic]` | Официальное руководство Anthropic `[L2]`, оптимальная зона внимания `[Evidence Scope: Claude, дата: 2025, source: vendor]` |
| Оптимальный файл правил | ~600 токенов (~60 строк) `[heuristic]` | Community benchmark, "sweet spot" `[L3]` `[Evidence Scope: модель не указана, дата: 2025, benchmark: community observations, source: community]` |
| SKILL.md (навык) | 500-1,500 токенов `[heuristic]` | В зоне высокого recall, без потерь от Lost in the Middle `[Evidence Scope: community measurements + vendor recommendation, дата: 2025, source: community]` |
| Spec-файл (.ai/specs/) | 1,000-3,000 токенов `[heuristic]` | Сложный, но целенаправленный; допустима зона убывающей отдачи |
| Документ архитектуры | 500-1,500 токенов `[heuristic]` | Справочный материал, загружается по требованию |
| Файл кода (для AI-понимания) | ≤ 300 строк (~1,800 токенов) `[heuristic]` | Sweet spot AI-понимания, до onset деградации `[L1]` `[L3]` `[Evidence Scope: GPT-3.5/Claude, дата: 2024, benchmark: Lost in the Middle + community code understanding tests, source: peer-reviewed + community]` |

**Зоны производительности** по Particula Tech (2025) `[L3]` `[community]`. **Примечание:** численные границы — community measurement на одном проекте (Q&A юридические документы), не универсальный порог `[heuristic]`:

| Зона | Диапазон токенов | Поведение |
|------|-----------------|-----------|
| Sweet spot | 500-2,000 | Оптимальная производительность, быстрый отклик, наивысшая точность |
| Убывающая отдача | 2,000-4,000 | На 40-80% медленнее `[Evidence Scope: unspecified model, дата: 2025, benchmark: single project Q&A, source: community measurement]`, 2-3% прирост точности при удвоении |
| Активная деградация | 4,000+ | Измеримое снижение качества, пропущенные детали, галлюцинации |

### Максимальная вложенность инструкций

- **Глубина workflow:** Максимум 3-4 уровня условной вложенности до деградации compliance `[heuristic]` `[L1]`
- **Уровни приоритета:** Максимум 3 (system > developer > user) — даже 2 уровня ненадёжны `[hard]` `[L1]` `[peer-reviewed]`
- **Цепочка шагов:** 3-шаговый workflow (spec-creation → spec-implementer → merge-helper) — в безопасной зоне до complexity cliff

### Стратегия приоритизации контента в навыках

1. **Критичный контент — первым и последним** (Lost in the Middle) `[hard]` `[L1]` `[peer-reviewed]`
2. **Минимум одновременных инструкций** — 5-7 ключевых правил на навык (Curse of Instructions) `[hard]` `[L1]` `[peer-reviewed]` `[Evidence Scope: frontier-модели, дата: 2025, benchmark: multi-instruction following, source: peer-reviewed]`
3. **Структурированные секции** — XML-теги или Markdown-заголовки для парсинга границ `[heuristic]` `[L2]` `[vendor]`
4. **Динамическая загрузка контекста** — just-in-time retrieval вместо статического stuffing `[heuristic]` `[L2]` `[vendor]`
5. **Compaction для многоходовых сессий** — сжатие вместо роста контекста `[heuristic]` `[L2]` `[vendor]`
6. **Примеры важнее правил** — 2-3 канонических примера эффективнее длинных списков правил `[heuristic]` `[L2]` `[vendor]`
7. **Статический контент — в начале** — для эффективности prompt caching `[heuristic]` `[L2]` `[vendor]`
8. **Evidence-first перед reasoning** — в длинных навыках сначала извлечь релевантные факты/цитаты/dependencies, затем выполнять вывод `[hard]` `[L1]` `[L2]`
9. **Контекст по eval, не по объёму** — длинный навык допустим, если он измеримо лучше короткого на regression cases `[hard]` `[L1]`

### Чеклист для валидации нового навыка

1. Навык занимает менее 1,500 токенов?
2. Наиболее критичные инструкции — в первых и последних 200 токенах?
3. Содержит 5-7 или менее поведенческих правил?
4. Есть 2-3 канонических примера вместо исчерпывающего списка edge cases?
5. Сложность задачи достаточно низка, чтобы избежать "complexity cliff"?
6. Навык декомпозирован в одну сфокусированную операцию?
7. Дополнительный контент загружается динамически, а не встроен статически?
8. Шаблон вывода структурирован (markdown/XML), чтобы снизить форматные галлюцинации?
9. Есть шаг извлечения evidence перед генерацией решения?
10. Сравнивалась ли короткая и длинная версия навыка на eval cases?

---

## Библиография

### L1 — Рецензируемые статьи и preprints

1. Vaswani, A., Shazeer, N., et al. "Attention Is All You Need." NeurIPS 2017. arXiv:1706.03762 `[peer-reviewed]`
2. Dao, T., Fu, D., Ermon, S., et al. "FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness." NeurIPS 2022. arXiv:2205.14135 `[peer-reviewed]`
3. Liu, N.F., Lin, K., Hewitt, J., et al. "Lost in the Middle: How Language Models Use Long Contexts." TACL 2024, Vol. 12, pp. 157-173. arXiv:2307.03172 `[peer-reviewed]`
4. Harada, K., Yamazaki, Y., et al. "Curse of Instructions: Large Language Models Cannot Follow Multiple Instructions at Once." ICLR 2025. openreview.net/forum?id=R6q67CDBCH `[peer-reviewed]`
5. Wallace, E., Xiao, K., et al. "The Instruction Hierarchy: Training LLMs to Prioritize Privileged Instructions." NeurIPS 2024. arXiv:2404.13208 `[peer-reviewed]`
6. "The Failure of Instruction Hierarchies in Large Language Models." AAAI. ojs.aaai.org/index.php/AAAI/article/view/40339 `[peer-reviewed]`
7. Rameshkumar, R., Huang, J., et al. "Reasoning Models Reason Well, Until They Don't." IJCNLP 2025. arXiv:2510.22371 `[peer-reviewed]`
8. Shojaee, P., Mirzadeh, I., et al. "The Illusion of Thinking." Apple ML Research, 2025. machinelearning.apple.com/research/illusion-of-thinking `[preprint]`
9. "An Information-Theoretic Bound on Closed-System Multi-Step LLM Reasoning." arXiv:2605.01704 `[preprint]`
10. "When Does Divide and Conquer Work for Long Context LLMs." arXiv:2506.16411 `[preprint]`
11. Farquhar, J., Kossen, H., et al. "Detecting Hallucinations in Large Language Models Using Semantic Entropy." Nature 630, 2024 `[peer-reviewed]`
12. Kadavath, S., et al. "Language Models (Mostly) Know What They Know." Anthropic, 2022 `[peer-reviewed]`
13. Huang, L., Yu, W., et al. "A Survey on Hallucination in Large Language Models." arXiv:2311.05232, ACM Transactions, 2023 `[peer-reviewed]`
14. Lewis, P., et al. "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks." NeurIPS 2020. arXiv:2005.11401 `[peer-reviewed]`
15. Wang, X., Wei, J., et al. "Self-Consistency Improves Chain of Thought Reasoning." ICLR 2023. arXiv:2203.11171 `[peer-reviewed]`
16. Dhuliawala, S., et al. "Chain-of-Verification Reduces Hallucination." arXiv:2311.07838, 2023 `[preprint]`
17. "NoLiMa: Long-Context Evaluation Beyond Literal Matching." arXiv:2502.05167, 2025 `[preprint]`
18. Agarwal, R., Singh, A., et al. "Many-Shot In-Context Learning." ICML 2024. arXiv:2404.11018 `[peer-reviewed]`
19. "How You Prompt Matters! Task-Oriented Constraints in System Prompts." EMNLP 2024 Findings `[peer-reviewed]`
20. "Large Language Model Instruction Following: A Survey." Computational Linguistics, MIT Press, 2024, Vol. 50, No. 3 `[peer-reviewed]`
21. "Intelligence Degradation in Long-Context LLMs." arXiv:2601.15300, 2025 `[preprint]`
22. Du, Y., Tian, M., Ronanki, S., et al. "Context Length Alone Hurts LLM Performance Despite Perfect Retrieval." EMNLP Findings 2025. arXiv:2510.05381 `[peer-reviewed]`
23. Shi, F., Chen, X., Misra, K., et al. "Large Language Models Can Be Easily Distracted by Irrelevant Context." ICML 2023. arXiv:2302.00093 `[peer-reviewed]`
24. Hsieh, C.-P., Sun, S., Kriman, S., et al. "RULER: What's the Real Context Size of Your Long-Context Language Models?" arXiv:2404.06654, 2024 `[peer-reviewed]`
25. Bai, Y., Lv, X., Zhang, J., et al. "LongBench: A Bilingual, Multitask Benchmark for Long Context Understanding." arXiv:2308.14508, 2023 `[peer-reviewed]`
26. Hai, N.L., Nguyen, D.M., Bui, N.D.Q. "On the Impacts of Contexts on Repository-Level Code Generation." arXiv:2406.11927, 2024/2025 `[preprint]`
27. Li, Z., et al. "Retrieval Augmented Generation or Long-Context LLMs? A Comprehensive Study and Hybrid Approach." EMNLP 2024 Industry Track. arXiv:2407.16833 `[peer-reviewed]`
28. "Long Context vs. RAG for LLMs: An Evaluation and Revisits." arXiv:2501.01880, 2025 `[preprint]`
29. Jimenez, C.E., et al. "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?" ICLR 2024. arXiv:2310.06770 `[peer-reviewed]`
30. Luo, T., et al. "RepoBench: Benchmarking Repository-Level Code Auto-Completion Systems." ICLR 2024. arXiv:2306.03091 `[peer-reviewed]`

### L2 — Официальная документация и блоги исследовательских групп `[vendor]`

1. Anthropic. "Effective Context Engineering for AI Agents." 2025. anthropic.com/engineering/effective-context-engineering-for-ai-agents `[vendor]`
2. Anthropic. "Prompt Engineering for Claude's Long Context Window." 2023. anthropic.com/news/prompting-long-context `[vendor]`
3. Anthropic. "Reduce Hallucinations." Claude API Docs. platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations `[vendor]`
4. OpenAI. "Why Language Models Hallucinate." 2024. cdn.openai.com/pdf/.../why-language-models-hallucinate.pdf `[vendor]`
5. Google. "Gemini 1.5 Technical Report." 2024. arXiv:2403.05530 `[vendor]`
6. Google. "Needle in a Haystack with Gemini." cloud.google.com/blog/.../the-needle-in-a-haystack-test `[vendor]`
7. Meta. "Llama 4 Herd Announcement." ai.meta.com/blog/llama-4-multimodal-intelligence/ `[vendor]`
8. Pinecone. "Chunking Strategies for LLM Applications." pinecone.io/learn/chunking-strategies/ `[vendor]`
9. Stanford HAI. "AI Index Report 2024/2026." hai.stanford.edu/ai-index-report `[vendor]`
10. Vectara. "Hallucination Leaderboard." github.com/vectara/hallucination-leaderboard `[vendor]`
11. Deloitte. "State of Generative AI in the Enterprise." Q1 2024 `[vendor]`
12. OpenAI. "SWE-bench Verified." swebench.com/verified.html, 2024 `[vendor]`

### L3 — Блоги, статьи, сообщество `[community]`

1. Particula Tech. "Optimal Prompt Length Before AI Performance Degrades." 2025. particula.tech/blog/optimal-prompt-length-ai-performance `[community]`
2. HumanLayer. "Writing a Good CLAUDE.md." humanlayer.dev/blog/writing-a-good-claude-md `[community]`
3. GitConnected. "Claude Code Best Practices: 12 Patterns Agentic Engineers Use." levelup.gitconnected.com/claude-code-best-practices `[community]`
4. Packmind. "Context Engineering Best Practices." 2026. packmind.com/context-engineering-ai-coding `[community]`
5. Rewire.it. "The Complexity Cliff: Why Reasoning Models Work Until They Don't." rewire.it/blog/the-complexity-cliff `[community]`
