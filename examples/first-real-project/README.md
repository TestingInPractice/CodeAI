# Task Manager API

REST API for task management built with FastAPI + SQLite.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /tasks | Create a task |
| GET | /tasks | List all tasks (optional: ?status=pending) |
| GET | /tasks/{id} | Get a task |
| PUT | /tasks/{id} | Update a task |
| DELETE | /tasks/{id} | Delete a task |
| GET | /stats | Get task statistics |

## Run

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Test

```bash
pytest tests/ -v
```
