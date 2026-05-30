# FastAPI Service

## Dev Commands
- Run: `uv run uvicorn src.main:app --reload`
- Test: `uv run pytest -xvs`
- Lint: `uv run ruff check src/ tests/`
- Typecheck: `uv run mypy src/`

## Project Structure
```
src/
  main.py          — FastAPI app entry
  api/
    routes/        — endpoint definitions
    schemas/       — Pydantic request/response models
  core/
    config.py      — settings via pydantic-settings
    db.py          — database session
    deps.py        — dependency injection
  services/        — business logic
tests/
  conftest.py      — fixtures (test client, test db)
  api/             — endpoint tests
  services/        — unit tests
```

## Conventions
- Input validation via Pydantic schemas, no manual checks
- Error responses: structured `{"detail": "...", "code": "..."}`
- Database: SQLAlchemy async + Alembic migrations
- Logging via `structlog`, not `print`
