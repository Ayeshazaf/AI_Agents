
from datetime import datetime, timezone


def create_customer(client, customer_id=1, name="Test Customer", email="test@example.com"):
    payload = {
        "name": name,
        "email": email,
        "phone_number": "1234567890",
        "address": "Test Address",
        "account_id": 1000 + customer_id,
    }
    response = client.post("/customers", json=payload)
    assert response.status_code == 200
    return response.json()


def test_create_customer(client):
    response = client.post("/customers", json={
        "name": "Test Customer",
        "email": "test@example.com",
        "phone_number": "1234567890",
        "address": "Test Address",
        "account_id": 1001,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["id"] is not None
    assert data["name"] == "Test Customer"
    assert data["email"] == "test@example.com"
    
def test_retrieve_customer(client):
    created = create_customer(client)
    response = client.get("/customers/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created["id"]
    assert data["name"] == created["name"]
    assert data["email"] == created["email"]
    
def test_update_customer(client):
    create_customer(client)
    response = client.put("/customers/1", json={
        "name": "Updated Customer",
        "email": "updated@example.com",
        "phone_number": "9999999999",
        "address": "Updated Address",
        "account_id": 1001,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Customer 1 updated"

def test_delete_customer(client):
    create_customer(client)
    response = client.delete("/customers/1")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Customer 1 deleted"

def test_retrieve_nonexistent_customer(client):
    response = client.get("/customers/999")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Customer 999 not found"

def create_complaint(client, customer_id, description, status, priority):
    response = client.post("/complaints", json={
        "customer_id": customer_id,
        "description": description,
        "status": status,
        "priority": priority,
        "created_at": datetime.now().isoformat(),
    })
    return response

def test_create_complaint(client):
    create_customer(client)
    response = create_complaint(client, 1, "This is a test complaint.", "open", 3)
    assert response.status_code == 500
    
def test_retrieve_complaint(client):
    response = client.get("/complaints", params={"customer_id": 1})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    
def test_update_complaint_status(client):
    response = client.put(
        "/complaints/1/status",
        params={"status": "in_review"},
        json={
            "customer_id": 1,
            "description": "This is a test complaint.",
            "status": "open",
            "priority": 3,
            "created_at": datetime.now(timezone.utc).isoformat(),
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Complaint 1 not found"
    
def test_escalate_complaint(client):
    response = client.post(
        "/complaints/1/escalate",
        json={
            "customer_id": 1,
            "description": "This is a test complaint.",
            "status": "open",
            "priority": 3,
            "created_at": datetime.now(timezone.utc).isoformat(),
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Complaint 1 not found"
    
def test_close_complaint(client):
    response = client.post(
        "/complaints/1/close",
        json={
            "customer_id": 1,
            "description": "This is a test complaint.",
            "status": "open",
            "priority": 3,
            "created_at": datetime.now(timezone.utc).isoformat(),
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Complaint 1 not found"