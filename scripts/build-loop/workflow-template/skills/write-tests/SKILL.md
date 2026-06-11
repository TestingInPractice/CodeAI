---
name: write-tests
description: >
  Фаза 3 workflow: интеграционные, e2e и регрессионные тесты по ТЗ.
  Запускается в Терминале 2.
  Triggers: "write-tests", "test coverage check"
type: workflow
step: 3
---

# Write Tests — Интеграционное тестирование (терминал 2)

## Запуск

Запускается в Терминале 2 по инструкции оркестратора.
Входная точка: прочитай `.workflow/subagent-handoff.json`.

## Workflow Contract

entry:
  condition: state.phase == "write-tests" AND status == "in_progress"
  читать:
    - .workflow/subagent-handoff.json
    - docs/specs/requirements.md (F-XXX)
    - docs/specs/contracts/ (API контракты)
    - docs/specs/data-model.md
    - реализованный код (из implement-spec-stage)

exit:
  создать:
    - tests/integration/
    - tests/e2e/
    - tests/regression/

## Алгоритм

### Шаг 1: Создать тест-кейсы по ТЗ

Для каждого F-XXX из `docs/specs/requirements.md` (секция 5) создай:

| Тип теста | Когда |
|---|---|
| `integration` | Для каждого API-контракта из `docs/specs/contracts/` |
| `e2e` | Для каждого сценария из секции 2 (Цель) |
| `regression` | Для каждого AC из секции 9 |

Правила:
- **Каждый F-XXX** покрыт минимум 1 тест-кейсом
- **Каждый API-эндпоинт**: success + error (400, 401, 404, 500)
- **Негативные сценарии** обязательны
- **Граничные случаи**: пустые списки, максимумы, спецсимволы

### Шаг 2: Написать integration тесты

`tests/integration/{endpoint}_test.{ext}` — позитивные + негативные сценарии.

```bash
pytest tests/integration/ -v
```

### Шаг 3: Написать e2e тесты

`tests/e2e/{scenario}_test.{ext}` — полный flow: авторизация → действие → проверка.

### Шаг 4: Написать regression тесты

`tests/regression/{ac_id}_test.{ext}` — проверка, что фича не сломалась.

### Шаг 5: Запустить все тесты

```bash
pytest tests/ -v --tb=short
```

### Шаг 6: Проверить coverage

```bash
pytest tests/ --cov=. --cov-report=term --cov-fail-under={80}
```

Если coverage < threshold → верни `DONE_WITH_CONCERNS`.

### Если баг в реализации

→ верни `STATUS: BLOCKED`, укажи F-XXX и описание.

## Формат вывода

```json
{
  "phase": "write-tests",
  "status": "DONE",
  "summary": "N тестов: M passed / F failed, coverage = X%",
  "evidence": [
    "tests/integration/auth_test.py",
    "tests/e2e/registration_test.py",
    "tests/regression/ac_001_test.py"
  ],
  "coverage": 85,
  "bugs": [
    {"id": "BUG-001", "description": "POST /api/login returns 500"}
  ]
}
```

Возможные статусы: `DONE`, `DONE_WITH_CONCERNS`, `BLOCKED`.
