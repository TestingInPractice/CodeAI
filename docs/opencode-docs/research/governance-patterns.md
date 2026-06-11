# Паттерны управления AI-агентными проектами: ADR, SDD, Governance

> **Дата:** 2026-05-07
> **Версия:** 1.0
> **Цель:** Сравнительный анализ индустриальных практик управления развитием проектов с AI-агентами, позиционирование dot_ai относительно аналогов

---

## 1. Architecture Decision Records (ADR)

### 1.1 Определение

ADR — практика документирования архитектурных решений в виде отдельных файлов в репозитории. Каждое решение = один markdown-файл с контекстом, альтернативами и обоснованием выбора `[L2]`.

Майкрофаулер определяет ADR как «короткий документ, который фиксирует и объясняет одно решение, значимое для продукта или экосистемы» `[L2]`.

### 1.2 MADR — доминирующий формат

MADR (Markdown Architectural Decision Records) — стандартизированный markdown-шаблон, v4.0.0 (2024). Наиболее распространённый формат ADR в индустрии `[L2]`.

**Структура хранения:**

```
docs/decisions/
├── 0001-record-architecture-decisions.md
├── 0002-use-python-fastapi.md
└── 0003-postgresql-over-mongodb.md
```

**Структура записи MADR:**

```
# {короткое название}

## Context and Problem Statement
{2–3 предложения: контекст и проблема}

## Decision Drivers
* {фактор 1}
* {фактор 2}

## Considered Options
* {вариант 1}
* {вариант 2}
* {вариант 3}

## Decision Outcome
Chosen option: "{вариант}", because {обоснование}.

### Consequences
* Good, because {положительное последствие}
* Bad, because {отрицательное последствие}

### Confirmation
{как проверить, что решение реализовано корректно}
```

