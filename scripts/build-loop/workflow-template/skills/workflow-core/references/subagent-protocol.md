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

Когда subagent возвращает NEEDS_CONTEXT:

1. Оркестратор создаёт запись в `state.{section}.open_questions[]`:
   ```json
   {
     "id": "oq-{uuid}",
     "question": "текст вопроса от subagent",
     "answer": null,
     "resolved": false
   }
   ```
2. Оркестратор создаёт GitHub Issue с тегом `question`
3. Ставит `state.status = "waiting_human"`
4. Пользователь отвечает → answer заполняется → resolved = true
5. Оркестратор перезапускает subagent с обновлённым контекстом

## Size limits

- SUMMARY: ≤200 символов
- EVIDENCE: ≤3 ссылки, ≤500 символов всего
- TASK_ID: UUID из phases.json

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
