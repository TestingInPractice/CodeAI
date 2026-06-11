# CodeAI Build Loop — Workflow Template

6 фаз: `plan-release → implement-spec-stage → write-tests → integrate-release → deploy-release`

## Терминал 1 (оркестратор)

Только смотрит состояние и говорит, что делать:

1. Прочитай `.workflow/state.json` — узнай текущую фазу
2. Запиши `.workflow/subagent-handoff.json` с `phase` и `skill_ref`
3. Скажи пользователю: "Открой T2, скажи `{phase}`"
4. Когда вернутся — прочитай `subagent-handoff.json`
5. Если `judge_verdict == "passed"`:
   - `python3 scripts/transition.py --project . --action transition`
   - Повтори с шага 1
6. Если иначе — объясни, пользователь открывает T2 снова

Подробно: `skills/workflow-core/SKILL.md`

## Терминал 2 (исполнитель + судья)

Всё в одной сессии: работа + судья.

1. Прочитай `.workflow/subagent-handoff.json`
2. Следуй `{skill_ref}` — делай фазу
3. Запусти судью: `python3 scripts/evaluate_judge.py prepare --project . --rubric judge-rubrics/{phase}.json`
4. Если FAILED — исправляй, пока не PASSED
5. Запиши результат в `.workflow/subagent-handoff.json`
6. Закрой терминал

## Контекст

- Оркестратор: `skills/workflow-core/SKILL.md`
- Протокол: `skills/workflow-core/references/subagent-protocol.md`
- Судья: `scripts/evaluate_judge.py` + `judge-rubrics/`
- Состояние: `.workflow/state.json` (читай/пиши только через `scripts/transition.py`)
