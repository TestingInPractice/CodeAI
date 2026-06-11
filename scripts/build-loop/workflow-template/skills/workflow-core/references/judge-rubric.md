# Judge Rubric Protocol

## Output format

```
VERDICT: <PASS|FAIL|PASS_WITH_CONCERNS>
SCORE: <0.0–1.0>
CRITICAL_FAILURES: <count>
SUMMARY: <1 строка, главный вывод>
```

## Rules

- PASS: score >= pass_threshold (из rubric) AND critical_failures == 0
- PASS_WITH_CONCERNS: score >= (pass_threshold - 0.2) AND critical_failures == 0
- FAIL: score < (pass_threshold - 0.2) OR critical_failures > 0

## Scoring

Каждый критерий оценивается по шкале 1-5:

| Score | Meaning |
|-------|---------|
| 5 | Превосходно, нет замечаний |
| 4 | Хорошо, мелкие недочёты |
| 3 | Удовлетворительно, есть замечания |
| 2 | Плохо, серьёзные проблемы |
| 1 | Не выполнено |

Итоговый score = weighted average:

```
score = sum(weight_i * score_i) / sum(weight_i) / 5
```

Где score_i ∈ {1,2,3,4,5}, weight_i — вес критерия.

## How to use

1. Оркестратор выбирает rubric по роли (analyst/developer/tester)
2. Передаёт rubric + артефакты судье
3. Судья оценивает каждый критерий с evidence
4. Оркестратор проверяет VERDICT
5. Если FAIL → rework или open question → human
6. Если PASS → записать verdict в state.json и перейти к следующей фазе

## Rubric format (JSON)

```json
{
  "name": "analyst|developer|tester",
  "rubric": [
    {
      "id": "criterion_id",
      "label": "Человекочитаемое название",
      "weight": 1-5,
      "scale": 5,
      "pass": 3-5,
      "critical": true/false,
      "evidence_required": true/false
    }
  ],
  "pass_threshold": 0.8,
  "allow_passed_with_concerns": true
}
```

## Phase-specific judges

| Phase | Judge rubric | What it checks |
|-------|-------------|----------------|
| `plan-release` | analyst | Полнота декомпозиции, трассируемость до ТЗ, качество задач |
| `implement-spec-stage` | developer | Качество кода, стиль, тесты, ADR compliance |
| `write-tests` | tester | Покрытие ТЗ тестами, негативные сценарии |
