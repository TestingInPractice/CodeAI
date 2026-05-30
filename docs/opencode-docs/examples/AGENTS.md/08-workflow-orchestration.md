# Workflow Orchestration (Boris Cherny style)

## Planning
- For any non-trivial task (3+ steps or architectural decisions):
  write plan to `tasks/todo.md` with checkable items
- If something goes sideways, STOP and re-plan
- Save full plans to `docs/plans/<date>/plan-<feature>.md`
- Checklists to `docs/plans/<date>/checklist-<feature>.md`

## Execution
- Use subagents for research, exploration, parallel analysis
- One tack per subagent for focused execution
- After each stage: run `/simplify` skill, then run checklist
- Never mark complete without proving it works

## Self-Improvement
- After ANY user correction: update `tasks/lessons.md` with the pattern
- Write rules that prevent the same mistake
- Review lessons at session start
