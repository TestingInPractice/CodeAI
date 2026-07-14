"""Tests for Task Manager API."""

import pytest
from fastapi.testclient import TestClient
from app.main import app, init_db, DB_PATH
import os


@pytest.fixture(autouse=True)
def setup_db():
    if DB_PATH.exists():
        os.remove(DB_PATH)
    init_db()
    yield
    if DB_PATH.exists():
        os.remove(DB_PATH)


@pytest.fixture
def client():
    return TestClient(app)


class TestCreateTask:
    def test_create_task(self, client):
        resp = client.post("/tasks", json={"title": "Buy milk"})
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "Buy milk"
        assert data["status"] == "pending"
        assert "id" in data

    def test_create_task_with_description(self, client):
        resp = client.post("/tasks", json={"title": "Code", "description": "Write tests"})
        assert resp.status_code == 201
        assert resp.json()["description"] == "Write tests"

    def test_create_task_with_priority(self, client):
        resp = client.post("/tasks", json={"title": "Urgent", "priority": 5})
        assert resp.status_code == 201
        assert resp.json()["priority"] == 5


class TestListTasks:
    def test_list_empty(self, client):
        resp = client.get("/tasks")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_after_create(self, client):
        client.post("/tasks", json={"title": "Task 1"})
        client.post("/tasks", json={"title": "Task 2"})
        resp = client.get("/tasks")
        assert len(resp.json()) == 2

    def test_list_filter_by_status(self, client):
        client.post("/tasks", json={"title": "A"})
        client.post("/tasks", json={"title": "B"})
        task_id = client.get("/tasks").json()[0]["id"]
        client.put(f"/tasks/{task_id}", json={"status": "done"})
        resp = client.get("/tasks?status=done")
        assert len(resp.json()) == 1


class TestGetTask:
    def test_get_existing(self, client):
        create_resp = client.post("/tasks", json={"title": "Get me"})
        task_id = create_resp.json()["id"]
        resp = client.get(f"/tasks/{task_id}")
        assert resp.status_code == 200
        assert resp.json()["title"] == "Get me"

    def test_get_not_found(self, client):
        resp = client.get("/tasks/9999")
        assert resp.status_code == 404


class TestUpdateTask:
    def test_update_title(self, client):
        task_id = client.post("/tasks", json={"title": "Old"}).json()["id"]
        resp = client.put(f"/tasks/{task_id}", json={"title": "New"})
        assert resp.json()["title"] == "New"

    def test_update_status(self, client):
        task_id = client.post("/tasks", json={"title": "WIP"}).json()["id"]
        resp = client.put(f"/tasks/{task_id}", json={"status": "in_progress"})
        assert resp.json()["status"] == "in_progress"

    def test_update_not_found(self, client):
        resp = client.put("/tasks/9999", json={"title": "X"})
        assert resp.status_code == 404


class TestDeleteTask:
    def test_delete_existing(self, client):
        task_id = client.post("/tasks", json={"title": "Delete me"}).json()["id"]
        resp = client.delete(f"/tasks/{task_id}")
        assert resp.status_code == 204
        assert client.get(f"/tasks/{task_id}").status_code == 404

    def test_delete_not_found(self, client):
        resp = client.delete("/tasks/9999")
        assert resp.status_code == 404


class TestStats:
    def test_empty_stats(self, client):
        resp = client.get("/stats")
        assert resp.json() == {"total": 0, "by_status": {}}

    def test_stats_after_operations(self, client):
        client.post("/tasks", json={"title": "A"})
        client.post("/tasks", json={"title": "B"})
        task_id = client.get("/tasks").json()[0]["id"]
        client.put(f"/tasks/{task_id}", json={"status": "done"})
        resp = client.get("/stats")
        assert resp.json()["total"] == 2
        assert resp.json()["by_status"]["done"] == 1
        assert resp.json()["by_status"]["pending"] == 1
