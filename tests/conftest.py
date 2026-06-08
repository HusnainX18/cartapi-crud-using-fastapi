"""
Test configuration and fixtures.

Architecture
------------
1. `engine` (session scope) — connects to shopping_cart_test_db, creates it if missing
2. `db` (function scope) — for each test: drop_all + create_all + yield a session
3. `client` (function scope) — TestClient with get_db overridden to use the test session
4. `sample_*` — pre-populated entities the tests can reuse

Why per-test drop_all + create_all?
-----------------------------------
Each test gets a known-empty database. No state leaks between tests.
Cost: ~50ms per test. With ~66 tests that's ~3.3s total. Worth the reliability.
"""
from __future__ import annotations

import os

import pymysql
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import sessionmaker

# Ensure the test database is used BEFORE importing the app, so the app's
# engine and session factory point at the test schema (not the dev one).
TEST_DB_NAME = "shopping_cart_test_db"
os.environ.setdefault("DATABASE_URL", f"mysql+pymysql://root:@localhost:3306/{TEST_DB_NAME}")

import app.models  # noqa: E402, F401  (registers all models on Base.metadata)
from app.core.config import settings  # noqa: E402  (env var above must be set first)
from app.db.database import Base, get_db  # noqa: E402
from app.main import app as fastapi_app  # noqa: E402  (rename to avoid shadowing the `app` package)


def _ensure_test_database_exists() -> None:
    """Create the test schema in MySQL if it doesn't exist.

    Connects without selecting a database, runs CREATE DATABASE IF NOT EXISTS,
    then closes. Idempotent — safe to call on every test run.
    """
    url = make_url(settings.database_url)
    dbname = url.database
    conn = pymysql.connect(
        host=url.host or "localhost",
        port=url.port or 3306,
        user=url.username or "root",
        password=url.password or "",
    )
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"CREATE DATABASE IF NOT EXISTS `{dbname}` "
                f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        conn.commit()
    finally:
        conn.close()


@pytest.fixture(scope="session")
def engine():
    """Session-scoped SQLAlchemy engine bound to the test schema.

    Created once for the whole test run. Tables are managed per-test
    by the `db` fixture (drop_all + create_all).
    """
    _ensure_test_database_exists()
    eng = create_engine(
        settings.database_url,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )
    yield eng
    eng.dispose()


@pytest.fixture(scope="session")
def SessionLocalTest(engine):
    """SessionLocal factory bound to the test engine."""
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def db(SessionLocalTest, engine):
    """Function-scoped DB session with a fresh schema.

    For each test:
        1. drop_all (wipe any prior state)
        2. create_all (build tables from Base.metadata)
        3. yield a session
        4. close the session

    Tests use this fixture to get a real DB session. The `client` fixture
    also uses it (via dependency override) so API calls hit the same DB.
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = SessionLocalTest()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db, SessionLocalTest):
    """FastAPI TestClient with get_db overridden to use the test session.

    This is the key trick: every API call in the tests goes through the
    overridden dependency, so it talks to the test schema, not the dev one.
    """

    def _override_get_db():
        try:
            yield db
        finally:
            pass  # session lifecycle owned by the `db` fixture

    fastapi_app.dependency_overrides[get_db] = _override_get_db
    with TestClient(fastapi_app) as c:
        yield c
    fastapi_app.dependency_overrides.clear()


# ------------------------------------------------------------------ #
# Sample-data factory fixtures
# ------------------------------------------------------------------ #
# These build real rows via the API so they reflect what the service
# layer actually does (hashing, defaults, FK checks, etc.).
# Each returns the JSON response so tests can chain off .json()["id"].


def _create_user(client, email="alice@example.com", password="secret123", name="Alice"):
    return client.post("/api/v1/users/", json={
        "email": email, "password": password, "name": name
    })


def _create_product(client, name="Widget", description="A widget", brand="Acme"):
    return client.post("/api/v1/products/", json={
        "name": name, "description": description, "brand": brand
    })


def _create_variant(
    client, product_id, sku="SKU-001", price=9.99, currency="USD", inventory_qty=100
):
    return client.post(
        f"/api/v1/products/{product_id}/variants",
        json={"sku": sku, "price": price, "currency": currency, "inventory_qty": inventory_qty},
    )


def _create_cart(client, user_id, discount=0.0):
    return client.post("/api/v1/carts/", json={"user_id": user_id, "discount": discount})


@pytest.fixture()
def sample_user(client):
    """Returns (response, user_id)."""
    r = _create_user(client)
    assert r.status_code == 201, r.text
    return r, r.json()["id"]


@pytest.fixture()
def sample_product(client):
    """Returns (response, product_id)."""
    r = _create_product(client)
    assert r.status_code == 201, r.text
    return r, r.json()["id"]


@pytest.fixture()
def sample_variant(client, sample_product):
    """Returns (response, variant_id). Depends on sample_product."""
    _, product_id = sample_product
    r = _create_variant(client, product_id)
    assert r.status_code == 201, r.text
    return r, r.json()["id"]


@pytest.fixture()
def sample_cart(client, sample_user):
    """Returns (response, cart_id). Depends on sample_user."""
    _, user_id = sample_user
    r = _create_cart(client, user_id)
    assert r.status_code == 201, r.text
    return r, r.json()["id"]
