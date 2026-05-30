# Basic TypeScript Project

## Build & Test
- Build: `pnpm build`
- Dev: `pnpm dev`
- Test all: `pnpm vitest run`
- Single test: `pnpm vitest run -t "<test name>"`
- Lint: `pnpm lint`
- Typecheck: `pnpm typecheck`

## Code Style
- Strict TypeScript, no `any`
- Named exports, no default exports
- 2-space indent
- JSDoc on all public functions
- Prefer `const` over `let`

## Git Workflow
- Branch naming: `feature/`, `fix/`, `chore/`
- Commit format: `type(scope): message` (conventional commits)
- Run `pnpm lint && pnpm typecheck && pnpm test` before every commit