MADR имеет научную публикацию и развивается с 2017 года. Официальный репозиторий: [github.com/adr/madr](https://github.com/adr/madr) `[L2]`.

**Статусная модель ADR:**

```
Proposed → Accepted → Deprecated → Superseded by ADR-XXXX
                  ↘ Rejected
```

### 1.3 DECISIONS.md — индексный файл

Некоторые проекты используют `DECISIONS.md` в корне как индекс всех ADR-файлов. Практика встречается у Microsoft, Renovate, Embedded Artistry `[L2]` `[L3]`.

Microsoft Engineering Playbook рекомендует ADR как часть Design Decision Log: первое ADR в проекте — решение использовать ADR для трекинга решений `[L2]`.

**Реальные примеры:**

| Проект | Подход | Путь |
|--------|--------|------|
| [Renovate](https://github.com/renovatebot/renovate/blob/main/docs/development/design-decisions.md) | Единый файл | `docs/development/design-decisions.md` |
| [CSAF CMS](https://github.com/secvisogram/csaf-cms-backend/blob/main/documents/architecture-decisions.md) | Единый файл | `documents/architecture-decisions.md` |
| [Embedded Artistry](https://embeddedartistry.com/blog/2018/04/05/documenting-architectural-decisions-within-our-repositories/) | Нумерованные файлы | `docs/architecture/decisions/NNNN-*.md` |
| [MADR](https://github.com/adr/madr/tree/develop/docs/decisions) | Нумерованные файлы | `docs/decisions/NNNN-*.md` |

### 1.4 Рекомендации AWS

AWS опубликовал best practices для ADR `[L2]`:

1. Начинать с простого — plain markdown файлов в репозитории
2. Хранить рядом с кодом — не в Confluence/wiki, а в Git
3. Нумеровать последовательно — для трассировки и ссылок
4. Включать статус — Proposed/Accepted/Deprecated/Superseded
5. Не удалять — даже отменённые решения сохраняют ценность

Исследование 2025 года показало, что команды, тратящие 20–30% времени координации на архитектурное выравнивание, часто не имеют устойчивых практик документирования решений `[L3]`.

---

## 2. Spec-Driven Development (SDD)

### 2.1 Определение

SDD — методология 2025 года, заменяющая хаотичную AI-генерацию кода («vibe coding») структурированным процессом: spec → plan → tasks → code. Основной инструмент — [GitHub Spec Kit](https://github.com/github/spec-kit) `[L2]`.

### 2.2 Governance-слой: constitution.md

Ключевой артефакт SDD — `constitution.md`, файл «non-negotiable principles», всегда находящийся в контексте AI-агента. Определяет неизменяемые правила проекта `[L2]` `[L3]`.

**Типичное содержимое constitution.md:**

- Стек технологий (например, «Always use Python»)
- Архитектурные принципы (Library-First, Test-First)
- Ограничения (CLI Interface, no GUI)
- Стандарты кодирования

Расположение: `.specify/memory/constitution.md` или `/memory/constitution.md` `[L3]`.

### 2.3 SDD-пайплайн

```
constitution.md  ← Non-negotiable principles (governance-слой)
       ↓
    spec.md       ← Feature/architecture specification
       ↓
   plan.md        ← Implementation plan
       ↓
  tasks.md        ← Granular task breakdown
       ↓
  AI Agent Code Generation
```

`constitution.md` загружается в каждый контекст генерации, обеспечивая соответствие всех выходов фундаментальным правилам проекта `[L3]`.

### 2.4 Generator-Verifier паттерн

Распространённый паттерн в SDD: один агент генерирует код, второй (или автоматический test suite) верифицирует результат против spec `[L3]`. Аналог разделения architect/editor в Claude Code.

### 2.5 Инструменты SDD

| Инструмент | Подход | Особенности |
|------------|--------|-------------|
| [GitHub Spec Kit](https://github.com/github/spec-kit) | constitution.md → spec → plan → tasks | Continuous architecture governance, CI-интеграция |
| [Kiro IDE](https://www.slideshare.net/slideshow/orchestrating-ai-agents-in-spec-driven-development-with-kiro-ide/286453580) | Spec-driven orchestration | IDE-интеграция, visual spec editing |
| [SDD Pilot](https://github.com/topics/spec-driven) | Structured phases + quality gates | Open-source toolkit |
| [BMAD-Method](https://www.linkedin.com/pulse/from-vibe-coding-spec-driven-development-master-github-rick-hightower-riifc) | Agent roles: Architect → Editor → QA | Multi-agent collaborative framework |

---

## 3. Сравнение с dot_ai

### 3.1 Маппинг концепций

| Индустриальный паттерн | dot_ai аналог | Примечание |
|------------------------|---------------|------------|
| `constitution.md` (SDD) | `CLAUDE.md` | Оба — governance-слой, всегда в контексте |
| ADR (MADR) | Секция spec «Архитектурные решения» | В dot_ai решения внутри spec, не в отдельных файлах |
| `spec.md` (SDD) | `.ai/specs/{branch}.md` (IEEE 29148) | dot_ai строже: IEEE 29148 с количественным score ≥85 |
| `plan.md` + `tasks.md` (SDD) | Этапы реализации в spec | В dot_ai план и задачи — секции внутри spec |
| Generator-Verifier (SDD) | spec-implementer → test-writer | Разделены как отдельные шаги workflow |
| Workflow pipeline (SDD) | spec-creation → implementer → merge | dot_ai: 3 обязательных шага с ENTRY/EXIT |
| Нумерация NNNN (ADR) | SemVer (dot_ai) | dot_ai версионирует specs, не отдельные решения |

### 3.2 Преимущества dot_ai

- **Tighter-интеграция с Claude Code**: нативные skills, rules, hooks, sub-agents — не агностик-тулкит `[L2]`
- **Строгая валидация**: IEEE 29148:2018 score ≥85 vs произвольные spec-форматы SDD `[L2]`
- **Детерминированный enforcement**: hooks для блокировки, settings для конфигурации — не только инструкции `[L2]`
- **Workflow guarantees**: ENTRY/EXIT условия, «один шаг за сессию» — предотвращает деградацию `[L1]`
- **Source of truth модель**: dot_ai → init → целевой проект — централизованное управление `[L3]`

### 3.3 Зоны роста

- **ADR-слой**: в dot_ai архитектурные решения живут внутри specs и теряются при архивации. Отдельный `docs/decisions/` с MADR-шаблоном обеспечил бы кросс-фичевую видимость решений `[L2]`
- **Superseded-цепочки**: ADR поддерживает «superseded by ADR-XXXX» — явное отслеживание эволюции решений. В dot_ai нет аналога `[L2]`
- **constitution.md-паттерн**: SDD выносит governance в отдельный файл, не смешивая с конфигурацией. В dot_ai CLAUDE.md совмещает обе роли — проще, но растёт при росте проекта `[L3]`

---

## 4. Governance и Requirements Engineering: эмпирическая база

### 4.1 IEEE 29148:2018 и трассируемость

**ISO/IEC/IEEE 29148:2018** — международный стандарт для процессов requirements engineering на протяжении жизненного цикла систем и ПО `[L2]`.

Ключевые артефакты стандарта:
- **Requirements Traceability Matrix** — структурированный артефакт, связывающий требования с их вышестоящими источниками (Section 5.2.5)
- **Requirements justification** — каждое требование должно иметь rationale и быть проверяемым
- **Базовая линия требований** — формальная точка для управления изменениями

**Трассируемость как governance-механизм** `[L2]`:
- SEBoK (Systems Engineering Body of Knowledge) рассматривает IEEE 29148 как primary reference для system definition и requirements processes
- Трассируемость обеспечивает: audit trail от решения к требованию, impact analysis при изменениях, compliance verification

### 4.2 AI-assisted Requirements Engineering

**«Generative AI for Requirements Engineering: A Systematic Literature Review»** (2024, Wiley SPE Journal) `[L1]` `[peer-reviewed]`:
- Комплексный SLR: анализ state-of-the-art применения GenAI в RE
- Покрывает: автоматизацию elicitation, traceability recovery, NFR management, consistency checking
- Вывод: GenAI улучшает скорость создания RE-артефактов, но качество требует human verification
- Проблема: LLM-generated требования могут быть правдоподобными, но неточными (аналог галлюцинаций) `[Evidence Scope: систематический обзор, дата: 2024, benchmark: RE literature analysis, source: peer-reviewed]`

**«From Elicitation to Evolution: AI-Assisted Framework for Requirements Quality, Traceability, and NFR Management»** (2025) `[L1]` `[preprint]`:
- Предлагает фреймворк для улучшения качества RE-артефактов через AI-assistance
- Три компонента: quality checking, traceability recovery, NFR management
- Проблема адресуется: RE-артефакты часто неоднозначны, противоречивы и слабо трассируемы
- Подтверждает ценность structured traceability — аналогично ADR + spec в dot_ai

**«An LLM-based Approach to Recover Traceability Links between Requirements»** (ACM 2024) `[L1]` `[peer-reviewed]`:
- Использование LLM для автоматического восстановления traceability links между требованиями
- Показывает: LLM способны выявлять семантические связи между requirements, которые rule-based подходы пропускают

### 4.3 Risk-Aware Requirements Engineering

**RARE Framework** (SSRN 2025) `[L1]` `[preprint]`:
- Risk-Aware Requirements Engineering for Generative AI-Enabled Systems
- Системно интегрирует GenAI-specific риски в RE-процесс
- Эмпирически валидирован: framework помогает выявлять риски, которые традиционные RE-подходы пропускают
- Ключевой инсайт: GenAI-системы требуют **расширенных** требований (beyond functional/non-functional) — safety, transparency, accountability constraints

### 4.4 Design Rationale и ADR: эмпирическая база

**ADR empirical evidence** `[L2]` `[L3]`:
- AWS, Microsoft, Embedded Artistry рекомендуют ADR для documenting architectural decisions
- Исследование 2025: команды, тратящие 20–30% координации на архитектурное выравнивание, часто не имеют устойчивых практик документирования решений — ADR снижает эту долю `[L3]`
- MADR имеет научную публикацию и развивается с 2017 года `[L2]`
- **Research gap:** прямых peer-reviewed исследований эффективности ADR на качестве ПО немного — в основном case studies и vendor recommendations

**Design Rationale** `[L2]`:
- IEEE 29148 требует rationale для каждого требования (Section 5.2.4)
- ADR-формат MADR включает `Decision Drivers` и `Decision Outcome` — это и есть design rationale
- В dot_ai: секция spec «Архитектурные решения» — реализует тот же паттерн inline

### 4.5 Spec-Driven Development: эмпирические данные

**GitHub Spec Kit** (2025) `[L2]` `[vendor]`:
- SDD-пайплайн: constitution.md → spec → plan → tasks → code
- Generator-Verifier паттерн: один агент генерирует, второй верифицирует против spec
- Кросс-инструментальная конвергенция: Claude Code (spec-creation → implementer → merge), Copilot (spec-driven modes), Cursor (spec-templates) `[L2]`

**«Architecting LLM-Based Multi-Agent Systems»** (TechRxiv, 2025) `[L1]` `[preprint]`:
- Behavioral evaluation multi-agent систем — оценивает не только конечный результат, но и процесс принятия решений
- Вывод: spec-driven orchestration (predefined workflow) превосходит ad-hoc координацию для структурированных задач

### 4.6 Практический вывод для dot_ai

1. **IEEE 29148 — обоснованная основа** для spec-формата: requirements traceability, justification, verifiability встроены в стандарт `[hard]` `[L2]`
2. **AI-assisted RE подтверждает ценность structured specs**, но требует human verification — генерация requirements без валидации рискованна `[hard]` `[L1]` `[peer-reviewed]`
3. **Design rationale в spec** — соответствует и IEEE 29148, и ADR-подходу; inline-формат (внутри spec) подходит для небольших проектов, отдельный `docs/decisions/` — для растущих `[heuristic]` `[L2]`
4. **RARE framework**: GenAI-системы требуют расширенных требований (safety, transparency) — dot_ai specs могут включать отдельную секцию GenAI-specific constraints `[hypothesis]` `[L1]` `[preprint]`
5. **Research gap:** прямые peer-reviewed исследования эффективности ADR и spec-driven development ограничены — обоснование dot_ai опирается на стандарты (IEEE 29148), vendor-практики и аналогии из RE-литературы, не на прямые экспериментальные данные

---

## 5. Рекомендации для dot_ai

### 5.1 Опциональный ADR-слой

Если проект накапливает кросс-фичевые решения, добавить `docs/decisions/` с MADR-шаблоном:

```
docs/decisions/
├── 0001-use-claude-code-skills.md
├── 0002-ieee-29148-spec-format.md
└── 0003-three-step-workflow.md
```

Не обязательно для всех проектов — только когда решений >5 и они пересекают границы specs.

### 5.2 Не дублировать SDD

dot_ai уже реализует SDD-пайплайн с более строгими гарантиями. Не нужно внедрять GitHub Spec Kit поверх — это дублирование.

### 5.3 Рассмотреть DECISIONS.md как опциональный шаблон

Добавить `templates/DECISIONS.md.tpl` в dot_ai для проектов, которым нужен ADR-индекс. Не обязательно при установке — доступен по запросу.

---

## Библиография

### L1 — Рецензируемые статьи

1. Zigman, M., et al. "Markdown Architectural Decision Records: Format and Tool Support." Scientific publication, 2018.
2. "Generative AI for Requirements Engineering: A Systematic Literature Review." Wiley Software: Practice and Experience, 2024. arXiv:2409.06741 `[peer-reviewed]`
3. "An LLM-based Approach to Recover Traceability Links between Requirements." ACM, 2024 `[peer-reviewed]`
4. Liu, X., et al. "AgentBench: Evaluating LLMs as Agents." ICLR 2024. arXiv:2308.03688 `[peer-reviewed]`
5. Chen, W., et al. "ChatDev: Communicative Agents for Software Development." ACL 2024. arXiv:2307.07924 `[peer-reviewed]`
6. Hong, S., et al. "MetaGPT: Meta Programming for Multi-Agent Collaborative Framework." ICLR 2024. arXiv:2308.00352 `[peer-reviewed]`
7. Li, G., et al. "CAMEL: Communicative Agents for Mind Exploration of Large Language Model Society." NeurIPS 2023. arXiv:2303.17760 `[peer-reviewed]`
8. "Auto-SLURP: A Benchmark Dataset for Evaluating Multi-Agent Frameworks." EMNLP 2025 Findings. arXiv:2504.18373 `[peer-reviewed]`
9. "Risk-Aware Requirements Engineering for Generative AI-Enabled Systems (RARE Framework)." SSRN, 2025 `[preprint]`
10. "From Elicitation to Evolution: AI-Assisted Framework for Requirements Quality, Traceability, and NFR Management." 2025 `[preprint]`
11. "Architecting LLM-Based Multi-Agent Systems." TechRxiv, 2025 `[preprint]`

### L2 — Официальная документация и блоги

1. ADR GitHub. "Architectural Decision Records." [adr.github.io](https://adr.github.io/)
2. ADR GitHub. "MADR — Markdown Architectural Decision Records." [adr.github.io/madr](https://adr.github.io/madr/)
3. ADR GitHub. "MADR Repository." [github.com/adr/madr](https://github.com/adr/madr)
4. Fowler, M. "ArchitectureDecisionRecord." [martinfowler.com/bliki/ArchitectureDecisionRecord.html](https://martinfowler.com/bliki/ArchitectureDecisionRecord.html)
5. Microsoft. "Design Decision Log — Engineering Fundamentals Playbook." [microsoft.github.io/code-with-engineering-playbook](https://microsoft.github.io/code-with-engineering-playbook/design/design-reviews/decision-log/)
6. AWS. "Master Architecture Decision Records (ADRs): Best Practices." [aws.amazon.com/blogs/architecture](https://aws.amazon.com/blogs/architecture/master-architecture-decision-records-adrs-best-practices-for-effective-decision-making/)
7. GitHub. "spec-kit: Toolkit for Spec-Driven Development." [github.com/github/spec-kit](https://github.com/github/spec-kit)
8. GitHub Blog. "Spec-driven development with AI." [github.blog/ai-and-ml/generative-ai](https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/)
9. Embedded Artistry. "Documenting Architectural Decisions Within Our Repositories." [embeddedartistry.com](https://embeddedartistry.com/blog/2018/04/05/documenting-architectural-decisions-within-our-repositories/)
10. Loqbooq. "ADR Templates in Markdown." [loqbooq.app/blog](https://loqbooq.app/blog/architectural-decision-record-templates)
11. ISO/IEC/IEEE 29148:2018. "Systems and Software Engineering — Life Cycle Processes — Requirements Engineering." `[standard]`
12. SEBoK. "ISO/IEC/IEEE 29148." [sebokwiki.org](https://sebokwiki.org/wiki/ISO/IEC/IEEE_29148) `[standard]`

### L3 — Блоги, статьи, сообщество

1. LinkedIn (2025). "Architecture Decision Records: From Documentation Theater to..." — исследование ADR-эффективности: команды с 20–30% координации часто без устойчивых практик
2. Level Up (GitConnected). "Exploring SDD: A Practical Guide with GitHub SpecKit." [levelup.gitconnected.com](https://levelup.gitconnected.com/exploring-spec-driven-development-sdd-a-practical-guide-with-github-speckit-and-copilot-72fd9a70535a)
3. Linuxera. "Spec-Driven Development with Spec Kit." [linuxera.org](https://linuxera.org/spec-driven-development-with-spec-kit/)
4. Medium (Predict). "Spec-Driven Development with AI Coding Agents: The Definitive Guide." [medium.com/predict](https://medium.com/predict/spec-driven-development-with-ai-coding-agents-the-definitive-guide-453fba1baf39) — Generator-Verifier паттерн
5. Medium (@tonylixu). "AI-Native Dev 3 — Spec-Driven Development." — `constitution.md` + `specs` как governance-паттерн
6. Orchestrator.dev. "Spec-Driven Development: Building Production-Ready Software." [orchestrator.dev/blog](https://orchestrator.dev/blog/2025-12-16-spec_driven_dev_article/)
7. LinkedIn (Hightower). "From 'Vibe Coding' to Spec-Driven Development." — BMAD-Method, agent roles
8. Augment Code. "AI Spec Template." [augmentcode.com/guides](https://www.augmentcode.com/guides/ai-spec-template) — `constitution.md` location patterns
9. Startupbricks. "Architecture Decision Records for Startups: The Complete 2025 Guide." [startupbricks.in](https://www.startupbricks.in/blog/architecture-decision-records-startups-guide)
10. Handsonarchitects (2025). "Making Better Architectural Decisions Thanks to Slow Thinking." — ADR + когнитивная наука
