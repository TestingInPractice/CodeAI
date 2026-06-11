# Build Loop — полная схема работы

## Что это

Build Loop — конвейер для пошаговой разработки проекта через AI-агентов.
Проект делится на фазы (phases), каждая фаза выполняется отдельным sub-agent'ом,
результат проверяется судьёй (judge), и только после этого коммитится.

---

## 1. Структура проекта после `init.sh`

```
my-project/
├── AGENTS.md                         # инструкция для оркестратора
├── docs/specs/
│   ├── goals.md                      # цели проекта
│   ├── acceptance-criteria.md        # критерии приёмки (AC-001, AC-002...)
│   └── contracts/
│       ├── api.md                    # API-контракты
│       └── data-models.md            # модели данных
├── scripts/judge/
│   └── llm-judge.py                  # судья (копируется из CodeAI)
└── .build-loop/
    ├── phases.json                   # состояние фаз (читает/пишет оркестратор)
    └── .gitignore                    # .build-loop/ в gitignore
```

---

## 2. Файлы CodeAI, образующие пайплайн

| Файл | Роль | Вызывается |
|------|------|-----------|
| `scripts/build-loop/init.sh` | Создаёт скелет проекта, AGENTS.md, копирует судью | 1 раз |
| `scripts/build-loop/setup.sh` | Устанавливает GStack, GSD, Superpowers | 1 раз |
| `scripts/build-loop/decompose.sh` | Генерирует phases.json из docs/specs/ | После init |
| `scripts/build-loop/next-phase.sh` | Показывает следующую готовую фазу | Каждый цикл |
| `scripts/build-loop/run-loop.sh` | 4 режима: status, prompt, judge, complete | Каждый цикл |
| `scripts/build-loop/build-loop.sh` | Агрегатор: setup → init → decompose → run | Опционально |
| `scripts/llm-judge.py` | Судья: 4 pillars (Relevance, Faithfulness, Context Precision, AC) | После sub-agent |
| `scripts/judge-check.sh` | Graph quality judge (отдельный, не в пайплайне) | Опционально |

---

## 3. Два режима работы

### Режим A: Ralph Loop (1 терминал, task() sub-agents)

**Для:** простых проектов, одного терминала opencode.

Оркестратор сам делегирует фазы через `task()` и сам запускает судью.

```
┌─────────────────────────────────────────────────────────┐
│  Терминал 1 (opencode)                                  │
│                                                         │
│  Оркестратор                          Sub-agent (task)  │
│  ┌──────────────┐    task() с prompt    ┌────────────┐  │
│  │ читает spec  │──────────────────────→│ свежая      │  │
│  │ next-phase   │                       │ сессия      │  │
│  │ print-prompt │                       │ читает spec │  │
│  │              │←──────────────────────│ пишет код   │  │
│  │ запускает    │   summary.txt          │ сохраняет   │  │
│  │ judge        │                       │ summary.txt │  │
│  │              │                       └────────────┘  │
│  │ PASS? → git commit + mark-complete                   │
│  │ FAIL? → task() снова с фидбеком                      │
│  └──────────────┘                                       │
└─────────────────────────────────────────────────────────┘
```

**Пошагово:**

1. Оркестратор читает `docs/specs/`
2. `bash scripts/build-loop/decompose.sh --project .` — создаёт phases.json
3. Для каждой pending фазы:
   a. `bash scripts/build-loop/next-phase.sh --project .` — узнать ID фазы
   b. `bash scripts/build-loop/run-loop.sh --project . --phase <id> --print-prompt`
   c. `task()` — делегировать свежему sub-agent'у (без task_id)
      - Sub-agent читает spec
      - Пишет код фазы
      - Сохраняет summary в `/tmp/p<id>-summary.txt`
      - Возвращает управление
   d. `bash scripts/build-loop/run-loop.sh --project . --judge --phase <id> --summary /tmp/p<id>-summary.txt`
   e. **FAIL** → вернуться к шагу c с фидбеком от судьи
   f. **PASS** → `git add -A && git commit -m "p<id>: ..." && git push && run-loop.sh --mark-complete <id>`
4. Повторять, пока все фазы не будут completed

### Режим B: 2-Terminal Workflow (T1 оркестратор + T2 исполнитель+судья)

**Для:** сложных проектов, где нужен человеческий контроль на каждом шаге.
Использует `.workflow/state.json` + `.workflow/subagent-handoff.json`.

