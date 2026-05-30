# Project with opencode.json instructions

This AGENTS.md works together with `opencode.json`:
```json
{
  "instructions": [
    "CONTRIBUTING.md",
    "docs/development-standards.md",
    "packages/*/AGENTS.md",
    "https://raw.githubusercontent.com/org/shared-rules/main/style.md"
  ]
}
```

## When to use instructions vs AGENTS.md
- **AGENTS.md:** lightweight, project-specific, team-wide (in git)
- **instructions in opencode.json:** reusable rules, shared across projects,
  remote URLs, glob patterns for monorepos
- Both are merged into the same prompt
