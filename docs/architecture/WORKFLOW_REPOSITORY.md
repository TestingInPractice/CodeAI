# WORKFLOW_REPOSITORY.md — Persistence Layer

**Date:** 2026-07-12
**Status:** Implemented (JSON)
**Package:** `scripts/core/repositories/`

---

## 1. Overview

Repository Pattern для хранения состояния Workflow Engine. Абстрагирует доступ к данным от бизнес-логики.

**Ключевой принцип:** Workflow Engine зависит от `WorkflowRepository` (интерфейс), не от конкретного хранилища. Замена JSON на SQLite не требует изменений в Engine.

---

## 2. Architecture

```
WorkflowEngine
    │
    ▼
WorkflowRepository (abstract)
    │
    ├── JsonWorkflowRepository (JSON files)
    └── (future) SqliteWorkflowRepository (SQLite)
```

### Storage Layout (JSON)

```
.workflow/
    state.json                    ← текущее состояние
    backups/
        20260712_103000_before-rollback.json
        20260712_104500_checkpoint.json
```

---

## 3. Interface: WorkflowRepository

**Module:** `scripts.core.repositories.base`

| Method | Signature | Returns | Description |
|--------|-----------|---------|-------------|
| `load` | `() -> WorkflowSnapshot \| None` | `WorkflowSnapshot \| None` | Загрузить текущее состояние |
| `save` | `(snapshot: WorkflowSnapshot) -> None` | `None` | Сохранить состояние |
| `backup` | `(label: str = "") -> str` | `str` (backup ID) | Создать бэкап |
| `restore` | `(backup_id: str) -> WorkflowSnapshot` | `WorkflowSnapshot` | Восстановить из бэкапа |
| `delete` | `() -> None` | `None` | Удалить текущее состояние |
| `list_backups` | `() -> list[dict]` | `list[dict]` | Список бэкапов |

---

## 4. Implementation: JsonWorkflowRepository

**Module:** `scripts.core.repositories.json_repo`

### Constructor

```python
JsonWorkflowRepository(
    state_dir: Path,           # Директория для файлов (e.g., ".workflow")
    state_filename: str = "state.json",  # Имя файла состояния
)
```

### Methods

#### `load()`

- Читает `state.json`
- Десериализует в `WorkflowSnapshot`
- Возвращает `None` если файла нет
- Raises `RepositoryError` при повреждении данных

#### `save(snapshot)`

- Создаёт директории если нет
- Сериализует `WorkflowSnapshot` в JSON
- Перезаписывает существующий файл
- Raises `RepositoryError` при ошибке записи

#### `backup(label)`

- Копирует `state.json` в `backups/<timestamp>_<label>.json`
- Если состояние пустое — сохраняет пустой `WorkflowSnapshot`
- Возвращает путь к бэкапу

#### `restore(backup_id)`

- Читает бэкап
- Десериализует в `WorkflowSnapshot`
- Сохраняет как текущее состояние
- Возвращает восстановленный снимок
- Raises `RepositoryError` если бэкап не найден

#### `delete()`

- Удаляет `state.json`
- Бэкапы не удаляются

#### `list_backups()`

- Сканирует `backups/` директорию
- Возвращает список метаданных: `id`, `label`, `created_at`, `size`

---

## 5. Error Handling

```python
class RepositoryError(Exception):
    message: str           # Описание ошибки
    code: str              # Стабильный код (REPO_LOAD_FAILED, etc.)
    recoverable: bool      # Можно ли повторить операцию
    cause: Exception | None  # Оригинальное исключение
```

### Error Codes

| Code | Description | Recoverable |
|------|-------------|-------------|
| `REPO_LOAD_FAILED` | Ошибка загрузки состояния | No |
| `REPO_SAVE_FAILED` | Ошибка сохранения | Yes |
| `REPO_BACKUP_FAILED` | Ошибка создания бэкапа | Yes |
| `REPO_BACKUP_NOT_FOUND` | Бэкап не найден | No |
| `REPO_RESTORE_FAILED` | Ошибка восстановления | No |
| `REPO_DELETE_FAILED` | Ошибка удаления | Yes |

---

## 6. Usage Examples

### Basic Operations

```python
from pathlib import Path
from scripts.core.repositories import JsonWorkflowRepository
from scripts.core.types import WorkflowSnapshot, WorkflowStatus

# Initialize
repo = JsonWorkflowRepository(Path(".workflow"))

# Load
snapshot = repo.load()
if snapshot is None:
    snapshot = WorkflowSnapshot(status=WorkflowStatus.IDLE)

# Modify
snapshot.iteration += 1
snapshot.status = WorkflowStatus.RUNNING

# Save
repo.save(snapshot)
```

### Backup Before Risky Operation

```python
# Backup before rollback
backup_id = repo.backup(label="before-rollback")

try:
    # Risky operation
    snapshot.phase.status = PhaseStatus.FAILED
    repo.save(snapshot)
except Exception:
    # Restore on failure
    repo.restore(backup_id)
```

### List Backups

```python
backups = repo.list_backups()
for b in backups:
    print(f"{b['label']} — {b['created_at']} ({b['size']} bytes)")
```

---

## 7. Replacing JSON with SQLite

To swap storage backend:

1. Create `SqliteWorkflowRepository` implementing `WorkflowRepository`
2. Change one line in Workflow Engine initialization:

```python
# Before (JSON)
repo = JsonWorkflowRepository(Path(".workflow"))

# After (SQLite)
repo = SqliteWorkflowRepository(Path(".workflow/state.db"))
```

Workflow Engine code does not change — it depends on the abstract `WorkflowRepository`.

### SQLite Schema (future)

```sql
CREATE TABLE workflow_state (
    id INTEGER PRIMARY KEY,
    data JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE workflow_backups (
    id INTEGER PRIMARY KEY,
    label TEXT,
    data JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 8. What Is NOT Implemented (yet)

- SQLite repository
- Concurrent access (file locking)
- State migration between backends
- Compression for large backups
- Retention policy (auto-delete old backups)
- Encryption for sensitive state
