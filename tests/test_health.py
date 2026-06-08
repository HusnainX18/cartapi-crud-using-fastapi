"""
test_health.py - 1 test
Liveness check. The app's heartbeat endpoint.
"""
from fastapi.testclient import TestClient


def test_health_check_returns_200_and_msg(client: TestClient):
    """GET / returns 200 with the app name + version in the message."""
    r = client.get("/")
    assert r.status_code == 200
    body = r.json()
    assert "msg" in body
    assert "CartAPI" in body["msg"]
    assert "1.0.0" in body["msg"]
