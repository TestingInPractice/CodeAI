---
name: write-tests
description: >
  Фаза 3 workflow: интеграционные, e2e, регрессионные тесты по ТЗ + судья.
  Запускается в Терминале 2.
  Triggers: "write-tests"
type: workflow
step: 3
---

# Write Tests — Тестирование (терминал 2)

## Запуск

Прочитай `.workflow/subagent-handoff.json`.

Читать:
- `docs/specs/requirements.md` (F-XXX)
- `docs/specs/contracts/`
- `docs/specs/data-model.md`
- реализованный код

## Алгоритм

### Шаг 1-4: Написать тесты

- `tests/integration/` — для каждого API-контракта: success + error
- `tests/e2e/` — для каждого сценария из секции 2
- `tests/regression/` — для каждого AC из секции 9

Каждый F-XXX минимум 1 тест. Негативные сценарии обязательны.

### Шаг 5: Запустить

```bash
pytest tests/ -v --tb=short
pytest tests/ --cov=. --cov-report=term --cov-fail-under=80
```

### Шаг 6: Запустить судью

```bash
python3 scripts/evaluate_judge.py prepare --project . --rubric judge-rubrics/tester.json
```

Если FAILED → исправь → перезапусти судью.

### Шаг 7: Записать результат

```json
{
  "phase": "write-tests",
  "status": "DONE",
  "summary": "N тестов: M passed, coverage = X%",
  "judge_verdict": "passed",
  "judge_score": 85,
  "coverage": 85,
  "bugs": [],
  "evidence": ["tests/integration/auth_test.py"]
}
```

Статусы: `DONE`, `DONE_WITH_CONCERNS`, `BLOCKED`.
