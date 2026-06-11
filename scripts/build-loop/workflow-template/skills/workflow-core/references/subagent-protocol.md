# Subagent Protocol

Subagent запускается в **терминале 2** — отдельная opencode-сессия с чистым контекстом.
Получает задание через `.workflow/subagent-handoff.json`, пишет результат туда же.

## Запуск

1. Оркестратор пишет `.workflow/subagent-handoff.json`:
   ```json
   {
     "phase": "plan-release",
     "skill_ref": "skills/plan-release/SKILL.md",
     "user_prompt": "plan-release",
     "task_uuid": null
   }
   ```

2. Оркестратор говорит пользователю:
   ```
   Открой второй терминал в этом проекте, запусти opencode и скажи
   "plan-release"
   ```

3. Пользователь открывает терминал 2, запускает opencode, говорит фразу

4. В терминале 2 агент читает:
   - `AGENTS.md` — bootstrap инструкция
   - `.workflow/subagent-handoff.json` — что делать
   - `skills/{phase}/SKILL.md` — инструкция фазы
   - Файлы проекта по необходимости

5. После работы агент пишет в `.workflow/subagent-handoff.json`:

## Output format

Запись в `.workflow/subagent-handoff.json`:

```json
{
  "phase": "plan-release",
  "skill_ref": "skills/plan-release/SKILL.md",
  "user_prompt": "plan-release",
  "task_uuid": null,
  "status": "DONE",
  "summary": "Созданы goals.md, architecture.md, 5 задач",
  "evidence": [
    "docs/specs/goals.md",
    "docs/specs/architecture.md"
  ],
  "open_questions": [],
  "created_tasks": ["task-001", "task-002"],
  "created_issues": []
}
```

### Status meanings

| Status | Meaning |
|--------|---------|
| `DONE` | Задача выполнена, все AC пройдены |
| `DONE_WITH_CONCERNS` | Выполнено, но есть open concerns |
| `BLOCKED` | Внешняя зависимость не выполнена |
| `NEEDS_CONTEXT` | Не хватает информации |

## Open questions loop

Когда subagent возвращает `NEEDS_CONTEXT` или judge FAIL с open questions:

1. Оркестратор создаёт `state.{section}.open_questions[]: {"id": "oq-{uuid}", "question": "...", "answer": null, "resolved": false}`
2. Ставит `state.status = "waiting_human"` через `transition.py --action wait`
3. Пользователь отвечает в терминале 1
4. Оркестратор пишет ответ в `state.{section}.open_questions[i]`, ставит `resolved: true`
5. Обновляет `docs/specs/requirements.md` — секция 12
6. `transition.py --action resume`
7. Повторяет отправку в терминал 2

## Context management

### Чтение по фазам

| Фаза | Читает | Context budget |
|------|--------|----------------|
| `plan-release` | requirements.md (весь), contracts/ | ≤5K |
| `implement-spec-stage` | 1 task.md + contracts/ для F-XXX | ≤4K |
| `write-tests` | contracts/ + spec секции 5, 9 | ≤6K |
| `integrate-release` | CHANGELOG.md + git log | ≤3K |
| `deploy-release` | state.deploy_release + CHANGELOG.md | ≤2K |

### Контекстный сброс между задачами

- Каждая задача в `implement-spec-stage` — **отдельный запуск терминала 2**
- Каждый батч в `write-tests` — отдельный запуск
- После завершения subagent терминал 2 закрывается, контекст очищен

## Security

- Subagent НЕ пишет в `state.json`, НЕ пишет в `phases.json`
- Subagent пишет только в `.workflow/subagent-handoff.json`
- Все изменения состояния — через оркестратор в терминале 1
