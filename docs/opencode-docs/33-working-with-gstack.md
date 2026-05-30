# Работа с GStack — AI-инжиниринг в 10–15 параллельных спринтах

> **Источник:** https://github.com/garrytan/gstack  
> **Автор:** Garry Tan (President & CEO Y Combinator)  
> **Лицензия:** MIT

---

GStack — это открытый набор SKILL.md-файлов и инструментов, который превращает Claude Code (и другие AI-агенты) в виртуальную инженерную команду: CEO, tech lead, дизайнер, QA-инженер, security-офицер, release-инженер и ещё десятки специалистов. Всё — через слэш-команды, всё — бесплатно.

Ключевой результат: один разработчик с GStack может **запускать 10–15 параллельных спринтов** (каждый — отдельная Claude-сессия) и выдерживать темп **~810× быстрее, чем в 2013 году** (11 417 логических строк/день против 14).

---

## Установка — 30 секунд

**Требования:** Claude Code, Git, Bun v1.0+, Node.js

```bash
# Шаг 1: клонировать и запустить setup
git clone --single-branch --depth 1 https://github.com/garrytan/gstack.git ~/.claude/skills/gstack
cd ~/.claude/skills/gstack && ./setup
```

Установка создаёт симлинки на все SKILL.md в `~/.claude/skills/gstack-*` и добавляет секцию в CLAUDE.md.

### Team mode (рекомендуется для репозиториев команды)

```bash
(cd ~/.claude/skills/gstack && ./setup --team) && ~/.claude/skills/gstack/bin/gstack-team-init required
```

## Поддержка других AI-агентов

| Agent | Флаг |
|-------|------|
| OpenAI Codex CLI | `--host codex` |
| OpenCode | `--host opencode` |
| Cursor | `--host cursor` |
| Factory Droid | `--host factory` |
| Slate | `--host slate` |
| Kiro | `--host kiro` |
| Hermes | `--host hermes` |
| GBrain | `--host gbrain` |

## Архитектура

```
Claude Code                     gstack
─────────                      ──────
                               ┌──────────────────────┐
  Tool call: $B snapshot -i    │  CLI (compiled binary)│
  ─────────────────────────→   │  • reads state file   │
                               │  • POST /command      │
                               │    to localhost:PORT   │
                               └──────────┬───────────┘
                                           │ HTTP
                               ┌──────────▼───────────┐
                               │  Server (Bun.serve)   │
                               │  • dispatches command  │
                               │  • talks to Chromium   │
                               │  • returns plain text  │
                               └──────────┬───────────┘
                                           │ CDP
                               ┌──────────▼───────────┐
                               │  Chromium (headless)   │
                               │  • persistent tabs     │
                               │  • cookies carry over  │
                               │  • 30min idle timeout  │
                               └───────────────────────┘
```

**Ключевые принципы:**
- **Демон, не одноразовый браузер.** Chromium живёт как процесс: логин сохраняется, куки не теряются, команды выполняются за ~100–200 мс (первый запуск ~3 с)
- **Bun под капотом.** Компилированный бинарник (58 MB), нативная SQLite (чтение Chromium cookie DB), встроенный HTTP-сервер
- **Bearer token auth.** Каждая сессия генерирует UUID-токен, записанный в `~/.gstack/browse.json` с правами 0o600

## Структура GStack: спринт

GStack организован как процесс — **Think → Plan → Build → Review → Test → Ship → Reflect**:

```
                                ┌──────────────┐
                                │ /office-hours │  ← рефрейминг продукта
                                └──────┬───────┘
                                       ▼
                          ┌─────────────────────┐
                          │   /plan-ceo-review   │  ← CEO-ревью
                          │   /plan-eng-review   │  ← архитектура
                          │  /plan-design-review │  ← дизайн
                          └──────────┬──────────┘
                                     ▼
                            ┌─────────────────┐
                            │  Implementation │  ← код (вне GStack)
                            └────────┬────────┘
                                     ▼
                           ┌───────────────────┐
                           │    /review        │  ← code review
                           │   /design-review  │  ← визуальный аудит
                           │     /qa           │  ← E2E-тесты в браузере
                           │     /cso          │  ← security audit
                           └────────┬──────────┘
                                    ▼
                            ┌────────────────┐
                            │    /ship       │  ← PR + тесты + coverage
                            │ /land-and-deploy│  ← merge → deploy
                            └────────┬───────┘
                                     ▼
                            ┌────────────────┐
                            │    /retro      │  ← ретроспектива
                            │  /document-release│ ← docs-синхронизация
                            └────────────────┘
```

## Полный список навыков

### Plan-mode (до написания кода)

