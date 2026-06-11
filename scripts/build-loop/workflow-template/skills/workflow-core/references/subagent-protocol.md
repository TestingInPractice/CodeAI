# Subagent Protocol

## Output format

Каждый subagent возвращает ровно 4 строки:

```
STATUS: <DONE|DONE_WITH_CONCERNS|BLOCKED|NEEDS_CONTEXT>
TASK_ID: <uuid задачи>
SUMMARY: <1 строка, что сделано>
EVIDENCE: <до 3 ссылок на файлы/тесты/логи>
```

## Status meanings

| Status | Meaning | Orchestrator action |
|--------|---------|---------------------|
| DONE | Задача выполнена, все AC пройдены | → Judge |
| DONE_WITH_CONCERNS | Выполнено, но есть open concerns | → Judge (решает rework или pass) |
| BLOCKED | Внешняя зависимость не выполнена | → Human (с причиной в SUMMARY) |
| NEEDS_CONTEXT | Не хватает информации (требования неясны) | → Open question → Human (до 2 уточнений), потом subagent |

## Open questions protocol

Когда subagent возвращает NEEDS_CONTEXT или judge FAIL с open questions:

1. Оркестратор создаёт запись в `state.{section}.open_questions[]`:
   ```json
   {
     "id": "oq-{uuid}",
     "question": "текст вопроса от subagent/judge",
     "answer": null,
     "resolved": false
   }
   ```
2. Оркестратор создаёт GitHub Issue с тегом `question`
3. Ставит `state.status = "waiting_human"` (через `transition.py --action wait`)
4. Пользователь отвечает в терминале → `transition.py --action resume`
5. UPDATE `docs/specs/requirements.md` — секция 12 (Open Questions)
6. ANSWER пишется в `state.{section}.open_questions[i].answer` + `resolved: true`
7. Оркестратор перезапускает subagent с обновлённым контекстом
8. После ответа subagent → judge заново

### CLI: ответ пользователя

```bash
# Оркестратор ждёт:
echo "OQ-{uuid}: {question}"
read USER_ANSWER

# Записать ответ в state
python3 -c "
import json
s = json.load(open('.workflow/state.json'))
oq = [q for q in s['plan_release']['open_questions'] if q['id'] == 'oq-{uuid}'][0]
oq['answer'] = '$USER_ANSWER'
oq['resolved'] = True
json.dump(s, open('.workflow/state.json', 'w'))
"

# resume
python3 scripts/transition.py --project . --action resume
```

## Context management

### Чтение по фазам

| Фаза | Читает | Не читает | Context budget |
|------|--------|-----------|----------------|
| `plan-release` | requirements.md (весь) | — | ≤5K |
| `implement-spec-stage` | 1 task.md + contracts/ для F-XXX | state.json (весь) | ≤4K на задачу |
| `write-tests` | contracts/ + spec секции 5, 9 | Код реализации (весь) | ≤6K |
| `integrate-release` | CHANGELOG.md + git log | task.md (все) | ≤3K |
| `deploy-release` | state.deploy_release + state.integrate_release + CHANGELOG.md | task.md, contracts/, spec/ | ≤2K |

### Progressive loading

Subagent читает файлы по мере необходимости, не все сразу:

1. Прочитать state.json (только свою секцию по section_key)
2. Если в секции есть ссылки на файлы (`spec_path`, `changelog_path`, задачи) — читать только их
3. **Не читать** файлы других фаз (docs/specs/architecture.md, contracts/, не свои task.md)

### Контекстный сброс между задачами

Для `implement-spec-stage`:
- Каждая задача — отдельный вызов subagent
- Оркестратор передаёт только: `task.uuid`, `task.title`, `spec_ref`
- После завершения задачи subagent завершается, контекст освобождается

Для `write-tests`:
- Один вызов, но не более 20 F-XXX за раз
- Если F-XXX > 20 — разбить на батчи
- Каждый батч = свежий вызов subagent с чистым контекстом

Для `plan-release`:
- Один вызов, но после секции 12 (Open Questions) — compaction
- Если user ответил на все вопросы — перезапустить subagent заново (старый контекст сброшен)

### Лимиты

- SUMMARY: ≤200 символов
- EVIDENCE: ≤3 ссылки, ≤500 символов всего
- TASK_ID: UUID из phases.json
- Context budget на файл: ≤1K токенов (если файл больше — читать offset/limit по секциям)

## Git protocol (для developer subagent)

1. `git checkout main && git pull`
2. `git checkout -b feat/{TASK_ID}`
3. Работать только в рамках этой ветки
4. Коммитить только относящиеся к задаче файлы
5. Написать unit-тесты
6. После DONE + judge PASSED: создать commit + push
7. Написать комментарий в GitHub Issue со ссылкой на коммит
8. Вернуться на main (оркестратор смержит)

## Security

- Subagent НЕ имеет права писать в .workflow/state.json
- Subagent НЕ имеет права писать в phases.json
- Все изменения состояния — только через оркестратор
