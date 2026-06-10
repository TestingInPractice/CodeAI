# Сводка и рекомендации

> **Дата:** 2026-05-13
> **Версия:** 1.2
> **Источник:** [ai-agent-mechanisms-review.md](ai-agent-mechanisms-review.md)
> **Методология:** [literature-review-methodology.md](../researches/literature-review-methodology.md)

---

## Обозначения типов рекомендаций

Рекомендации в этом документе классифицированы по силе доказательства (см. [методологию](../researches/literature-review-methodology.md)):

| Тип | Маркер | Значение |
|-----|--------|----------|
| Hard recommendation | `[hard]` | Основано на peer-reviewed или local eval. Применимо как общее правило |
| Heuristic | `[heuristic]` | Подтверждено vendor-данными или согласованными community-наблюдениями. Отправная точка, требует проверки |
| Hypothesis | `[hypothesis]` | Предположение, требующее local eval для подтверждения |

---

## 5.1 Сводная таблица механизмов

| Механизм | Когда использовать | Overhead | Надёжность | Ограничение |
|---|---|---|---|---|
| **Rules** | Постоянные инструкции, стандарты кода, ограничения проекта | Низкий (токены в контексте) | Вероятностная (<95%) `[L1]` `[peer-reviewed]` `[Evidence Scope: 13 frontier-моделей, дата: 2025, benchmark: instruction compliance benchmarks, source: peer-reviewed]` | Curse of Instructions при >7 правил `[L1]` `[peer-reviewed]` `[Evidence Scope: frontier-модели, дата: 2025, benchmark: ICLR 2025, source: peer-reviewed]` |
| **Skills** | Многошаговые процедуры, workflow с этапами | Средний (lazy loading) | Вероятностная (зависит от prompt) | Sweet spot <1,500 токенов `[heuristic]` `[L2]` `[L3]` `[Evidence Scope: community measurements + vendor recommendation, модель/дата: 2025, source: community + vendor]` |
| **Sub-agents** | Исследование, сложные задачи, параллелизация | Высокий (~12K токенов/вызов) `[vendor]` `[Evidence Scope: Claude Code, 2025]` | Высокая (чистый контекст) | 1 уровень вложенности, потеря родительского контекста `[L1]` `[L2]` |
| **Hooks** | Enforcement ограничений, линтинг, валидация | Минимальный (shell-команда) | Детерминированная (100%) `[L2]` `[vendor]` | Не понимает контекст (command-тип) `[L2]` `[vendor]` |

## 5.2 Матрица принятия решений

```
Задача: управление AI-агентом
│
├─ Нарушение недопустимо? (security, compliance)
│  └─ ДА → HOOKS (детерминированный enforcement)
│
├─ Требует многошаговой процедуры?
│  ├─ ДА, <5 операций → SKILL (один навык)
│  ├─ ДА, >5 операций → SKILL + WORKFLOW (цепочка навыков)
│  └─ ДА, нужна изоляция → SUB-AGENT
│
├─ Требует исследования/анализа?
│  ├─ Read-only, много файлов → SUB-AGENT (Explore, Haiku)
│  ├─ Параллельные аспекты → N SUB-AGENTS (parallel)
│  └─ Зависит от контекста беседы → ОСТАВИТЬ В ОСНОВНОМ КОНТЕКСТЕ
│
└─ Постоянная инструкция?
   ├─ Критичная → CLAUDE.md (eager loading)
   ├─ По типу файлов → RULES с paths (conditional loading)
   └─ По запросу → SKILL (lazy loading)
```

## 5.3 Рекомендации для dot_ai

На основе эмпирических данных из всех четырёх секций:

**Архитектура правил (CLAUDE.md):**
- Корневой CLAUDE.md: ≤200 строк, 5–7 ключевых правил, критичное в первых и последних строках `[hard]` — обосновано Curse of Instructions `[L1]` `[peer-reviewed]` и Lost in the Middle `[L1]` `[peer-reviewed]`
- `.claude/rules/` с `paths:` frontmatter для условных инструкций `[hard]` — архитектура Claude Code `[L2]` `[vendor]`
- Не дублировать правила между CLAUDE.md и skills `[heuristic]` — следует из конечности бюджета внимания `[L2]` `[vendor]`