| Команда | Роль | Описание |
|---------|------|----------|
| `/office-hours` | YC Office Hours | 6 форсирующих вопросов, которые переформулируют продукт до написания кода |
| `/plan-ceo-review` | CEO/Founder | Найти 10-star продукт внутри запроса. 4 режима: Expansion, Selective, Hold Scope, Reduction |
| `/plan-eng-review` | Eng Manager | Закрепить архитектуру, data flow, диаграммы, edge cases, тесты |
| `/plan-design-review` | Senior Designer | Оценка каждого дизайн-измерения 0–10, AI Slop detection |
| `/plan-devex-review` | DX Lead | Developer Experience аудит: TTHW, personas, friction points |
| `/autoplan` | Review Pipeline | CEO → дизайн → eng → DX review в одной команде |
| `/design-consultation` | Design Partner | Построить дизайн-систему с нуля, исследовать ландшафт |
| `/spec` | Spec Author | Vague intent → исполняемый spec в 5 фаз с code-reading |

### Implementation + Review

| Команда | Роль | Описание |
|---------|------|----------|
| `/review` | Staff Engineer | Найти баги, которые проходят CI, но падают в проде. Auto-fix |
| `/codex` | Second Opinion | Независимый code review от OpenAI Codex CLI. 3 режима |
| `/investigate` | Debugger | Системный root-cause debugging. Iron Law: без расследования — никаких фиксов |
| `/design-review` | Designer Who Codes | Визуальный аудит + fix loop с атомарными коммитами |
| `/design-shotgun` | Design Explorer | 4–6 AI-вариантов макетов, comparison board, итерация по фидбеку |
| `/design-html` | Design Engineer | Mockup → production HTML/CSS (Pretext, 30 KB, zero deps) |
| `/devex-review` | DX Tester | Живой DX-аудит: замеряет TTHW, скриншотит ошибки |
| `/qa` | QA Lead | Реальный браузер → найти баги → исправить → регрессионные тесты |
| `/qa-only` | QA Reporter | Только отчёт о багах, без изменений кода |
| `/scrape` | Data Extractor | Извлечение данных с веб-страницы. Второй вызов — ~200 мс |
| `/skillify` | Skill Codifier | Закрепить успешный `/scrape` как permanent browser-skill |

### Release + Deploy

| Команда | Роль | Описание |
|---------|------|----------|
| `/ship` | Release Engineer | Тесты → review → push → PR. Workspace-aware version queue |
| `/land-and-deploy` | Release Engineer | Merge → CI → deploy → verify production health |
| `/canary` | SRE | Post-deploy monitoring: console errors, perf regressions |
| `/benchmark` | Performance Engineer | Core Web Vitals, page load, resource sizes. Before/after per PR |
| `/document-release` | Technical Writer | Обновить все доки под только что залитый код. Diataxis coverage map |
| `/document-generate` | Documentation Author | Сгенерировать недостающие доки с нуля (tutorial/how-to/reference/explanation) |
| `/setup-deploy` | Deploy Configurator | Одноразовое определение платформы деплоя (Fly.io, Vercel, Render) |
| `/landing-report` | Dashboard | Read-only dashboard для ship queue |
| `/gstack-upgrade` | Self-Updater | Обновление GStack до последней версии |

### Операционные + Память

| Команда | Роль | Описание |
|---------|------|----------|
| `/context-save` | Session Memory | Сохранить git state, решения, оставшуюся работу |
| `/context-restore` | Session Restore | Восстановить контекст, даже между Conductor workspaces |
| `/learn` | Memory | Управление тем, что GStack выучил между сессиями |
| `/retro` | Eng Manager | Еженедельная ретроспектива: per-person breakdowns, shipping streaks |
| `/health` | Code Health | Дашборд качества: type checker, linter, tests, dead code |
| `/cso` | Chief Security Officer | OWASP Top 10 + STRIDE threat model. Zero-noise: 17 false positive exclusions |
| `/setup-gbrain` | Memory Setup | Persistent knowledge base для агента между сессиями |
| `/sync-gbrain` | Brain Sync | Поддержание gbrain в актуальном состоянии |

### Браузер + Интеграция

| Команда | Роль | Описание |
|---------|------|----------|
| `/browse` | QA Engineer | Headless Chromium, реальные клики, ~100 мс/команда |
| `/open-gstack-browser` | Browser Launcher | Видимый GStack Browser с сайдбаром + anti-bot stealth |
| `/setup-browser-cookies` | Session Manager | Импорт cookies из Chrome/Arc/Brave/Edge |
| `/pair-agent` | Multi-Agent Coordinator | Подключить любого AI-агента к вашему браузеру |

### iOS QA (v1.43+)

| Команда | Описание |
|---------|----------|
| `/ios-qa` | Drive real iPhone over USB CoreDevice + embedded StateServer |
| `/ios-fix` | Автономный iOS-багфиксер с регрессионными снэпшотами |
| `/ios-design-review` | QA на реальном iPhone: 10-мерная Apple HIG rubric |
| `/ios-clean` | Stripping DebugBridge + `#if DEBUG` перед Release |
| `/ios-sync` | Регенерация debug bridge под новые шаблоны |

### Safety

| Команда | Описание |
|---------|----------|
| `/careful` | Предупреждать перед `rm -rf`, `DROP TABLE`, force-push |
| `/freeze` | Заблокировать редактирование только одной директории |
| `/guard` | `/careful` + `/freeze` |
| `/unfreeze` | Снять `/freeze` |