```
┌──────────────────────────┐     ┌──────────────────────────────┐
│  Терминал 1 (оркестратор) │     │  Терминал 2 (исполнитель)    │
│                           │     │                              │
│  ┌─────────────┐          │     │  ┌──────────────┐           │
│  │ reads state │  открой  │     │  │ читает       │           │
│  │ пишет       │─────────│────→│  │ subagent-    │           │
│  │ subagent-   │  T2,     │     │  │ handoff.json │           │
│  │ handoff     │  скажи   │     │  │              │           │
│  │             │  "{фаз}" │     │  │ выполняет    │           │
│  │ ждёт "done" │←────────│─────│  │ фазу         │           │
│  │ читает      │  готово  │     │  │              │           │
│  │ handoff     │          │     │  │ запускает    │           │
│  │ проверяет   │          │     │  │ evaluate_    │           │
│  │ verdict     │          │     │  │ judge.py     │           │
│  │             │          │     │  │              │           │
│  │ PASS →      │          │     │  │ пишет        │           │
│  │ transition  │          │     │  │ verdict в    │           │
│  │ FAIL →      │          │     │  │ handoff      │           │
│  │ "открой T2" │          │     │  └──────────────┘           │
│  └─────────────┘          │     └──────────────────────────────┘
└──────────────────────────┘
```

**T1 умеет только:** читать state.json, писать handoff, запускать transition.py.
**T2 делает всё:** реализацию + тесты + судью.

**Пошагово:**

**T1 (оркестратор):**
1. Прочитать `.workflow/state.json` — узнать текущую фазу
2. Записать `.workflow/subagent-handoff.json`:
   ```json
   {"phase": "plan-release", "skill_ref": "skills/plan-release/SKILL.md", "user_prompt": "plan-release"}
   ```
3. Сказать пользователю: "Открой T2, скажи `plan-release`"
4. Когда вернулись — прочитать handoff
5. Если `judge_verdict == "passed"`:
   - `python3 scripts/transition.py --project . --action transition`
   - Повторить с шага 1
6. Если failed — объяснить, пользователь открывает T2 снова

**T2 (исполнитель + судья):**
1. Прочитать `.workflow/subagent-handoff.json`
2. Следовать `{skill_ref}` — выполнить фазу
3. Запустить судью:
   ```
   python3 scripts/evaluate_judge.py prepare --project . --rubric judge-rubrics/{phase}.json
   ```
4. Если FAILED → исправлять, пока не PASSED
5. Записать результат в handoff
6. Закрыть терминал

### Режим C: Full Pipeline (spec → human gate → per-task analyst→dev→tester)

**Для:** production-проектов, где нужен полный цикл: spec → ревью человека → аналитик → судья → разработчик → судья → тестировщик → судья.

Старт: пользователь говорит "сделай проект X, используй наш workflow https://github.com/TestingInPractice/CodeAI"

```
┌──────────────────────────────────────────────────────────────────┐
│ РЕЖИМ C: FULL AUTO PIPELINE                                      │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│ [Человек] создаёт репо, открывает opencode, пишет промт          │
│     ↓                                                            │
│ 0. SETUP                                                         │
│    start-project.sh: clone CodeAI → setup.sh → init.sh           │
│    → .workflow/state.json                                        │
│     ↓                                                            │
│ 1. SPEC                                                          │
│    AI (или GStack /spec) → docs/specs/goals.md                   │
│    по шаблону requirements.md (F-XXX, AC, архитектура, контракты) │
│     ↓                                                            │
│    [СУДЬЯ] evaluate_judge.py — structural + IEEE 29148           │
│    PASS → human_gate                                             │
│     ↓                                                            │
│ 2. HUMAN GATE                                                    │
│    status: waiting_human → человек читает spec                   │
│    правит, утверждает → transition                               │
│     ↓                                                            │
│ 3. DECOMPOSE                                                     │
│    decompose.sh → phases.json                                    │
│    [СУДЬЯ] evaluate_judge.py — coverage                          │
│     ↓ PASS                                                       │
│ 4. PER-TASK CYCLE (для p1..pN)                                   │
│    ┌─────────────────────────────────────────────────────┐       │
│    │ task() АНАЛИТИК → ADR, data models, contracts       │       │
│    │ [СУДЬЯ] llm-judge.py                                │       │
│    │ FAIL → re-delegate аналитик                         │       │
│    │ ↓ PASS                                               │       │
│    │ task() РАЗРАБОТЧИК → код фазы                       │       │
│    │ [СУДЬЯ] llm-judge.py                                │       │
│    │ FAIL → re-delegate разработчик                      │       │
│    │ ↓ PASS                                               │       │
│    │ task() ТЕСТИРОВЩИК → unit/integration тесты          │       │
│    │ [СУДЬЯ] llm-judge.py                                │       │
│    │ FAIL → re-delegate тестировщик                      │       │
│    │ ↓ PASS                                               │       │
│    │ git commit + mark-complete → next task              │       │
│    └─────────────────────────────────────────────────────┘       │
│     ↓                                                            │
│ 5. COMPLETE → отчёт                                             │
└──────────────────────────────────────────────────────────────────┘
```