**Архитектура навыков (SKILL.md):**
- Тело навыка: 500–1,500 токенов, sweet spot compliance `[heuristic]` — community measurements `[L3]` `[community]`, vendor engineering blog `[L2]` `[vendor]` `[Evidence Scope: unspecified model, дата: 2025, benchmark: Q&A tasks (Particula Tech), source: community + vendor]`
- Frontmatter: конкретные триггеры в description и when_to_use `[hard]` — архитектура Claude Code `[L2]` `[vendor]`
- Структура: Workflow Contract (начало) → Алгоритм → Правила → Примеры (конец) `[hard]` — обосновано Lost in the Middle `[L1]` `[peer-reviewed]`
- Каждый навык = одна simple задача (до complexity cliff) `[hard]` — обосновано complexity cliff `[L1]` `[peer-reviewed]`
- Supporting files: `SKILL.md` как маршрутизатор, `references/`, `scripts/`, `assets/`, `EVALS.md`, `LEARNINGS.md` как второй слой контекста `[heuristic]` — Agent Skills spec и Anthropic/OpenAI docs `[L2]` `[vendor/spec]`

**Архитектура субагентов:**
- Explore (Haiku) для параллельного исследования (≤5 агентов) `[heuristic]` — vendor рекомендация `[L2]` `[vendor]`, применимость к конкретному проекту зависит от задач
- General-purpose для сложных задач с чистым контекстом `[hard]` — обосновано разделением контекста `[L2]` `[vendor]`
- Не делегировать тривиальные задачи (overhead ~12K токенов) `[hard]` — overhead измерен vendor `[L2]` `[vendor]` `[Evidence Scope: Claude Code, 2025]`
- Субагент возвращает сводку 1,000–2,000 токенов `[heuristic]` — vendor рекомендация `[L2]` `[vendor]` `[Evidence Scope: Claude Code, дата: 2025, source: vendor recommendation]`

**Архитектура хуков:**
- PreToolUse: блокировка опасных Bash-команд, модификация параметров `[hard]` — hooks выполняются детерминированно `[L2]` `[vendor]`
- PostToolUse: линтинг после Edit, валидация после Write `[hard]` — hooks выполняются детерминированно `[L2]` `[vendor]`
- Stop: проверка полноты перед завершением `[heuristic]` — зависит от качества чеклиста в навыке
- CI/CD как внешний enforcement для всех инструментов `[hard]` — не зависит от LLM compliance

**Workflow (3 шага):**
- spec-creation → spec-implementer → merge-helper — выровнен с complexity cliff (каждый шаг = individually simple) `[hard]` — обосновано complexity cliff `[L1]` `[peer-reviewed]`
- «Один шаг за сессию» — предотвращает рост контекста и деградацию compliance `[hard]` — обосновано Lost in the Middle `[L1]` `[peer-reviewed]` и Curse of Instructions `[L1]` `[peer-reviewed]`
- spec-implementer использует субагентов для параллельного исследования — обосновано разделением на Code Mapper и Data Flow Tracer `[heuristic]` — архитектурный паттерн dot_ai, требует local eval для подтверждения

## 5.4 Research Gaps и Roadmap

### Классификация текущих рекомендаций

Все практические рекомендации из §5.3 классифицированы по силе доказательства:

| Рекомендация | Тип | Источники | Что нужно для повышения |
|---|---|---|---|
| Корневой CLAUDE.md: ≤200 строк, 5–7 правил | `[hard]` | Curse of Instructions `[L1]`, Lost in the Middle `[L1]` | — |
| `.claude/rules/` с `paths:` frontmatter | `[hard]` | Claude Code architecture `[L2]` | — |
| Не дублировать правила между CLAUDE.md и skills | `[heuristic]` | Конечность бюджета внимания `[L2]` | Local eval EC-1 |
| Тело навыка: 500–1,500 токенов | `[heuristic]` | Community `[L3]` + vendor `[L2]` | Local eval EC-1 |
| Frontmatter с триггерами | `[hard]` | Claude Code architecture `[L2]` | — |
| Структура: Contract → Алгоритм → Правила → Примеры | `[hard]` | Lost in the Middle `[L1]` | — |
| Каждый навык = одна простая задача | `[hard]` | Complexity cliff `[L1]` | — |
| Supporting files one-level deep | `[heuristic]` | Agent Skills spec + Anthropic/OpenAI docs `[L2]` | Local eval EC-7 |
| Explore (Haiku) для параллельного исследования (≤5 агентов) | `[heuristic]` | Vendor `[L2]` | Local eval EC-4 |
| General-purpose для сложных задач | `[hard]` | Разделение контекста `[L2]` | — |
| Не делегировать тривиальные задачи (~12K overhead) | `[hard]` | Vendor measurement `[L2]` | — |
| Субагент возвращает 1,000–2,000 токенов | `[heuristic]` | Vendor `[L2]` | Local eval EC-4 |
| PreToolUse: блокировка опасных команд | `[hard]` | Hooks determinism `[L2]` | — |
| PostToolUse: линтинг после Edit | `[hard]` | Hooks determinism `[L2]` | — |
| Stop: проверка полноты | `[heuristic]` | Зависит от качества чеклиста | Local eval EC-5 |
| CI/CD как внешний enforcement | `[hard]` | Не зависит от LLM compliance | — |
| «Один шаг за сессию» | `[hard]` | Lost in the Middle `[L1]`, Curse of Instructions `[L1]` | — |
| LEARNINGS.md retrieval | `[hypothesis]` | Reflexion `[L1]`, логическая аналогия | Local eval EC-6 |

