"""
test_variants.py - 8 tests
Variant CRUD. 4 positive, 4 negative.
"""
from fastapi.testclient import TestClient


def _make_product(client, name="Phone") -> int:
    return client.post("/api/v1/products/", json={"name": name}).json()["id"]


# ------------------------------------------------------------------ #
# Positive
# ------------------------------------------------------------------ #

def test_create_variant_attaches_to_product(client: TestClient):
    pid = _make_product(client)
    r = client.post(f"/api/v1/products/{pid}/variants", json={
        "sku": "P-001", "price": 199.0, "inventory_qty": 50
    })
    assert r.status_code == 201
    body = r.json()
    assert body["sku"] == "P-001"
    assert body["product_id"] == pid
    assert body["price"] == 199.0


def test_get_variant_by_id(client: TestClient):
    pid = _make_product(client)
    v = client.post(f"/api/v1/products/{pid}/variants", json={
        "sku": "G-1", "price": 10.0, "inventory_qty": 5
    }).json()
    r = client.get(f"/api/v1/products/variants/{v['id']}")
    assert r.status_code == 200
    assert r.json()["sku"] == "G-1"


def test_update_variant_changes_price_and_qty(client: TestClient):
    pid = _make_product(client)
    v = client.post(f"/api/v1/products/{pid}/variants", json={
        "sku": "U-1", "price": 10.0, "inventory_qty": 5
    }).json()
    r = client.patch(f"/api/v1/products/variants/{v['id']}", json={
        "price": 12.5, "inventory_qty": 8
    })
    assert r.status_code == 200
    body = r.json()
    assert body["price"] == 12.5
    assert body["inventory_qty"] == 8


def test_delete_variant_returns_200(client: TestClient):
    pid = _make_product(client)
    v = client.post(f"/api/v1/products/{pid}/variants", json={
        "sku": "D-1", "price": 1.0, "inventory_qty": 1
    }).json()
    r = client.delete(f"/api/v1/products/variants/{v['id']}")
    assert r.status_code == 200
    # Confirm gone
    r2 = client.get(f"/api/v1/products/variants/{v['id']}")
    assert r2.status_code == 404


# ------------------------------------------------------------------ #
# Negative
# ------------------------------------------------------------------ #

def test_get_nonexistent_variant_returns_404(client: TestClient):
    r = client.get("/api/v1/products/variants/99999")
    assert r.status_code == 404


def test_update_nonexistent_variant_returns_404(client: TestClient):
    r = client.patch("/api/v1/products/variants/99999", json={"price": 1.0})
    assert r.status_code == 404


def test_delete_nonexistent_variant_returns_404(client: TestClient):
    r = client.delete("/api/v1/products/variants/99999")
    assert r.status_code == 404


def test_create_variant_with_duplicate_sku_returns_409(client: TestClient):
    """SKU has a UNIQUE constraint - duplicate triggers conflict."""
    pid = _make_product(client)
    r1 = client.post(f"/api/v1/products/{pid}/variants", json={
        "sku": "DUP-1", "price": 1.0, "inventory_qty": 1
    })
    assert r1.status_code == 201
    r2 = client.post(f"/api/v1/products/{pid}/variants", json={
        "sku": "DUP-1", "price": 2.0, "inventory_qty": 2
    })
    assert r2.status_code == 409
