---
name: workflow-core
description: >
  Master orchestrator skill for CodeAI Build Loop.
  Runs in Terminal 1. Manages state, transitions, judges.
  Deploys subagents to Terminal 2 for clean context per task.
  Triggers: "next phase", "run workflow", "validate state", "check workflow",
  "start project", "begin phase", "transition phase", "continue workflow".
type: workflow
step: 0
---

# CodeAI Workflow Core — Orchestrator

## Модель двух терминалов

```
Терминал 1 (оркестратор)        Терминал 2 (субагент)
┌──────────────────────┐       ┌──────────────────────┐
│ state.json           │       │ subagent-handoff.json│
│ фазы                 │◄─────►│ (запрос → результат) │
│ переходы             │       │                      │
│ судьи                │       │ свежий контекст      │
│ open questions       │       │ одна задача          │
└──────────────────────┘       └──────────────────────┘
```

- **Терминал 1** — only orchestrator. Читает/пишет state.json, запускает судей,
  задаёт вопросы пользователю, переключает фазы.
- **Терминал 2** — only subagent. Оркестратор говорит "открой терминал 2,
  запусти opencode, скажи '<skill>'". Субагент выполняет одну задачу,
  пишет результат в `.workflow/subagent-handoff.json`, завершается.
- Пользователь возвращается в терминал 1, оркестратор читает результат.
- **После завершения субагента — контекст в терминале 2 очищен.**

## Workflow Contract

entry:
  artifacts:
    - .workflow/state.json
    - .workflow/phases.json
  condition: state.json валиден по state.schema.json

exit:
  condition: state.json обновлён с новым phase/status
  artifacts:
    - .workflow/state.json (updated)

next_skill: null (выбирает по state.json)

---

## Фазы workflow и их исполнение

| Фаза | Терминал | Делает |
|------|----------|--------|
| `plan-release` | 2 | Аналитик: читает requirements.md, создаёт задачи, файлы, issues |
| `implement-spec-stage` | 2 | Разработчик: берёт задачу, реализует, unit-тесты |
| `write-tests` | 2 | Тестировщик: пишет интеграционные/e2e/регрессионные тесты |
| `integrate-release` | 1 | Оркестратор: merge, changelog, tag, закрытие issues |
| `deploy-release` | 2 | DevOps: health check, smoke, отчёт |

**`integrate-release`** выполняется оркестратором в терминале 1
(не требует тяжёлого контекста — только changelog + merge).

**Shortcut:** `apply-small-fix` → выполняется прямо в терминале 1
(тривиальный фикс), затем `integrate-release` → `deploy-release`.

---

## Алгоритм

### Bootstrap (первый запуск)

Если `state.phase == "plan-release"` и `state.status == "pending"`:

1. Проверь `docs/specs/requirements.md` — если нет, скажи пользователю написать
2. `transition.py --project . --to plan-release --action transition`
3. Скажи пользователю:

   ```
   Открой второй терминал в этом проекте, запусти opencode и скажи:
   "plan-release"

   После завершения вернись сюда и скажи "готово".
   ```

4. Жди, пока пользователь не вернётся и не скажет "готово"
5. Прочитай `.workflow/subagent-handoff.json` — проверь STATUS
6. Запусти судью (`scripts/evaluate_judge.py prepare --rubric judge-rubrics/analyst.json`)
7. Если judge PASSED → `transition.py --project . --to implement-spec-stage --action transition`
8. Если есть open questions → создай issue, объясни пользователю

### Основной цикл

Для каждой фазы (`plan-release`, `implement-spec-stage`, `write-tests`, `deploy-release`)
кроме `integrate-release`:

1. Прочитай `state.json`
2. Проверь entry conditions
3. `transition.py --project . --action transition` (ставит `in_progress`)
4. Запиши `.workflow/subagent-handoff.json`:

   ```json
   {
     "phase": "implement-spec-stage",
     "task_uuid": "impl-001",
     "skill_ref": "skills/implement-spec-stage/SKILL.md",
     "user_prompt": "выполни задачу impl-001 по инструкции skills/implement-spec-stage/SKILL.md"
   }
   ```

5. Скажи пользователю:

   ```
   Открой второй терминал в этом проекте, запусти opencode и скажи:
   "<фаза> / <task_uuid>"

   После завершения вернись сюда и скажи "готово".
   ```

6. Жди ответа пользователя
7. Прочитай `.workflow/subagent-handoff.json` — проверь STATUS
8. Если NEEDS_CONTEXT → open questions → waiting_human
9. Если DONE → запусти судью
10. Если judge PASSED → `transition.py --project . --action transition` на следующую фазу
11. Если judge FAILED → верни на доработку (снова отправь в терминал 2)

### Фаза integrate-release

Выполняется прямо в терминале 1 (оркестратор делает merge + changelog):

1. `transition.py --project . --action transition`
2. Определи версию (автоинкремент от последнего git tag)
3. `git checkout main && git merge --no-ff feat/{uuid}`
4. Обнови `CHANGELOG.md`
5. Закрой GitHub Issues
6. `git tag -a v{X.Y.Z}` && `git push --tags`
7. `transition.py --project . --action complete`

### Переключение терминала оркестратора

Если контекст в терминале 1 >70%:

1. Сохрани состояние в `state.json`
2. Запиши `.workflow/context-handoff.json`:

   ```json
   {
     "phase": "implement-spec-stage",
     "status": "in_progress",
     "completed": ["plan-release"],
     "pending": ["реализовать F-002"],
     "notes": "F-001 реализован, судья прошёл"
   }
   ```

3. Скажи пользователю:

   ```
   Контекст >70%. Открой новый терминал в этом проекте,
   запусти opencode и скажи "continue workflow".
   Я сохранил состояние в context-handoff.json.
   Этот терминал можно закрыть.
   ```
4. Заверши текущую сессию

**В новой сессии:**
1. Прочитай `.workflow/state.json`
2. Прочитай `.workflow/context-handoff.json` (восстанови контекст)
3. Удали `.workflow/context-handoff.json`
4. Продолжи с текущей фазы

---

## Правила и ограничения

1. **Только оркестратор пишет в state.json** — через `scripts/transition.py`
2. **Субагент пишет только в `subagent-handoff.json`** — STATUS, EVIDENCE
3. **Оркестратор никогда не запускает subagent внутри своей сессии**
4. **Субагент работает одну задачу и завершается** — контекст чистый
5. **Emergency override**: `--action override` bypass gates
6. **Open questions**: оркестратор задаёт пользователю в терминале 1
7. **Приоритет инструкций**: opencode.json > AGENTS.md > SKILL.md > config.yaml

## Ссылки

- Subagent protocol: references/subagent-protocol.md
- Judge rubric: references/judge-rubric.md
- Transition rules: `.workflow/config.yaml`
- State schema: schemas/state.schema.json
- Phase skills: skills/{phase-name}/SKILL.md