**Итого:** 10 `[hard]`, 7 `[heuristic]`, 1 `[hypothesis]`. Из 7 heuristic — 6 связаны с конкретными eval cases (EC-1, EC-4, EC-5, EC-6, EC-7), что даёт путь к повышению или понижению.

### Roadmap литобзора по направлениям

Ниже — направления, где текущий литобзор имеет gaps. Для каждого указаны: приоритет, текущее покрытие, что отсутствует, какие решения dot_ai зависят от направления, и какие источники искать.

#### P0 — Критичные gaps

**1. Instruction Following: пределы многоинструктивности**

| Поле | Значение |
|------|----------|
| **Текущее покрытие** | Curse of Instructions `[L1]`, IFEval/SIFo benchmarks, Instruction Hierarchy |
| **Что отсутствует** | Количественные пороги для frontier-моделей 2026: сколько именно инструкций соблюдается надёжно при разных типах задач (код, prose, research). Как сказывается длина промпта на compliance в диапазоне 500–5,000 токенов. Взаимодействие между инструкциями в skills и rules (конфликтующие приоритеты) |
| **Почему важно** | Рекомендации «5–7 правил в CLAUDE.md», «sweet spot 500–1,500 токенов» основаны на community/vendor данных `[heuristic]`. Без peer-reviewed порогов архитектура навыков может быть субоптимальна |
| **Решения dot_ai** | Размер и структура CLAUDE.md, количество rules, структура навыков (Workflow Contract), чеклисты в Stop-хоках |
| **Источники для поиска** | ManyIFEval/Curse of Instructions follow-up работы (ICLR 2026, EMNLP 2025), FollowBench v2, работы по instruction conflicts и priority resolution,[model-specific instruction compliance reports от Anthropic/OpenAI] |

**2. Agentic Coding Evals: валидация рекомендаций на реальных задачах**

| Поле | Значение |
|------|----------|
| **Текущее покрытие** | SWE-bench `[L1]`, RepoBench `[L1]`, Arize AI SWE-bench `[L3]` |
| **Что отсутствует** | Результаты SWE-bench Verified для Claude Code и аналогичных agent-инструментов. Анализ dependency utilization: используют ли агенты существующий код или переписывают. Разница между agent-agnostic и agent-specific eval методологиями |
| **Почему важно** | dot_ai рекомендует архитектуру навыков и workflow, но нет прямых eval-данных о том, как эти рекомендации влияют на success rate на реальных задачах |
| **Решения dot_ai** | Eval стратегия (local-eval-plan.md), архитектура spec-implementer, выбор между субагентами и основным контекстом |
| **Источники для поиска** | SWE-bench Verified leaderboard обновления 2026, RepoExec (execution-based eval), работы по agent evaluation methodology (AgentBench follow-up), vendor reports от Claude Code / Cursor / Copilot с метриками |

#### P1 — Важные gaps

**3. Context Engineering: long context vs retrieved context**

