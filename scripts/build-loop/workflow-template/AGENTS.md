# CodeAI Build Loop — Workflow Template

Этот репозиторий содержит шаблон multi-agent workflow для opencode:
6 фаз (plan-release → implement-spec-stage → write-tests → integrate-release → deploy-release), гибридный судья с IEEE 29148, open questions loop.

## Если пользователь попросил развернуть workflow в новом проекте

1. **Определи целевой проект.** Пользователь передал ссылку на репозиторий или указал директорию.

2. **Запусти инициализацию:**
   ```
   python3 scripts/init_workflow.py --project <путь к проекту>
   ```

3. **Переключись на целевой проект.** Открой его директорию.

4. **Прочитай `.workflow/state.json`.** Там написана текущая фаза.

5. **Начни с plan-release** — прочитай `docs/specs/requirements.md` (пользователь его написал) и запусти цикл.

## Если пользователь просит запустить workflow в проекте, где уже есть `.workflow/`

Просто прочитай `.workflow/state.json` и следуй текущей фазе.

## Контекст

- Навыки оркестратора: `skills/workflow-core/SKILL.md`
- Протокол subagent: `skills/workflow-core/references/subagent-protocol.md`
- Судья: `scripts/evaluate_judge.py` + `judge-rubrics/`
- Состояние: `.workflow/state.json` (читай/пиши только через `scripts/transition.py`)
- Установки не нужны — всё работает из этой директории
