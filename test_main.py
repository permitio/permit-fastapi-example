from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

admin_token = 'Bearer admin@permit-todo.app'
                

def test_get_tasks():
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == [
        {"title": "Task 1", "checked": False},
        {"title": "Task 2", "checked": True},
        {"title": "Task 3", "checked": False},
    ]

def test_get_task():
    response = client.get("/tasks/1")
    assert response.status_code == 200
    assert response.json() == {"title": "Task 1", "checked": False}

def test_create_task():
    response = client.post("/tasks", json={"title": "Task 4", "checked": False}, headers={"Authorization": admin_token})
    assert response.status_code == 200
    assert response.json() == {"title": "Task 4", "checked": False}

def test_update_task():
    response = client.put("/tasks", json={"title": "Task 4", "checked": True}, headers={"Authorization": admin_token})
    assert response.status_code == 200
    assert response.json() == {"title": "Task 4", "checked": True}

def test_delete_task():
    response = client.delete("/tasks", json={"title": "Task 4", "checked": True}, headers={"Authorization": admin_token})
    assert response.status_code == 200
    assert response.json() == {"title": "Task 4", "checked": True}
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == [
        {"title": "Task 1", "checked": False},
        {"title": "Task 2", "checked": True},
        {"title": "Task 3", "checked": False},
    ]