| Поле | Значение |
|------|----------|
| **Текущее покрытие** | Lost in the Middle `[L1]`, Li et al. RAG vs Long-Context `[L1]`, Anthropic context engineering `[L2]` |
| **Что отсутствует** | Количественное сравнение для задач codebase exploration (10–50 файлов). Пороги, при которых RAG/fragmentation (через субагенты) выигрывает у long context. Влияние evidence-first (quote-before-answer) на разные типы задач |
| **Почему важно** | Решение «субагент vs основной контекст» (EC-4) зависит от эмпирических порогов. Текущая рекомендация `[heuristic]` «≤5 Explore-агентов» не имеет количественного обоснования |
| **Решения dot_ai** | Архитектура spec-implementer (субагенты для сбора информации), навыки с evidence-first, порог целесообразности субагентов |
| **Источники для поиска** | Long context vs RAG работы 2025–2026, retrieval-augmented generation для code-specific задач, работы по top-k retrieval для multi-file кодовых баз, benchmarkи типа Needle in a Haystack для кода |

**4. Multi-Agent Systems: оркестрация и коммуникация**

| Поле | Значение |
|------|----------|
| **Текущее покрытие** | AgentBench `[L1]`, ChatDev `[L1]`, MetaGPT `[L1]`, CAMEL `[L1]`, AOrchestra `[L1]` `[preprint]` |
| **Что отсутствует** | Сравнительный анализ: single-agent с tools vs multi-agent orchestration для задач уровня spec-implementer. Коммуникационные паттерны между агентами (shared state vs message passing). Эмпирические данные об overhead оркестрации |
| **Почему важно** | dot_ai использует простую схему «основной агент + Explore-субагенты». Нет данных о том, когда более сложная оркестрация (fan-out/fan-in, shared state) оправдана |
| **Решения dot_ai** | Архитектура субагентов, выбор паттерна оркестрации, порог перехода от простых к сложным агентным схемам |
| **Источники для поиска** | AgentVerse, AutoGen multi-agent evals, работы по agent communication overhead, MetaGPT/ChatDev follow-up с quantitative comparisons, LangGraph orchestration patterns |

#### P2 — Перспективные gaps

**5. Skill Evolution / Memory: рефлексия и самообучение**

| Поле | Значение |
|------|----------|
| **Текущее покрытие** | Reflexion `[L1]`, Adaptive Memory Distillation `[L1]` `[preprint]`, LEARNINGS.md pattern `[hypothesis]` |
| **Что отсутствует** | Эмпирические данные о долгосрочном эффекте learning logs на качество задач. Порог prompt bloat: когда объём накопленного опыта начинает вредить. Eval-gated self-modification: как проверять качество само-модификаций навыков |
| **Почему важно** | Рекомендация LEARNINGS.md — единственная `[hypothesis]` в summary. Без eval-gated механизма есть риск накопления нерелевантного или некорректного «опыта» |
| **Решения dot_ai** | LEARNINGS.md в навыках, механизм дистилляции опыта, порог размера learning log |
| **Источники для поиска** | Reflexion follow-up (NeurIPS 2024–2026), работы по episodic memory для LLM-агентов, prompt bloat / context window management, self-modifying agents с safety constraints |

**6. Governance / Requirements: traceability и compliance**

