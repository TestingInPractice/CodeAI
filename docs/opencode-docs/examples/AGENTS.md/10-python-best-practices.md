# AGENTS.md для Python-разработчика

## Build & Test
- Install: `uv sync` (или `pip install -e ".[dev]"`)
- Test all: `uv run pytest` (или `pytest`)
- Single test: `uv run pytest tests/test_file.py::test_name -xvs`
- Lint: `uv run ruff check .`
- Format: `uv run ruff format .`
- Typecheck: `uv run mypy src/`
- Coverage: `uv run pytest --cov=src/ --cov-report=term-missing`

## Code Style
- PEP 8, type hints на все функции (Python 3.12+)
- `ruff` ruleset из `pyproject.toml`
- `pathlib` вместо `os.path`
- Dataclasses или Pydantic вместо raw dicts
- `isort` для сортировки импортов
- Имена: `snake_case` для функций/переменных, `PascalCase` для классов, `UPPER_CASE` для констант

## Project Structure
```
project/
├── src/
│   └── package/
│       ├── __init__.py
│       ├── main.py
│       ├── api/          # endpoints
│       ├── core/         # config, db, deps
│       ├── models/       # Pydantic/SQLAlchemy
│       ├── services/     # business logic
│       └── schemas/      # request/response models
├── tests/
│   ├── conftest.py
│   ├── test_api/
│   └── test_services/
├── pyproject.toml
├── README.md
└── AGENTS.md
```

## Dependencies & Environment
- Используй `uv` для управления пакетами (быстрее pip)
- `virtualenv` / `.venv` — изолируй окружение для каждого проекта
- `pyproject.toml` — единый источник конфигурации (вместо setup.py, requirements.txt, setup.cfg)
- Зависимости: основные в `[project.dependencies]`, dev в `[project.optional-dependencies]`

## Testing
- pytest — основной фреймворк
- Fixtures в `conftest.py` — для переиспользуемых тестовых данных
- Mock'и — только для внешних сервисов (API, БД, файловая система)
- Параметризация — `@pytest.mark.parametrize` вместо копирования тестов
- Coverage ≥ 80%, но главное — проверенная логика, а не процент
- `tox` или `nox` — для прогона тестов на нескольких версиях Python

## Libraries by Purpose
- **HTTP client:** `httpx` (асинхронный, вместо requests)
- **CLI:** `typer` или `click`
- **ORM:** SQLAlchemy 2.0 + Alembic для миграций
- **Validation:** Pydantic v2
- **Async:** `anyio` / `asyncio`
- **Data:** Polars (вместо pandas для больших данных)
- **Web framework:** FastAPI (REST) или Litestar

## Documentation
- Docstrings: Google style (или NumPy style)
- README.md: что, зачем, как запустить
- mkdocs или Sphinx для развёрнутой документации
- Примеры кода в docstrings — тестируются через doctest

## Performance & Security
- Избегай циклов в Pandas/Polars — используй vectorized operations
- `asyncio` для I/O-bound задач, `multiprocessing` для CPU-bound
- Не используй `pickle` с непроверенными данными
- SAST: `bandit` для сканирования безопасности
- `python-dotenv` для env variables, никогда не коммить `.env`
