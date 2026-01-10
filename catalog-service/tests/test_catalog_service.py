from fastapi.testclient import TestClient
import catalog_service.core.middlewares.auth_middleware as auth_middleware
from main import app


class _FakeResp:
    def __init__(self, status_code=200, payload=None):
        self.status_code = status_code
        self._payload = payload or {}

    def json(self):
        return self._payload


def test_home(monkeypatch):
    # Patch the requests.post used by the AuthMiddleware to simulate successful verify
    monkeypatch.setattr(auth_middleware.requests, "post", lambda url, params=None: _FakeResp(200, {}))
    client = TestClient(app)
    r = client.get("/")
    assert r.status_code == 401

