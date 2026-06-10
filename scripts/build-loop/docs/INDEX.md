# CodeAI Docs — База знаний

> Структурированная документация по AI-assisted разработке: фреймворки, MCP, OpenCode, best practices, архитектура, инструменты.

---

## 📂 01. Фреймворки AI-разработки

**↪️ [[01-frameworks/README|Все материалы категории →]]**

### GSD (Get Shit Done)
| Файл | Описание |
|------|----------|
| `01-frameworks/2025-07-26_GSD-Superpowers.md` | 🎥 GSD & Superpowers — SDLC эволюция 2026, 6 core hooks + 73 advanced, 7 Superpowers skills |
| `01-frameworks/2025-07-26_GSD-Superpowers-thesis.md` | 📋 Структурированные тезисы для агента |
| `01-frameworks/2025-06-07_GSD-vs-Paul.md` | 🎥 7 проблем GSD и как Paul решает их через sequential processing + UAT |
| `01-frameworks/2025-06-07_GSD-vs-Paul-thesis.md` | 📋 Тезисы: context loss, broken loop, fake verification, drift, token cost |
| `01-frameworks/2025-07-26_GSD-for-OpenCode.md` | 🎥 GSD Tasher'a для OpenCode — sub-agent архитектура, parallel execution |
| `01-frameworks/2025-07-26_GSD-for-OpenCode-thesis.md` | 📋 Тезисы для адаптации GSD под OpenCode |
| `01-frameworks/2025-07-26_GSD-vs-OpenSpec.md` | 🎥 Сравнение GSD и OpenSpec на NewWriter: 126M vs 35M токенов |
| `01-frameworks/2025-07-26_GSD-vs-OpenSpec-thesis.md` | 📋 Тезисы: когда выбирать GSD, когда OpenSpec |
| 📎 `docs/opencode-docs/gsd/35-gsd-get-shit-done.md` | GSD методология — spec-driven development через контекст-инжиниринг |

### GStack
| Файл | Описание |
|------|----------|
| 📎 `docs/opencode-docs/gstack/32-gstack-gsd-superpower-workflow.md` | GStack + GSD + Superpowers — объединение Spec-фреймворков |
| 📎 `docs/opencode-docs/gstack/33-working-with-gstack.md` | Работа с GStack — AI-инжиниринг в 10-15 параллельных спринтах |
| 📎 `docs/opencode-docs/transcripts/gstack-gsd-superpower-workflow-transcript.md` | 🎥 Стенограмма видео GStack+GSD+Superpowers Workflow |

### Superpowers
| Файл | Описание |
|------|----------|
| 📎 `docs/opencode-docs/superpowers/34-superpowers-methodology.md` | Superpowers — полная методология: TDD, 2-stage review, subagent-driven |

### DOTI
| Файл | Описание |
|------|----------|
| `01-frameworks/2025-07-26_DOTI.md` | 🎥 DOTI — ИИ-агенты без хаоса в коде (годовой опыт, 1326 строк) |
| `01-frameworks/2025-07-26_DOTI-thesis.md` | 📋 Тезисы: Context → Plan → Execute → Verify |

### OpenSpec
| 📎 `docs/opencode-docs/build-loop/49-build-loop-reference.md` | Build Loop — GStack → GSD → Superpower → Ralph Loop |
| 📎 `docs/opencode-docs/coding-agent-harness/47-components-of-a-coding-agent.md` | 6 компонентов coding agent harness |

---

## 📂 02. MCP (Model Context Protocol)

**↪️ [[02-mcp/README|Все материалы категории →]]

| Файл | Описание |
|------|----------|
| `02-mcp/2025-06-07_MCP-tools-telegram-watcher.md` | 🎥 MCP Tools: 6 фич протокола, Telegram Watcher на Python |
| `02-mcp/2025-06-07_MCP-tools-telegram-watcher-thesis.md` | 📋 Тезисы: принцип "одно действие вместо трёх", CLI/агент подключение |
| `02-mcp/obsidian-hybrid-search-ohs.md` | 📄 OHS — MCP для семантического поиска по Obsidian (BM25 + fuzzy + semantic) |
| 📎 `docs/opencode-docs/astronomer-agents/45-astronomer-agents.md` | Astronomer/agents — MCP для Airflow |
| 📎 `docs/opencode-docs/22-mcp.md` | OpenCode MCP документация |

---

## 📂 03. OpenCode & Agent Configuration

**↪️ [[03-opencode-config/README|Все материалы категории →]]**

