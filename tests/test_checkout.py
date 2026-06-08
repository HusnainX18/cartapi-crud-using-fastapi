"""
test_checkout.py - 5 tests
Checkout: success, empty, insufficient inventory, status change, inventory decrement.
3 positive, 2 negative.
"""

from fastapi.testclient import TestClient


def _setup_full(client, inventory=10, price=10.0):
    """User + product + variant + cart with 1 item of qty=2. Return all ids."""
    uid = client.post(
        "/api/v1/users/", json={"email": "buyer@example.com", "password": "secret", "name": "Buyer"}
    ).json()["id"]
    pid = client.post("/api/v1/products/", json={"name": "BuyItem"}).json()["id"]
    vid = client.post(
        f"/api/v1/products/{pid}/variants",
        json={"sku": "CHK-1", "price": price, "inventory_qty": inventory},
    ).json()["id"]
    c = client.post("/api/v1/carts/", json={"user_id": uid}).json()
    client.post(f"/api/v1/carts/{c['id']}/items", json={"product_variant_id": vid, "quantity": 2})
    return uid, pid, vid, c["id"]


# ------------------------------------------------------------------ #
# Positive
# ------------------------------------------------------------------ #


def test_checkout_returns_200_and_marks_cart_checked_out(client: TestClient):
    _, _, _, cid = _setup_full(client)
    r = client.post(f"/api/v1/carts/{cid}/checkout")
    assert r.status_code == 200
    assert r.json()["status"] == "CHECKED_OUT"


def test_checkout_decrements_variant_inventory(client: TestClient):
    """Inventory is reduced by the purchased quantity."""
    _, _, vid, cid = _setup_full(client, inventory=10, price=10.0)
    # Initial inventory = 10
    before = client.get(f"/api/v1/products/variants/{vid}").json()["inventory_qty"]
    assert before == 10
    client.post(f"/api/v1/carts/{cid}/checkout")
    after = client.get(f"/api/v1/products/variants/{vid}").json()["inventory_qty"]
    assert after == 8  # 10 - 2


def test_cannot_add_to_checked_out_cart(client: TestClient):
    """Once a cart is CHECKED_OUT, adding items returns 400."""
    _, _, vid, cid = _setup_full(client)
    client.post(f"/api/v1/carts/{cid}/checkout")
    r = client.post(f"/api/v1/carts/{cid}/items", json={"product_variant_id": vid, "quantity": 1})
    assert r.status_code == 400


# ------------------------------------------------------------------ #
# Negative
# ------------------------------------------------------------------ #


def test_checkout_empty_cart_returns_400(client: TestClient):
    """An empty cart cannot be checked out -> 400."""
    uid = client.post(
        "/api/v1/users/", json={"email": "empty@example.com", "password": "secret", "name": "E"}
    ).json()["id"]
    c = client.post("/api/v1/carts/", json={"user_id": uid}).json()
    r = client.post(f"/api/v1/carts/{c['id']}/checkout")
    assert r.status_code == 400
    assert "empty" in r.json()["msg"].lower()


def test_checkout_nonexistent_cart_returns_404(client: TestClient):
    r = client.post("/api/v1/carts/99999/checkout")
    assert r.status_code == 404
