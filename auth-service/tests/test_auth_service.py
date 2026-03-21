from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json().get("status") == "healthy"


def test_login_success():
    payload = {"email": "john@example.com", "password": "password123"}
    r = client.post("/login", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "token" in data
    assert data["user"]["email"] == "john@example.com"


def test_login_failure():
    payload = {"email": "nope@example.com", "password": "bad"}
    r = client.post("/login", json=payload)
    assert r.status_code == 401
