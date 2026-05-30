# Monorepo (pnpm workspaces + Turborepo)

## Workspace Commands
- Install all: `pnpm install`
- Build all: `pnpm turbo run build`
- Build a package: `pnpm turbo run build --filter=@scope/package-name`
- Test all: `pnpm turbo run test`
- Lint all: `pnpm turbo run lint`

## Package Conventions
- Each package has its own AGENTS.md at `packages/<name>/AGENTS.md`
- Shared code goes in `packages/shared/`
- Internal dependencies use workspace protocol: `"@scope/shared": "workspace:*"`

## opencode.json (for monorepo glob)
```json
{
  "instructions": ["packages/*/AGENTS.md"]
}
```
