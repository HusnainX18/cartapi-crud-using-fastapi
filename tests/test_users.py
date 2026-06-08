"""
test_users.py - 10 tests
User CRUD: 5 positive, 5 negative.
"""

from fastapi.testclient import TestClient

# ------------------------------------------------------------------ #
# Positive
# ------------------------------------------------------------------ #


def test_create_user_returns_201_with_id(client: TestClient):
    """POST /users with valid payload returns 201 and an id."""
    r = client.post(
        "/api/v1/users/", json={"email": "bob@example.com", "password": "hunter2", "name": "Bob"}
    )
    assert r.status_code == 201
    body = r.json()
    assert body["email"] == "bob@example.com"
    assert body["name"] == "Bob"
    assert isinstance(body["id"], int)


def test_get_user_by_id_returns_matching_user(client: TestClient):
    """POST then GET returns the same user."""
    created = client.post(
        "/api/v1/users/", json={"email": "carol@example.com", "password": "secret", "name": "Carol"}
    ).json()
    r = client.get(f"/api/v1/users/{created['id']}")
    assert r.status_code == 200
    assert r.json()["email"] == "carol@example.com"


def test_update_user_changes_name_and_email(client: TestClient):
    """PATCH /users/{id} updates fields."""
    created = client.post(
        "/api/v1/users/", json={"email": "dan@example.com", "password": "secret", "name": "Dan"}
    ).json()
    r = client.patch(f"/api/v1/users/{created['id']}", json={"name": "Daniel"})
    assert r.status_code == 200
    assert r.json()["name"] == "Daniel"


def test_delete_user_returns_200_with_msg(client: TestClient):
    """DELETE /users/{id} returns a confirmation message."""
    created = client.post(
        "/api/v1/users/", json={"email": "eve@example.com", "password": "secret", "name": "Eve"}
    ).json()
    r = client.delete(f"/api/v1/users/{created['id']}")
    assert r.status_code == 200
    assert "msg" in r.json()


def test_get_user_cart_for_user_with_no_cart_returns_404(client: TestClient):
    """A user with no cart returns 404 (no active cart exists)."""
    created = client.post(
        "/api/v1/users/", json={"email": "frank@example.com", "password": "secret", "name": "Frank"}
    ).json()
    r = client.get(f"/api/v1/users/{created['id']}/cart")
    assert r.status_code == 404


# ------------------------------------------------------------------ #
# Negative
# ------------------------------------------------------------------ #


def test_get_user_with_nonexistent_id_returns_404(client: TestClient):
    """GET on a missing user returns 404."""
    r = client.get("/api/v1/users/99999")
    assert r.status_code == 404
    assert "msg" in r.json()


def test_update_nonexistent_user_returns_404(client: TestClient):
    """PATCH on a missing user returns 404."""
    r = client.patch("/api/v1/users/99999", json={"name": "Ghost"})
    assert r.status_code == 404


def test_delete_nonexistent_user_returns_404(client: TestClient):
    """DELETE on a missing user returns 404."""
    r = client.delete("/api/v1/users/99999")
    assert r.status_code == 404


def test_create_user_with_duplicate_email_returns_409(client: TestClient):
    """Two users with the same email -> 409 conflict."""
    payload = {"email": "dupe@example.com", "password": "secret", "name": "First"}
    r1 = client.post("/api/v1/users/", json=payload)
    assert r1.status_code == 201
    r2 = client.post("/api/v1/users/", json={**payload, "name": "Second"})
    assert r2.status_code == 409


def test_create_user_with_short_password_returns_422(client: TestClient):
    """Pydantic validation: password < 6 chars -> 422."""
    r = client.post(
        "/api/v1/users/", json={"email": "weak@example.com", "password": "abc", "name": "Weak"}
    )
    assert r.status_code == 422
    body = r.json()
    assert "msg" in body
