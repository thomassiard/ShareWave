from fastapi.testclient import TestClient
from server.auth_service import app

client = TestClient(app)

def test_login():
    response = client.post("/login", json={"username": "user", "password": "pass"})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_invalid_login():
    response = client.post("/login", json={"username": "user", "password": "wrong_pass"})
    assert response.status_code == 401
