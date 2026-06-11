---
name: write-tests
description: >
  Фаза 3 workflow: интеграционное, e2e и регрессионное тестирование.
  Создание тест-кейсов по ТЗ, покрытие всех F-XXX, проверка coverage.
  Triggers: "write tests", "add integration tests", "test coverage",
  "run test suite".
type: workflow
step: 3
---

# Write Tests — Интеграционное тестирование

## Workflow Contract

entry:
  artifacts:
    - .workflow/state.json
    - docs/specs/requirements.md
    - docs/specs/contracts/ (API контракты)
    - docs/specs/data-model.md
    - реализованный код (из implement-spec-stage)
  condition: >
    state.phase == "write-tests" AND
    state.status == "in_progress" AND
    state.implement_spec_stage.judge_verdict == "passed"

exit:
  condition: Все тест-кейсы написаны и прошли, coverage >= threshold
  artifacts:
    - integration tests
    - e2e tests
    - regression tests
    - coverage report

next_skill: integrate-release (если judge PASSED)

---

## Алгоритм

### Шаг 1: Получить список тест-кейсов

Прочитай `state.write_tests.test_cases[]`.

Если `test_cases[]` пуст — создай тест-кейсы из ТЗ.

### Шаг 2: Определить coverage target

Прочитай `state.write_tests.coverage`:
- `threshold` — минимальный процент покрытия (по умолчанию 80)
- `percentage` — текущий (0, если ещё не считали)

### Шаг 3: Создать тест-кейсы по ТЗ

Для каждого F-XXX из `docs/specs/requirements.md` (секция 5) создай тест-кейсы:

| Тип теста | Когда создавать |
|---|---|
| `integration` | Для каждого API-контракта из `docs/specs/contracts/` |
| `e2e` | Для каждого пользовательского сценария из секции 2 (Цель) |
| `regression` | Для каждого AC из секции 9 |

Формат тест-кейса в `state.write_tests.test_cases[]`:

```json
{
  "id": "TC-001",
  "title": "POST /api/auth/telegram — успешная авторизация",
  "ref_issue": "F-001",
  "type": "integration",
  "scenario": "Отправить POST /api/auth/telegram с валидным initData",
  "expected": "Статус 200, тело { token, user }",
  "status": "pending"
}
```

Правила:
- **Каждый F-XXX** покрыт минимум 1 тест-кейсом
- **Каждый API-эндпоинт** покрыт: success + error (400, 401, 404, 500)
- **Негативные сценарии** обязательны: невалидные данные, отсутствие прав, таймауты
- **Граничные случаи**: пустые списки, максимальные значения, спецсимволы

### Шаг 4: Написать integration тесты

Для каждого API-контракта:
1. Создай файл `tests/integration/{endpoint}_test.{ext}`
2. Реализуй позитивные сценарии (success)
3. Реализуй негативные сценарии (4xx, 5xx)
4. Проверь response body соответствует контракту

```bash
pytest tests/integration/ -v
```

### Шаг 5: Написать e2e тесты

Для каждого пользовательского сценария:
1. Создай файл `tests/e2e/{scenario}_test.{ext}`
2. Реализуй полный flow: авторизация → действие → проверка результата

### Шаг 6: Написать regression тесты

Для каждого AC из секции 9:
1. Создай файл `tests/regression/{ac_id}_test.{ext}`
2. Проверь, что уже реализованная фича не сломалась

### Шаг 7: Запустить тесты

```bash
pytest tests/ -v --tb=short 2>&1
```

### Шаг 8: Проверить coverage

```bash
pytest tests/ --cov=. --cov-report=term --cov-fail-under={threshold}
```

Обнови `state.write_tests.coverage.percentage`.

Если coverage < threshold → `DONE_WITH_CONCERNS`.

### Шаг 9: Отметить статусы

Для каждого пройденного тест-кейса установи `status: passed`.
Для каждого упавшего — `status: failed`.

### Если тесты не проходят

1. Определи причину: баг в реализации или некорректный тест
2. Если баг → `STATUS: BLOCKED`, укажи F-XXX и описание бага
3. Если тест некорректен → исправь тест

### Формат вывода

```
STATUS: DONE | DONE_WITH_CONCERNS | BLOCKED
SUMMARY: N тестов: M passed / F failed / S skipped, coverage = X%
EVIDENCE:
  - tests/integration/auth_test.py
  - tests/e2e/registration_test.py
  - tests/regression/ac_001_test.py
```