### OpenCode Docs
| Файл | Описание |
|------|----------|
| 📎 `docs/opencode-docs/01-intro.md` — `29-ecosystem.md` | Полная документация OpenCode (29 разделов) |
| 📎 `docs/opencode-guide/00-overview.md` — `09-project-example-step-2.md` | Гайд по настройке OpenCode-проекта (10 файлов) |

### AGENTS.md / CLAUDE.md
| Файл | Описание |
|------|----------|
| `03-opencode-config/2025-06-07_AGENTS-CLAUDE-howto.md` | 🎥 AGENTS.md и CLAUDE.md: как готовить? |
| `03-opencode-config/2025-06-07_AGENTS-CLAUDE-howto-thesis.md` | 📋 Тезисы: что должно/не должно быть в AGENTS.md |
| `03-opencode-config/AGENTS-md-examples-gist.md` | 📄 Примеры AGENTS.md от Boris Cherny (Self-Improvement Loop) |
| `03-opencode-config/opencode-project-guide-datatalks.md` | 📄 Большой гайд по настройке OpenCode-проекта |
| 📎 `docs/opencode-docs/30-agentsmd.md` | AGENTS.md — открытый формат инструкций |
| 📎 `docs/opencode-docs/31-agents-ecosystem-comparison.md` | Сравнение AGENTS.md / CLAUDE.md / GEMINI.md |
| 📎 `docs/opencode-docs/37-agentsmd-opencode.md` | AGENTS.md в OpenCode |
| 📎 `docs/opencode-docs/38-claudemd-best-practices.md` | Как писать эффективный CLAUDE.md / AGENTS.md |
| 📎 `docs/opencode-docs/39-cursor-rules.md` | Cursor Rules |
| 📎 `docs/opencode-docs/examples/AGENTS.md/` | 10 примеров AGENTS.md под разные сценарии |
| 📎 `docs/opencode-docs/01-how-openai-uses-codex.md` | Как OpenAI использует Codex (PDF how-openai-uses-codex-ru) |

---

## 📂 04. Best Practices

**↪️ [[04-best-practices/README|Все материалы категории →]]

| Файл | Описание |
|------|----------|
| `04-best-practices/2025-07-26_Hermes-agent.md` | 🎥 Hermes agent — как ставить задачи агенту |
| `04-best-practices/2025-07-26_Hermes-agent-thesis.md` | 📋 Принципы постановки задач: конкретность, контекст, критерии готовности |
| `04-best-practices/2025-07-26_AI-products-systematic-improvement.md` | 🎥 Системное улучшение AI-продуктов |
| `04-best-practices/2025-07-26_AI-products-systematic-improvement-thesis.md` | 📋 Eval-driven development, итеративный подход, human-in-the-loop |
| `04-best-practices/coding-agent-harness-architecture.md` | 📄 6 компонентов кодинг-агента: контекст, инструменты, память, субагенты |
| `04-best-practices/2026-02-12_Context-Engineering-thesis.md` | 📄 Context Engineering — data teams как команды контекста для AI-агентов |
| `04-best-practices/2025-LLM-testing-guide.md` | 🎥 Тестирование AI и LLM систем — полный гайд для QA Engineer |
| `04-best-practices/2025-LLM-testing-guide-thesis.md` | 📋 3 столпа качества, LLM-as-a-judge, RAG-тестирование |
| `04-best-practices/2025-vitaly-kharisov-ai-frontend.md` | 🎥 «Я 99.99% кода пишу нейронкой» — Виталий Харисов (Яндекс, БЭМ) |
| `04-best-practices/2025-vitaly-kharisov-ai-frontend-thesis.md` | 📋 Тезисы: X10 в OS vs X4 на работе, LLM как архитектурный партнёр |
| `04-best-practices/2025-polyakov-test-generation.md` | 🎥 Автогенерация тестов в IDE: RAG + LLM — Александр Поляков (Сбер) |
| `04-best-practices/2025-polyakov-test-generation-thesis.md` | 📋 RAG в IDE-плагине: BM25 → векторный поиск → генерация. 68% тестов без правок |
| `04-best-practices/2025-LLM-better-than-you.md` | 🎥 LLM пишет код лучше тебя. Ты просто не умеешь его настраивать |
| `04-best-practices/2025-LLM-better-than-you-thesis.md` | 📋 Qwen 3 27B, настройка агента, AGENTS.md, MCP |
| `04-best-practices/2025-AI-code-unsupportable.md` | 🎥 Почему ИИ-код становится неподдерживаемым |
| `04-best-practices/2025-AI-code-unsupportable-thesis.md` | 📋 Тактика vs Стратегия, 80% правило, архитектура с первого дня |
| 📎 `docs/opencode-docs/40-skillopt.md` | SkillOpt — автоматическая оптимизация AGENTS.md (Microsoft) |
| 📎 `docs/opencode-docs/41-modern-web-guidance.md` | Chrome Modern Web Guidance |
| 📎 `docs/opencode-docs/42-codex-maxxing-patterns.md` | Jason Liu Codex Maxxing паттерны |
| 📎 `docs/opencode-docs/43-agents-best-practices-skill.md` | agents-best-practices — agent skill от DenisSergeevitch |
| 📎 `docs/opencode-docs/44-creating-agent-skills-video.md` | 🎥 Создание Agent Skills (Lyp5LUFaZDA) |

