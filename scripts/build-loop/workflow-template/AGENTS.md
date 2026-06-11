# CodeAI Build Loop — Workflow Template

6 фаз: `plan-release → implement-spec-stage → write-tests → integrate-release → deploy-release`
Два терминала: 1 = оркестратор, 2 = субагент.

## Если это Терминал 1 (оркестратор)

Прочитай `.workflow/state.json` и следуй текущей фазе:

1. `transition.py --project . --action start —to {phase}`
2. Скажи пользователю: "Открой Терминал 2, скажи `{phase}`"
3. Жди "готово", прочитай `.workflow/subagent-handoff.json`
4. Запусти судью: `scripts/evaluate_judge.py prepare --rubric judge-rubrics/{phase}.json`
5. Если PASSED → переход к следующей фазе

Подробно: `skills/workflow-core/SKILL.md`

## Если это Терминал 2 (субагент)

Прочитай `.workflow/subagent-handoff.json` — там будет `skill_ref` и `task_uuid`.

Следуй инструкции из `{skill_ref}`.

После завершения запиши результат обратно в `.workflow/subagent-handoff.json`.
Этот терминал можно закрыть.

## Контекст

- Оркестратор: `skills/workflow-core/SKILL.md`
- Протокол: `skills/workflow-core/references/subagent-protocol.md`
- Судья: `scripts/evaluate_judge.py` + `judge-rubrics/`
- Состояние: `.workflow/state.json` (читай/пиши только через `scripts/transition.py`)
- Установки не нужны — всё из этой директории
