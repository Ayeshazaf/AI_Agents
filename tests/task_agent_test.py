# Verify you can create, retrieve, update, and delete tasks cleanly.


def create_task_payload(task_id=1, title="Test Task"):
    return {
        "id": task_id,
        "title": title,
        "description": "A test task",
        "status": "in_progress",
        "priority": "high",
    }

def test_create_task(client):
    response = client.post("/tasks", json=create_task_payload())
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Task"
    
def test_retrieve_task(client):
    client.post("/tasks", json=create_task_payload())
    response = client.get("/tasks/1")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Task"

def test_update_task(client):
    client.post("/tasks", json=create_task_payload())
    response = client.put("/tasks/1", json={"id": 1, "title": "Updated Task", "description": "An updated test task", "status": "in_progress", "priority": "medium"})
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data

def test_delete_task(client):
    client.post("/tasks", json=create_task_payload())
    response = client.delete("/tasks/1")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Task 1 deleted"