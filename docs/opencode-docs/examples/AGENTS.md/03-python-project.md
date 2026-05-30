# Python Project

## Build & Test
- Install: `uv sync` (or `pip install -e ".[dev]"`)
- Test: `uv run pytest` (or `pytest`)
- Single test: `uv run pytest tests/test_file.py::test_name`
- Lint: `uv run ruff check .`
- Format: `uv run ruff format .`
- Typecheck: `uv run mypy src/`

## Code Style
- Python 3.12+, type hints on all functions
- `ruff` ruleset: based on `pyproject.toml`
- Use `pathlib` over `os.path`
- Dataclasses or Pydantic models, no raw dicts

## Project Structure
- `src/` — application code
- `tests/` — tests, mirroring `src/` structure
- `scripts/` — utility scripts