## Browser daemon — ключевая инновация

Постоянный браузерный демон — сердце GStack. В отличие от Playwright (3–5 с на холодный старт, потеря состояния между вызовами):

- **Sub-second latency** — после первого вызова ~100–200 мс
- **Persistent state** — логин один раз, куки живут, табы открыты
- **30-min idle timeout** — авто-выключение, не жрёт память
- **Port auto-selection** — случайный порт 10000–60000, до 10 параллельных workspace

### Ref system (@e1, @e2, @c1)

Рефы — способ адресации элементов без CSS-селекторов и XPath:

```
$B snapshot -i    → парсит accessibility tree, назначает @e1, @e2...
$B click @e3      → click по сохранённому Locator'у
$B snapshot -C    → ищет clickable элементы не из ARIA tree (@c1, @c2)
```

Playwright Locators вместо DOM-мутаций: работает через CSP, React hydration, Shadow DOM.

## Builder Ethos — философия GStack

GStack вшивает три принципа в каждый SKILL.md:

| Принцип | Суть |
|---------|------|
| **Boil the Lake** | Полнота стоит дёшево (секунды AI-времени). Делай полную версию всегда. 100% test coverage для модуля — норма |
| **Search Before Building** | Прежде чем строить — поищи. Три слоя знания: tried-and-true → new-and-popular → first principles |
| **User Sovereignty** | AI рекомендует — пользователь решает. Даже два AI согласны — это сигнал, не приказ |

## Типовой workflow

```
# 1. Прояснить идею
/office-hours
# → GStack задаёт 6 форсирующих вопросов, пишет design doc

# 2. CEO-ревью и архитектура
/autoplan
# → CEO → дизайн → eng-ревью, план готов

# 3. Код (любым AI-агентом)
# 4. Code review
/review
# → Auto-fix багов, вопросы по спорным моментам

# 5. QA в реальном браузере
/qa https://staging.myapp.com
# → Открывает Chromium, кликает, находит баги, фиксит

# 6. Ship
/ship
# → Тесты: 42 → 51 (+9 новых). PR: github.com/you/app/pull/42

# 7. Post-deploy
/canary
# → Мониторинг ошибок, перформанса
```

## Параллельные спринты

GStack спроектирован для параллельной работы. Используя [Conductor](https://conductor.build) или аналоги:

```
┌────── Session 1 ──────┐
│ /office-hours (new feature)│
└────────────────────────┘
┌────── Session 2 ──────┐
│ /review (PR #42)       │
└────────────────────────┘
┌────── Session 3 ──────┐
│ Implementation (feat)  │
└────────────────────────┘
┌────── Session 4 ──────┐
│ /qa (staging)          │
└────────────────────────┘
```

Каждая сессия — изолированный workspace. Процесс (Think → Plan → Build → Review → Test → Ship → Reflect) гарантирует предсказуемость.

## Multi-Agent

`/pair-agent` позволяет подключить несколько AI-агентов к одному браузеру:

1. Claude Code запускает `/pair-agent`
2. GStack Browser открывается с видимым окном
3. Paste блока инструкций в другого агента (OpenClaw, Hermes, Codex)
4. Каждый агент получает свою вкладку
5. Scoped tokens, tab isolation, rate limiting

`/codex` — cross-model second opinion: Claude + OpenAI Codex на одном diff.

## Prompt Injection Defense (Sidebar Agent)

Многоуровневая защита для sidebar agent'а, который читает веб-страницы (потенциально враждебные):

1. **L1–L3 Content Security** — datamarking, strip скрытых элементов, URL blocklist
2. **L4 ML Classifier (22 MB BERT-small ONNX)** — локально, без сети
3. **L4b Transcript Classifier (Claude Haiku)** — анализ формы диалога
4. **L5 Canary Token** — случайный токен в system prompt. Если утёк → BLOCK
5. **L6 Ensemble Combiner** — BLOCK требует согласия 2+ классификаторов

## Troubleshooting

| Проблема | Решение |
|----------|---------|
| Skill не появляется | `cd ~/.claude/skills/gstack && ./setup` |
| `/browse` не работает | `cd ~/.claude/skills/gstack && bun install && bun run build` |
| Stale install | `/gstack-upgrade` или `auto_upgrade: true` в `~/.gstack/config.yaml` |
| Хочешь `/qa` вместо `/gstack-qa`? | `./setup --no-prefix` |

---

## Ссылки

- [GitHub: garrytan/gstack](https://github.com/garrytan/gstack)
- [ETHOS.md — Builder Philosophy](https://github.com/garrytan/gstack/blob/main/ETHOS.md)
- [ARCHITECTURE.md — System Design](https://github.com/garrytan/gstack/blob/main/ARCHITECTURE.md)
- [AGENTS.md — Полный список skills](https://github.com/garrytan/gstack/blob/main/AGENTS.md)
- [BROWSER.md — Browse Command Reference](https://github.com/garrytan/gstack/blob/main/BROWSER.md)
- [GBrain — Persistent Knowledge for AI Agents](https://github.com/garrytan/gstack)