**Ключевые отличия от A и B:**

| Аспект | Режим C |
|--------|---------|
| Фаз | 6 фаз верхнего уровня (setup→spec→human→decompose→task_cycle→complete) |
| Per-task | analyst → **judge** → developer → **judge** → tester → **judge** |
| Human gate | waiting_human после spec, до decompose |
| Состояние | `.workflow/state.json` (transition.py) |
| Spec | Полный шаблон requirements.md (F-XXX, AC, архитектура, контракты, UI, non-functional) |
| Судья | Один `llm-judge.py` для всех ролей (4 pillars: AC → Relevance → Faithfulness → Context Precision) |

**Команды:**

```bash
# Старт проекта
bash scripts/start-project.sh \
  --project . \
  --prompt "Сделай todo-приложение" \
  --workflow-repo "https://github.com/TestingInPractice/CodeAI"

# Управление состоянием
python3 scripts/transition.py --project . status
python3 scripts/transition.py --project . start --phase spec
python3 scripts/transition.py --project . human-gate --questions '["Вопрос?"]'
python3 scripts/transition.py --project . approve
python3 scripts/transition.py --project . transition

# Per-task шаги
bash scripts/workflow/run-task.sh --project . --phase p1 --step analyst --print-prompt
bash scripts/workflow/run-task.sh --project . --phase p1 --step analyst --judge --summary /tmp/p1-analyst.txt
bash scripts/workflow/run-task.sh --project . --phase p1 --step dev --print-prompt
bash scripts/workflow/run-task.sh --project . --phase p1 --step dev --judge --summary /tmp/p1-dev.txt
bash scripts/workflow/run-task.sh --project . --phase p1 --step tester --print-prompt
bash scripts/workflow/run-task.sh --project . --phase p1 --step tester --judge --summary /tmp/p1-tester.txt
bash scripts/workflow/run-task.sh --project . --phase p1 --complete
```

---

## 4. Судья (Judge)

### 4a. llm-judge.py — 4 pillars (Ralph Loop)

Вызывается из `run-loop.sh --judge`.

```
python3 scripts/judge/llm-judge.py \
  --question "Phase p3: Chat Interface" \
  --response "$(cat /tmp/p3-summary.txt)" \
  --context "$(cat docs/specs/goals.md)" \
  --phase-id "p3" \
  --phases-path ".build-loop/phases.json"
```

**4 pillars (в порядке важности):**

| Pillar | Что проверяет | Вес |
|--------|--------------|-----|
| AC Check | Acceptance criteria покрыты? ключевые термины из AC в ответе | 25% |
| Relevance | Ответ отвечает на вопрос? overlap слов ≥20% | 25% |
| Faithfulness | Ответ основан на контексте? hallucination ratio ≤50% | 25% |
| Context Precision | Контекст качественный? структура, длина 10-2000 слов | 25% |

**Score:** среднее арифметическое 4 pillars. PASS ≥ 0.5.

### 4b. evaluate_judge.py — гибридный (2-Terminal Workflow)

Два шага:

**Шаг 1. Structural check (скрипт):**
```
python3 scripts/evaluate_judge.py prepare \
  --rubric judge-rubrics/analyst.json \
  --spec docs/specs/requirements.md \
  --tasks-dir .workflow/tasks/
```
Проверяет:
- F-XXX coverage: каждое требование → задача
- AC completeness: у каждой задачи есть acceptance criteria
- Task completeness (developer): все задачи выполнены

Если structural errors > 0 → FAIL, AI judge не запускается.