---

## 📂 05. Архитектура

| Файл | Описание |
|------|----------|
| 📎 `docs/opencode-docs/microservices-patterns/46-design-microservices-architecture-with-patterns.md` | 11-step microservices evolution с паттернами и принципами |
| 📎 `docs/opencode-docs/obsidian/36-obsidian-hybrid-search-ohs.md` | Obsidian Hybrid Search — cross-session memory для AI-агентов |
| 📎 `docs/opencode-docs/test-generator-suite/48-test-generator-suite.md` | TGS — LLM-генератор API-тестов и тест-кейсов |

---

## 📂 06. Инструменты

**↪️ [[06-tools/README|Все материалы категории →]]

| Файл | Описание |
|------|----------|
| `06-tools/browse-sh.md` | browse.sh — Browser CLI и каталог веб-скиллов (npm install -g browse) |
| `06-tools/obsidian-guide.md` | Obsidian для AI-агентов: CLI, Headless Sync, AGENTS.md, интеграция |
| `06-tools/microsoft-skills.md` | microsoft/skills — 174 скилла для Azure AI агентов |
| `06-tools/tgs-test-generator-suite.md` | TGS — генератор API-тестов на LLM |
| 📎 `docs/skills/` | Azure SDK skills (Python, TypeScript, Java, .NET, Rust, Foundry и др.) |

---

## 📂 07. Статьи и референсы

**↪️ [[07-articles/README|Все материалы категории →]]

| Файл | Описание |
|------|----------|
| `07-articles/2025-06-07_AI-news-digest.md` | 🎥 AI-дайджест: Google, Anthropic Claude 4.8, Vertex AI |
| `07-articles/2025-06-07_AI-news-digest-thesis.md` | 📋 Тезисы новостей |
| 📎 `docs/opencode-docs/07-zen.md` | OpenCode Zen |
| 📎 `docs/opencode-docs/08-share.md` | OpenCode Share |

---

## 📂 08. Внешние референсы

**↪️ [[references/dot-ai/README|dot_ai →]]** | **↪️ [[references/hands-on-ai-engineering/README|Hands-On AI Engineering →]]**

| Раздел | Описание |
|--------|----------|
| `references/dot-ai/best_practice/` (9 файлов) | Best practices от davjdk/dot_ai — skills, rules, CLAUDE.md, sub-agents, hooks и др. |
| `references/dot-ai/researches/` (5 файлов) | Research notes — governance, eval-plan, transformer-limitations |
| `references/hands-on-ai-engineering/` | 30 AI-агентов + OCR, audio, RAG от Sumanth077 — production-ready примеры с кодом |

---

## 📂 09. Build Loop (наш проект)

| Файл | Описание |
|------|----------|
| 📎 `scripts/build-loop/setup.sh` | Установка инструментов и инициализация |
| 📎 `scripts/build-loop/init.sh` | Инициализация AGENTS.md и структуры |
| 📎 `scripts/build-loop/decompose.sh` | Декомпозиция spec на фазы |
| 📎 `scripts/build-loop/build-loop.sh` | Главный оркестратор |
| 📎 `scripts/build-loop/run-loop.sh` | Запуск фазы Build Loop |
| 📎 `scripts/build-loop/next-phase.sh` | Показать следующую фазу |
| 📎 `docs/opencode-docs/build-loop/49-build-loop-reference.md` | Build Loop reference |

---

## Ссылки на внешние ресурсы

| Ресурс | URL |
|--------|-----|
| OpenCode docs | https://opencode.ai/docs/ru/ |
| AGENTS.md | https://agents.md/ |
| Microsoft Skills | https://github.com/microsoft/skills |
| browse.sh | https://browse.sh/ |
| Cursor Rules | https://cursor.com/ru/docs/rules |
| Claude Code rules | https://code.claude.com/docs/ru/memory.html |
| OpenAI Codex | https://developers.openai.com/codex/ |
| datatalks OpenCode | https://datatalks.ru/opencode/index.html |
| SkillOpt | https://microsoft.github.io/SkillOpt/ |
| Chrome Modern Web | https://developer.chrome.com/docs/modern-web-guidance |
