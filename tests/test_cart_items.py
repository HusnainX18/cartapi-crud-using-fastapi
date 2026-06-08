"""
test_cart_items.py - 10 tests
Add / update / delete items in a cart. 5 positive, 5 negative.
"""
from fastapi.testclient import TestClient


def _setup(client) -> tuple[int, int, int]:
    """Create user + product + variant, return (user_id, product_id, variant_id)."""
    uid = client.post("/api/v1/users/", json={
        "email": "shopper@example.com", "password": "secret", "name": "Shopper"
    }).json()["id"]
    pid = client.post("/api/v1/products/", json={"name": "Item"}).json()["id"]
    vid = client.post(f"/api/v1/products/{pid}/variants", json={
        "sku": "SHP-1", "price": 25.0, "inventory_qty": 100
    }).json()["id"]
    return uid, pid, vid


# ------------------------------------------------------------------ #
# Positive
# ------------------------------------------------------------------ #

def test_add_item_to_cart_returns_201(client: TestClient):
    uid, _, vid = _setup(client)
    c = client.post("/api/v1/carts/", json={"user_id": uid}).json()
    r = client.post(f"/api/v1/carts/{c['id']}/items", json={
        "product_variant_id": vid, "quantity": 2
    })
    assert r.status_code == 201
    body = r.json()
    assert len(body["items"]) == 1
    assert body["items"][0]["quantity"] == 2
    assert body["subtotal"] == 50.0  # 2 * 25.0


def test_update_item_quantity_changes_line_total(client: TestClient):
    uid, _, vid = _setup(client)
    c = client.post("/api/v1/carts/", json={"user_id": uid}).json()
    item = client.post(f"/api/v1/carts/{c['id']}/items", json={
        "product_variant_id": vid, "quantity": 1
    }).json()["items"][0]
    r = client.patch(
        f"/api/v1/carts/{c['id']}/items/{item['id']}",
        json={"quantity": 4},
    )
    assert r.status_code == 200
    assert r.json()["items"][0]["quantity"] == 4
    assert r.json()["subtotal"] == 100.0


def test_delete_item_removes_from_cart(client: TestClient):
    uid, _, vid = _setup(client)
    c = client.post("/api/v1/carts/", json={"user_id": uid}).json()
    item = client.post(f"/api/v1/carts/{c['id']}/items", json={
        "product_variant_id": vid, "quantity": 1
    }).json()["items"][0]
    r = client.delete(f"/api/v1/carts/{c['id']}/items/{item['id']}")
    assert r.status_code == 200
    r2 = client.get(f"/api/v1/carts/{c['id']}")
    assert r2.json()["items"] == []


def test_add_multiple_items_to_cart(client: TestClient):
    """Two different variants -> 2 items in cart."""
    uid = client.post("/api/v1/users/", json={
        "email": "multi@example.com", "password": "secret", "name": "M"
    }).json()["id"]
    p1 = client.post("/api/v1/products/", json={"name": "P1"}).json()["id"]
    p2 = client.post("/api/v1/products/", json={"name": "P2"}).json()["id"]
    v1 = client.post(f"/api/v1/products/{p1}/variants", json={
        "sku": "M-1", "price": 10.0, "inventory_qty": 50
    }).json()["id"]
    v2 = client.post(f"/api/v1/products/{p2}/variants", json={
        "sku": "M-2", "price": 20.0, "inventory_qty": 50
    }).json()["id"]
    c = client.post("/api/v1/carts/", json={"user_id": uid}).json()
    client.post(f"/api/v1/carts/{c['id']}/items", json={
        "product_variant_id": v1, "quantity": 1
    })
    r = client.post(f"/api/v1/carts/{c['id']}/items", json={
        "product_variant_id": v2, "quantity": 1
    })
    assert r.status_code == 201
    assert len(r.json()["items"]) == 2
    assert r.json()["subtotal"] == 30.0


def test_cart_total_applies_discount(client: TestClient):
    """Cart total = subtotal - discount (clamped at 0)."""
    uid = client.post("/api/v1/users/", json={
        "email": "disc@example.com", "password": "secret", "name": "D"
    }).json()["id"]
    pid = client.post("/api/v1/products/", json={"name": "DiscItem"}).json()["id"]
    vid = client.post(f"/api/v1/products/{pid}/variants", json={
        "sku": "DI-1", "price": 100.0, "inventory_qty": 10
    }).json()["id"]
    c = client.post("/api/v1/carts/", json={"user_id": uid, "discount": 30.0}).json()
    r = client.post(f"/api/v1/carts/{c['id']}/items", json={
        "product_variant_id": vid, "quantity": 1
    })
    assert r.json()["subtotal"] == 100.0
    assert r.json()["total"] == 70.0


# ------------------------------------------------------------------ #
# Negative
# ------------------------------------------------------------------ #

def test_add_duplicate_item_returns_409(client: TestClient):
    """Adding the same variant twice -> 409 (use PATCH instead)."""
    uid, _, vid = _setup(client)
    c = client.post("/api/v1/carts/", json={"user_id": uid}).json()
    client.post(f"/api/v1/carts/{c['id']}/items", json={
        "product_variant_id": vid, "quantity": 1
    })
    r = client.post(f"/api/v1/carts/{c['id']}/items", json={
        "product_variant_id": vid, "quantity": 1
    })
    assert r.status_code == 409


def test_add_item_with_quantity_exceeding_inventory_returns_422(client: TestClient):
    uid = client.post("/api/v1/users/", json={
        "email": "inv@example.com", "password": "secret", "name": "I"
    }).json()["id"]
    pid = client.post("/api/v1/products/", json={"name": "LowStock"}).json()["id"]
    vid = client.post(f"/api/v1/products/{pid}/variants", json={
        "sku": "LOW-1", "price": 50.0, "inventory_qty": 2
    }).json()["id"]
    c = client.post("/api/v1/carts/", json={"user_id": uid}).json()
    r = client.post(f"/api/v1/carts/{c['id']}/items", json={
        "product_variant_id": vid, "quantity": 100
    })
    assert r.status_code == 422


def test_add_item_with_nonexistent_variant_returns_404(client: TestClient):
    uid = client.post("/api/v1/users/", json={
        "email": "nf@example.com", "password": "secret", "name": "N"
    }).json()["id"]
    c = client.post("/api/v1/carts/", json={"user_id": uid}).json()
    r = client.post(f"/api/v1/carts/{c['id']}/items", json={
        "product_variant_id": 99999, "quantity": 1
    })
    assert r.status_code == 404


def test_update_nonexistent_cart_item_returns_404(client: TestClient):
    uid, _, vid = _setup(client)
    c = client.post("/api/v1/carts/", json={"user_id": uid}).json()
    r = client.patch(f"/api/v1/carts/{c['id']}/items/99999", json={"quantity": 1})
    assert r.status_code == 404


def test_add_item_with_zero_quantity_returns_422(client: TestClient):
    """gt=0 validation on quantity."""
    uid, _, vid = _setup(client)
    c = client.post("/api/v1/carts/", json={"user_id": uid}).json()
    r = client.post(f"/api/v1/carts/{c['id']}/items", json={
        "product_variant_id": vid, "quantity": 0
    })
    assert r.status_code == 422
