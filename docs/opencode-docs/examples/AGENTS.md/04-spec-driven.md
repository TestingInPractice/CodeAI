# Spec-Driven Development

## Workflow (GSD Loop)
1. Write spec in `docs/specs/` as markdown
2. Get review before implementation
3. Implement following the spec exactly
4. Verify: spec matches implementation
5. Commit with spec reference in message

## Spec Conventions
- Specs at `docs/specs/<name>/README.md`
- Include: context, requirements, API surface, examples
- ADRs at `docs/adr/` for architectural decisions
- After implementation, update specs to reflect reality

## References
- Project guidelines: @docs/guidelines.md
- API patterns: @docs/api-standards.md