| Поле | Значение |
|------|----------|
| **Текущее покрытие** | IEEE 29148 `[L2]`, RARE Framework `[L1]` `[preprint]`, GenAI for RE systematic review `[L1]` |
| **Что отсутствует** | Эмпирические данные о влиянии spec-driven development на качество AI-генерируемого кода. ADR (Architecture Decision Records) с evidence-based обоснованиями. Traceability между требованиями и сгенерированным кодом |
| **Почему важно** | dot_ai использует spec → implement → merge workflow, но нет данных о том, улучшает ли spec-driven подход результаты по сравнению с ad-hoc prompting |
| **Решения dot_ai** | spec-creation workflow, критерии качества spec (IEEE 29148 scoring), связь spec ↔ реализация ↔ тесты |
| **Источники для поиска** | AI-assisted requirements engineering (RE'2025, REFSQ 2026), traceability recovery для AI-generated code, spec-driven vs prompt-driven development сравнения, ADR patterns для AI systems |

### Правило: новые hard recommendations

**Новыe рекомендации уровня `[hard]` в `docs/` требуют:**
- Либо минимум один источник `[peer-reviewed]` с прямым доказательством
- Либо подтверждение через воспроизводимый `[local-eval]` (3+ повтора)
- Либо минимум один источник `[vendor]` + согласованность с `[peer-reviewed]` (только для инструмент-специфичных рекомендаций)

Рекомендации, не соответствующие этим критериям, публикуются как `[heuristic]` или `[hypothesis]` с явным указанием gaps в доказательной базе.

---

## 5.5 Динамическое создание агентов (dynamic agent templates)

Дополнительное исследование: [dynamic-agent-templates.md](dynamic-agent-templates.md)

**Ключевые находки:**

| Подход | Суть | Когда использовать |
|---|---|---|
| **Claude Code Subagents** | Статические (`.claude/agents/`) или CLI-defined, Impersonator-pattern для runtime | Когда типы задач известны заранее |
| **LangGraph Send API** | Динамический fan-out: `Send(node, state)` в runtime | Map-reduce, orchestrator-worker |
| **AOrchestra 4-tuple** `(I,C,T,M)` | Orchestrator создаёт агента «на лету» через Instruction, Context, Tools, Model | Complex long-horizon задачи |
| **AgentSpawn** | Runtime spawning по 5 метрикам сложности (interdependency, cyclomatic, failures, overflow, uncertainty) | Кодогенерация с непредсказуемой сложностью |
| **PydanticAI Genie** | Агент сам генерирует и регистрирует tools через `ast.parse` + `exec` | Когда набор инструментов неизвестен заранее |

**Практический вывод для dot_ai**: для текущего workflow (spec-creation -> spec-implementer -> merge-helper) динамическое создание агентов не требуется — все роли предопределены. Паттерн AOrchestra `(I,C,T,M)` может быть полезен при расширении на произвольные задачи (research mode, code review mode).

## 5.6 Local Eval Plan

Детальный план: [local-eval-plan.md](../researches/local-eval-plan.md)

Рекомендации `[heuristic]` и `[hypothesis]` из данного документа связаны с конкретными eval cases для эмпирической проверки:

| Eval Case | Проверяемая рекомендация | Текущий тип | Ожидаемый результат |
|-----------|------------------------|-------------|-------------------|
| **EC-1** Short vs Long skill | «Тело навыка: 500–1,500 токенов» | `[heuristic]` | Определить порог для dot_ai навыков |
| **EC-2** Examples vs Rules | «Примеры важнее правил» | `[heuristic]` | Повысить до `[hard]` или уточнить |
| **EC-3** Evidence-first | «Цитаты перед ответом улучшают точность» | `[L2]` | Валидация в контексте dot_ai |
| **EC-4** Subagent vs Main | «Explore для параллельного исследования» | `[heuristic]` | Определить порог целесообразности |
| **EC-5** Prompt vs Hook | «Hooks для критичных ограничений» | `[hard]` | Количественное подтверждение |
| **EC-6** LEARNINGS.md | «Reflexion через learning log» | `[heuristic]` | Подтвердить или отвергнуть |
| **EC-7** Supporting files | «SKILL.md как маршрутизатор + focused references/scripts/assets» | `[heuristic]` | Сравнить monolithic skill vs supporting-file skill на workflow-задачах |

**Правило:** результат eval case может повысить тип рекомендации (`heuristic` → `hard`) или понизить (`heuristic` → `hypothesis`).

---

## 5.7 Библиография

### L1 — Рецензируемые статьи (arxiv, Nature, конференции)

1. Vaswani, A., Shazeer, N., et al. "Attention Is All You Need." NeurIPS 2017. arXiv:1706.03762 `[peer-reviewed]`
2. Liu, N.F., Lin, K., Hewitt, J., et al. "Lost in the Middle: How Language Models Use Long Contexts." TACL 2024, Vol. 12, pp. 157-173. arXiv:2307.03172 `[peer-reviewed]`
3. Harada, K., Yamazaki, Y., et al. "Curse of Instructions: Large Language Models Cannot Follow Multiple Instructions at Once." ICLR 2025 `[peer-reviewed]`
4. Wallace, E., Xiao, K., et al. "The Instruction Hierarchy: Training LLMs to Prioritize Privileged Instructions." NeurIPS 2024. arXiv:2404.13208 `[peer-reviewed]`
5. "The Failure of Instruction Hierarchies in Large Language Models." AAAI `[peer-reviewed]`
6. Tripathi, V., Allu, U., Ahmed, B. "The Instruction Gap: LLMs Get Lost in Following Instruction." arXiv:2601.03269, 2025 `[preprint]`
7. "When Thinking Fails: The Pitfalls of Reasoning for Instruction-Following in LLMs." Amazon Science, 2025. OpenReview: w5uUvxp81b `[peer-reviewed]`
8. "ReasonIF: Large Reasoning Models Fail to Follow Instructions During Reasoning." Together AI, 2025 `[preprint]`
9. "How You Prompt Matters! Task-Oriented Constraints in System Prompts." EMNLP 2024 Findings `[peer-reviewed]`
10. "Large Language Model Instruction Following: A Survey." Computational Linguistics, MIT Press, 2024, Vol. 50, No. 3 `[peer-reviewed]`
11. "When Does Divide and Conquer Work for Long Context LLMs." arXiv:2506.16411, 2025 `[preprint]`
12. Khot, T., et al. "Decomposed Prompting: A Modular Approach for Solving Complex Tasks." ICLR 2023 `[peer-reviewed]`
13. Zhou, D., et al. "Least-to-Most Prompting Enables Complex Reasoning in Large Language Models." ICLR 2022 `[peer-reviewed]`
14. Rameshkumar, R., et al. "Reasoning Models Reason Well, Until They Don't." IJCNLP 2025. arXiv:2510.22371 `[peer-reviewed]`
15. Shojaee, P., et al. "The Illusion of Thinking." Apple ML Research, 2025 `[preprint]`
16. Jiang, S., Nam, D. "An Empirical Study of Developer-Provided Context for AI Coding Assistants in Open-Source Projects." arXiv:2512.18925, 2025 `[preprint]`
17. Xu, Z., Peng, Y., et al. "AOrchestra: Automating Sub-Agent Creation for Agentic Orchestration." arXiv:2602.03786, 2026 `[preprint]`
18. Costa, I. "AgentSpawn: Adaptive Multi-Agent Collaboration Through Dynamic Spawning for Long-Horizon Code Generation." arXiv:2602.07072, 2026 `[preprint]`
19. Chen, G., Dong, S., et al. "AutoAgents: A Framework for Automatic Agent Generation." IJCAI 2024. arXiv:2309.17288 `[peer-reviewed]`
20. Zhang, W., et al. "AgentOrchestra: A Hierarchical Multi-Agent Framework for General-Purpose Task Solving." arXiv:2506.12508, 2025 `[preprint]`
21. Jiang, Y., et al. "FollowBench: A Multi-level Fine-grained Constraints Following Benchmark for Large Language Models." ACL 2024. arXiv:2310.20410 `[peer-reviewed]`
22. Zhou, J., et al. "Instruction-Following Evaluation for Large Language Models." arXiv:2311.07911, 2023 `[peer-reviewed]`
23. "The SIFo Benchmark: Investigating the Sequential Instruction Following Ability of Large Language Models." EMNLP 2024 Findings. arXiv:2406.19999 `[peer-reviewed]`
24. Shinn, N., et al. "Reflexion: Language Agents with Verbal Reinforcement Learning." NeurIPS 2023. arXiv:2303.11366 `[peer-reviewed]`
25. "What Deserves Memory: Adaptive Memory Distillation for LLM Agents." arXiv:2508.03341, 2025 `[preprint]`
26. Li, Z., et al. "Retrieval Augmented Generation or Long-Context LLMs? A Comprehensive Study and Hybrid Approach." EMNLP 2024. arXiv:2407.16833 `[peer-reviewed]`
27. "Long Context vs. RAG for LLMs: An Evaluation and Revisits." arXiv:2501.01880, 2025 `[preprint]`
28. Jimenez, C.E., et al. "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?" ICLR 2024. arXiv:2310.06770 `[peer-reviewed]`
29. Luo, T., et al. "RepoBench: Benchmarking Repository-Level Code Auto-Completion Systems." ICLR 2024. arXiv:2306.03091 `[peer-reviewed]`
30. Liu, X., et al. "AgentBench: Evaluating LLMs as Agents." ICLR 2024. arXiv:2308.03688 `[peer-reviewed]`
31. Chen, W., et al. "ChatDev: Communicative Agents for Software Development." ACL 2024. arXiv:2307.07924 `[peer-reviewed]`
32. Hong, S., et al. "MetaGPT: Meta Programming for Multi-Agent Collaborative Framework." ICLR 2024. arXiv:2308.00352 `[peer-reviewed]`
33. Li, G., et al. "CAMEL: Communicative Agents for Mind Exploration of Large Language Model Society." NeurIPS 2023. arXiv:2303.17760 `[peer-reviewed]`
34. "Auto-SLURP: A Benchmark Dataset for Evaluating Multi-Agent Frameworks." EMNLP 2025 Findings. arXiv:2504.18373 `[peer-reviewed]`
35. "Generative AI for Requirements Engineering: A Systematic Literature Review." Wiley SPE, 2024. arXiv:2409.06741 `[peer-reviewed]`
36. "An LLM-based Approach to Recover Traceability Links between Requirements." ACM, 2024 `[peer-reviewed]`
37. "Risk-Aware Requirements Engineering for GenAI-Enabled Systems (RARE Framework)." SSRN, 2025 `[preprint]`

### L2 — Официальная документация и блоги `[vendor]`

1. Anthropic. "Effective Context Engineering for AI Agents." 2025. anthropic.com/engineering/effective-context-engineering-for-ai-agents
2. Anthropic. "Prompt Engineering for Claude's Long Context Window." 2023. anthropic.com/news/prompting-long-context
3. Anthropic. "How Claude Code works." code.claude.com/docs/en/how-claude-code-works
4. Anthropic. "Extend Claude with skills." code.claude.com/docs/en/skills
5. Anthropic. "Skill authoring best practices." platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
6. OpenAI. "Skills in ChatGPT." help.openai.com/en/articles/20001066 `[vendor]`
7. Agent Skills. "Specification." agentskills.io/specification `[spec]`
8. Anthropic. "Automate with hooks." code.claude.com/docs/en/hooks
9. Anthropic. "Subagents." code.claude.com/docs/en/subagents
10. Anthropic. "Memory." code.claude.com/docs/en/memory
11. Anthropic. "Settings." code.claude.com/docs/en/settings
12. Anthropic. "Compaction." platform.claude.com/docs/en/build-with-claude/compaction
13. Cursor. "Rules." docs.cursor.com/context/rules
14. GitHub. "Custom instructions for GitHub Copilot." docs.github.com/copilot/customizing-copilot
15. Aider. "Conventions." aider.chat/docs/usage/conventions.html
16. LangChain. "Use the graph API — Map-Reduce and Send API." docs.langchain.com/oss/python/langgraph/use-graph-api
17. Microsoft. "Selector Group Chat — AutoGen." microsoft.github.io/autogen/dev/user-guide/agentchat-user-guide/selector-group-chat.html
18. CrewAI. "Tasks." docs.crewai.com/en/concepts/tasks
19. Pydantic. "Agents — PydanticAI Docs." pydantic.dev/docs/ai/core-concepts/agent/
20. Microsoft Azure. "Agent Factory: The new era of agentic AI." azure.microsoft.com/en-us/blog/agent-factory, 2025

### L3 — Блоги, статьи, сообщество `[community]`

1. Arize AI. "CLAUDE.md Best Practices from Prompt Learning." arize.com/blog — +5.19% to +10.87% SWE-bench improvement `[Evidence Scope: SWE-bench, модель/дата не указаны, community measurement]`
2. Particula Tech. "Optimal Prompt Length Before AI Performance Degrades." 2025. particula.tech/blog `[Evidence Scope: Q&A юридические документы, 6,000→1,800 токенов, модель не указана]`
3. AgentRuleGen. ".cursorrules vs CLAUDE.md vs Copilot Instructions: 2026 Comparison." agentrulegen.com/guides/cursorrules-vs-claude-md
4. Agensi. "SKILL.md vs CLAUDE.md vs .cursorrules Compared." agensi.io/learn/skill-md-vs-claude-md-vs-cursorrules
5. Medium. "Your AI Coding Agent Is Only as Good as Its Rules." medium.com/@alexefimenko
6. dev.to. "AI Agents Don't Follow Your Rules — Here's a Compiler That Makes Them." dev.to/whitehatd
7. Shchegrikovich. "Dynamic Sub Agents in Claude Code." shchegrikovich.substack.com, 2025
8. Medium/@mudassarm30. "Dynamically Generating Pydantic AI Agent Tools." 2024
9. Medium/@gazzumatteo. "Meta-Agents: Building Agents That Create & Optimize Agents." 2025
10. AgentVidia. "LangGraph Fan-Out Fan-In Pattern." agentvidia.com, 2025
