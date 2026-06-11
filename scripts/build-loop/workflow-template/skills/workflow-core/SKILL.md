---
name: workflow-core
description: >
  Master orchestrator skill for CodeAI Build Loop.
  Runs in Terminal 1. Only reads state, tells user what to do,
  applies transitions. All work + judge happens in Terminal 2.
  Triggers: "next phase", "run workflow", "check workflow",
  "start project", "begin phase", "continue workflow".
type: workflow
step: 0
---

# CodeAI Workflow Core — Orchestrator (T1)

## Модель

```
T1 (оркестратор)            T2 (исполнитель + судья)
┌──────────────┐           ┌──────────────────────┐
│ читает state │──открой──→│ выполняет фазу       │
│ пишет transition│       │ запускает судью       │
│ только это   │←─готово──│ пишет verdict         │
└──────────────┘           └──────────────────────┘
```

**T1 умеет только:**
- Прочитать `state.json`
- Сказать пользователю "открой T2, скажи {фазу}"
- Прочитать `subagent-handoff.json` (результат + verdict)
- `transition.py --project . --action transition` на следующую фазу

**T2 делает всё:** реализацию, тесты, merge, changelog, deploy, И судью.

---

## Алгоритм

### Bootstrap (первый запуск)

Если `state.phase == "plan-release"` и `state.status == "pending"`:

1. Проверь `docs/specs/requirements.md` — если нет, скажи пользователю написать
2. `transition.py --project . --to plan-release --action start`
3. Запиши `.workflow/subagent-handoff.json`:

   ```json
   {
     "phase": "plan-release",
     "skill_ref": "skills/plan-release/SKILL.md",
     "user_prompt": "plan-release"
   }
   ```

4. Скажи пользователю:

   ```
   Открой второй терминал в этом проекте, запусти opencode и скажи:
   "plan-release"

   После завершения вернись сюда и скажи "готово".
   ```

5. Жди ответа пользователя
6. Прочитай `.workflow/subagent-handoff.json`
7. Если `judge_verdict == "passed"`:
   - Извлеки `spec_version` и `release_branch` из handoff
   - Запиши их в `state.json` (через `transition.py` неудобно — можно прямым чтением/записью state, но только version и release_branch)
   - `transition.py --project . --to implement-spec-stage --action transition`
   - Вернись к шагу 3 для следующей фазы, передав `spec_version` и `release_branch` в handoff
8. Если `judge_verdict == "failed"` или `open_questions` есть → объясни пользователю, он открывает T2 снова

### Основной цикл

```
1. Прочитай state.json
2. Если status == "completed" → переходи к следующей фазе
3. Если status == "pending" или "in_progress":
   a. transition.py --action start (если pending)
   b. Запиши subagent-handoff.json
   c. Скажи пользователю: "Открой T2, скажи '{phase}'"
   d. Жди "готово"
   e. Прочитай subagent-handoff.json
   f. Если verdict == "passed" → transition.py --action transition
   g. Если иначе → объясни, жди повторного открытия T2
4. Повтори
```

### Переполнение контекста в T1

Если контекст >70%:

1. Запиши `.workflow/context-handoff.json`:

   ```json
   {
     "phase": "implement-spec-stage",
     "status": "in_progress",
     "pending": ["реализовать F-002"]
   }
   ```

2. Скажи:

   ```
   Контекст >70%. Открой новый терминал 1 в этом проекте,
   запусти opencode и скажи "continue workflow".
   Состояние сохранено. Этот терминал можно закрыть.
   ```

3. Заверши сессию

В новой сессии: прочитай state.json + context-handoff.json → удали handoff → продолжай.

---

## Правила

1. T1 **никогда** не запускает subagent внутри своей сессии
2. T1 **никогда** не запускает судью
3. T1 пишет state.json только через `scripts/transition.py`
4. T1 пишет subagent-handoff.json только перед отправкой в T2
5. T1 читает subagent-handoff.json только после возврата пользователя
6. Все остальное — в T2

## Ссылки

- Subagent protocol: references/subagent-protocol.md
- Transition rules: `.workflow/config.yaml`
- State schema: schemas/state.schema.json
- Phase skills: skills/{phase-name}/SKILL.md (выполняются в T2)
