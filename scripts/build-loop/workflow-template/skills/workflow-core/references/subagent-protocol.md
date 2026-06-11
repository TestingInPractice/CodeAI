# Subagent Protocol

Subagent запускается в **терминале 2**. Одна сессия = одна фаза + судья.
Получает задание через `.workflow/subagent-handoff.json`, пишет результат туда же.

## Запуск

1. Оркестратор (T1) пишет `.workflow/subagent-handoff.json`:

   ```json
   {
     "phase": "plan-release",
     "skill_ref": "skills/plan-release/SKILL.md",
     "user_prompt": "plan-release"
   }
   ```

2. T1 говорит пользователю:
   ```
   Открой второй терминал в этом проекте, запусти opencode и скажи "{phase}"
   ```

3. В T2 агент читает:
   - `AGENTS.md` — bootstrap
   - `.workflow/subagent-handoff.json` — что делать
   - `skills/{phase}/SKILL.md` — инструкция фазы

4. Выполняет работу (создание файлов, код, тесты, merge, changelog, deploy — по фазе)

5. **Запускает судью:**

   ```bash
   python3 scripts/evaluate_judge.py prepare \
     --project . \
     --rubric judge-rubrics/{phase}.json
   ```

   Если судья FAILED → дорабатывает, пока не PASSED.
   (Кроме случая, когда нужна информация от пользователя — тогда `NEEDS_CONTEXT`.)

6. Пишет результат в `.workflow/subagent-handoff.json`

## Формат результата

```json
{
  "phase": "plan-release",
  "status": "DONE",
  "summary": "Созданы goals.md, architecture.md, 5 задач",
  "evidence": [
    "docs/specs/goals.md",
    "docs/specs/architecture.md"
  ],
  "judge_verdict": "passed",
  "judge_score": 85,
  "open_questions": [],
  "created_tasks": ["task-001", "task-002"],
  "created_issues": []
}
```

### Status meanings

| Status | Meaning |
|--------|---------|
| `DONE` | Задача выполнена, judge PASSED |
| `DONE_WITH_CONCERNS` | Выполнено, judge PASSED, но есть concerns |
| `BLOCKED` | Внешняя зависимость не выполнена |
| `NEEDS_CONTEXT` | Не хватает информации — open question |

## Open questions

Если нужна информация от пользователя:

1. Запиши в результат `"status": "NEEDS_CONTEXT"`, заполни `open_questions[]`
2. T1 прочитает, создаст вопросы, поставит `waiting_human`
3. После ответа пользователя T1 обновляет handoff и говорит "открой T2 снова"

## Security

- T2 **никогда** не пишет в `state.json` и `phases.json`
- T2 пишет только в `.workflow/subagent-handoff.json` и рабочие файлы проекта
- Все изменения состояния — через `scripts/transition.py` в T1