**Шаг 2. AI judge (генерация prompt для subagent-судьи):**
Если structural check PASSED → генерируется AI prompt с:
- Rubric критерии (из JSON, с весами)
- IEEE 29148 критерии: Necessary, Implementation-free, Unambiguous, Complete, Atomic, Verifiable, Traceable

**Verdict:** PASS / FAIL / PASS_WITH_CONCERNS

### 4c. Когда какой судья

| Режим | Судья | Почему |
|-------|-------|--------|
| A (Ralph) / C (Full) | `llm-judge.py` | 4 pillars: AC → Relevance → Faithfulness → Context Precision |
| B (2-Terminal) | `evaluate_judge.py` | Structural + AI prompt с IEEE 29148; для режима где T2 сам проверяет файлы |

---

## 5. Жизненный цикл фазы

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ PENDING  │───→│ IN FLIGHT│───→│ VERIFIED │───→│ COMPLETED│
│          │    │ (task()) │    │ (judge)  │    │ (git)    │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
                      │               │
                      │               │ FAIL
                      │               ↓
                      │         ┌──────────┐
                      └────────→│ REWORK   │
                                │ (task()  │
                                │  again)  │
                                └──────────┘
```

**Состояния в phases.json:**
- `pending` — фаза ожидает выполнения
- `in_progress` — выполняется (опционально)
- `completed` — выполнена, проверена судьёй, закоммичена

---

## 6. Data Flow

### phases.json (состояние фаз)
```json
{
  "phases": [
    {
      "id": "p1",
      "name": "Project Setup",
      "description": "Init project structure",
      "status": "completed",
      "depends_on": [],
      "acceptance_criteria": [
        "AC-001: Project scaffold created",
        "AC-002: Build tools configured"
      ]
    },
    {
      "id": "p2",
      "name": "Core Feature",
      "description": "Implement main logic",
      "status": "pending",
      "depends_on": ["p1"],
      "acceptance_criteria": [
        "AC-003: Feature X works"
      ]
    }
  ]
}
```

### subagent-handoff.json (только 2-Terminal режим)
```json
{
  "phase": "plan-release",
  "status": "DONE",
  "summary": "Созданы goals.md, architecture.md",
  "evidence": ["docs/specs/goals.md"],
  "judge_verdict": "passed",
  "judge_score": 85,
  "open_questions": []
}
```

### /tmp/p{id}-summary.txt (Ralph Loop, пишет sub-agent)
```
Created: src/index.html, src/app.js, src/styles.css
Modified: docs/api.md
Acceptance criteria met: AC-001, AC-002, AC-003
Phase complete.
```

---

## 7. Команды быстрого доступа

```bash
# Полный цикл (1 раз)
bash scripts/build-loop/build-loop.sh --project /path/to/project --setup-only
bash scripts/build-loop/build-loop.sh --project /path/to/project --decompose-only

# Статус фаз
bash scripts/build-loop/run-loop.sh --project .

# Следующая фаза
bash scripts/build-loop/next-phase.sh --project .

# Prompt для sub-agent
bash scripts/build-loop/run-loop.sh --project . --phase p1 --print-prompt

# Запустить судью (после выполнения фазы sub-agent'ом)
bash scripts/build-loop/run-loop.sh --project . --judge --phase p1 --summary /tmp/p1-summary.txt

# Или через build-loop.sh
bash scripts/build-loop/build-loop.sh --project . --judge

# Отметить фазу completed (после прохождения судьи)
bash scripts/build-loop/run-loop.sh --project . --mark-complete p1
```

---

## 8. Выбор режима

| Фактор | A: Ralph Loop | B: 2-Terminal | C: Full Pipeline |
|--------|--------------|---------------|------------------|
| Терминалов | 1 | 2 | 1 |
| Человеческий контроль | минимальный | на каждом шаге | human gate на spec |
| Сложность проекта | низкая-средняя | средняя-высокая | любая |
| Судья | llm-judge.py | evaluate_judge.py | llm-judge.py (на всех этапах) |
| Per-task шаги | dev только | всё в T2 | analyst → dev → tester |
| Состояние | phases.json | state.json + handoff.json | .workflow/state.json |
| Sub-agent запуск | task() без task_id | ручное открытие T2 | task() без task_id |
| Когда выбрать | быстрый прототип | milestones, команда | production, полный цикл |
