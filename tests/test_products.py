"""
test_products.py - 12 tests
Product CRUD + cascade behaviour. 5 positive, 7 negative.
"""

from fastapi.testclient import TestClient

# ------------------------------------------------------------------ #
# Positive
# ------------------------------------------------------------------ #


def test_create_product_returns_201(client: TestClient):
    r = client.post(
        "/api/v1/products/", json={"name": "Laptop", "description": "16GB RAM", "brand": "Acme"}
    )
    assert r.status_code == 201
    body = r.json()
    assert body["name"] == "Laptop"
    assert body["brand"] == "Acme"


def test_list_products_returns_array(client: TestClient):
    """GET /products returns a list."""
    client.post("/api/v1/products/", json={"name": "Mouse"})
    r = client.get("/api/v1/products/")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    assert len(r.json()) >= 1


def test_get_product_includes_variants(client: TestClient):
    """GET /products/{id} returns the product with its variants list."""
    p = client.post("/api/v1/products/", json={"name": "Keyboard"}).json()
    client.post(
        f"/api/v1/products/{p['id']}/variants",
        json={"sku": "KB-001", "price": 49.99, "inventory_qty": 5},
    )
    r = client.get(f"/api/v1/products/{p['id']}")
    assert r.status_code == 200
    body = r.json()
    assert body["name"] == "Keyboard"
    assert len(body["variants"]) == 1
    assert body["variants"][0]["sku"] == "KB-001"


def test_update_product_changes_fields(client: TestClient):
    p = client.post("/api/v1/products/", json={"name": "OldName"}).json()
    r = client.patch(f"/api/v1/products/{p['id']}", json={"name": "NewName"})
    assert r.status_code == 200
    assert r.json()["name"] == "NewName"


def test_delete_product_cascades_to_variants(client: TestClient):
    """Deleting a product also deletes its variants (FK ON DELETE CASCADE)."""
    p = client.post("/api/v1/products/", json={"name": "ToDelete"}).json()
    v = client.post(
        f"/api/v1/products/{p['id']}/variants",
        json={"sku": "DEL-001", "price": 1.0, "inventory_qty": 1},
    ).json()
    r = client.delete(f"/api/v1/products/{p['id']}")
    assert r.status_code == 200
    # Variant should also be gone
    v_resp = client.get(f"/api/v1/products/variants/{v['id']}")
    assert v_resp.status_code == 404


# ------------------------------------------------------------------ #
# Negative
# ------------------------------------------------------------------ #


def test_get_nonexistent_product_returns_404(client: TestClient):
    r = client.get("/api/v1/products/99999")
    assert r.status_code == 404


def test_update_nonexistent_product_returns_404(client: TestClient):
    r = client.patch("/api/v1/products/99999", json={"name": "Ghost"})
    assert r.status_code == 404


def test_delete_nonexistent_product_returns_404(client: TestClient):
    r = client.delete("/api/v1/products/99999")
    assert r.status_code == 404


def test_create_product_with_empty_name_returns_422(client: TestClient):
    r = client.post("/api/v1/products/", json={"name": ""})
    assert r.status_code == 422


def test_create_variant_for_nonexistent_product_returns_404(client: TestClient):
    r = client.post(
        "/api/v1/products/99999/variants", json={"sku": "X-1", "price": 1.0, "inventory_qty": 0}
    )
    assert r.status_code == 404


def test_create_variant_with_negative_price_returns_422(client: TestClient):
    p = client.post("/api/v1/products/", json={"name": "BadPrice"}).json()
    r = client.post(
        f"/api/v1/products/{p['id']}/variants",
        json={"sku": "BAD-1", "price": -5.0, "inventory_qty": 1},
    )
    assert r.status_code == 422


def test_create_variant_with_zero_inventory_is_allowed(client: TestClient):
    """Zero inventory is valid (pydantic ge=0) - business can pre-list items."""
    p = client.post("/api/v1/products/", json={"name": "Preorder"}).json()
    r = client.post(
        f"/api/v1/products/{p['id']}/variants",
        json={"sku": "PO-1", "price": 99.0, "inventory_qty": 0},
    )
    assert r.status_code == 201
    assert r.json()["inventory_qty"] == 0
