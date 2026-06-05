# CartAPI

A production-style shopping cart REST API built with FastAPI, SQLAlchemy 2.0, and MySQL.

Implements a clean layered architecture (router → service → repository) with custom exceptions, structured logging, and centralized error handling.

---

## Features

- Full CRUD for **Users**, **Products**, **Product Variants**, **Carts**, and **Cart Items**
- Inventory-aware **checkout** flow with automatic stock decrement
- Layered architecture: routers, services, repositories, models, schemas
- Centralized exception handling — clients only ever see `{"msg": "..."}` on errors
- Adaptive response logging (`SUCCESS` / `CLIENT_ERROR` / `SERVER_ERROR`) with method, path, status, duration
- Database error handlers for `IntegrityError`, `OperationalError`, generic `SQLAlchemyError`
- Auto-rollback of DB session on any unhandled exception

---

## Tech Stack

| Layer | Technology |
|---|---|
| Web framework | FastAPI 0.115 |
| ORM | SQLAlchemy 2.0 (typed `Mapped[...]` style) |
| Validation | Pydantic 2 + pydantic-settings |
| Database | MySQL 8.0 (via PyMySQL) |
| Migrations | Alembic (Phase 6) |
| Runtime | Python 3.12+ |

---

## Project Structure

```
app/
├── api/v1/              # FastAPI routers (cart, user, product)
├── constants/           # Enums (CartStatus, etc.)
├── core/                # Config + logger
├── db/                  # SQLAlchemy engine + session factory
├── exceptions/          # Custom exceptions + global handlers
├── middleware/          # Request/response logging middleware
├── models/              # SQLAlchemy ORM models
├── repositories/        # DB query layer (no business logic)
├── schemas/             # Pydantic request/response models
├── services/            # Business logic (uses repositories)
└── main.py              # FastAPI app factory
logs/                    # Runtime log files (gitignored)
```

---

## Quick Start

### 1. Prerequisites

- Python **3.12+**
- MySQL **8.0+** running locally
- A database named `shopping_cart_db` (created manually)

```sql
CREATE DATABASE shopping_cart_db CHARACTER SET utf8mb4;
```

### 2. Clone & install

```bash
git clone https://github.com/HusnainX18/cartapi-crud-using-fastapi.git
cd cartapi-crud-using-fastapi

python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env and fill in your MySQL credentials
```

### 4. Run the server

```bash
uvicorn app.main:app --reload
```

The API will be available at:

- **API:** http://localhost:8000
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## Environment Variables

| Variable | Description | Default | Required |
|---|---|---|---|
| `DATABASE_URL` | SQLAlchemy connection string | — | Yes |
| `APP_NAME` | Display name shown in docs and health check | `CartAPI` | No |
| `APP_VERSION` | App version | `1.0.0` | No |
| `DEBUG` | If `True`, SQLAlchemy echoes all SQL | `False` | No |
| `LOG_LEVEL` | `DEBUG` / `INFO` / `WARNING` / `ERROR` / `CRITICAL` | `INFO` | No |
| `LOG_TO_FILE` | If `True`, also write to `logs/app.log`. Disable in containers (stdout goes to CloudWatch). | `False` | No |

---

## API Endpoints (summary)

| Method | Path | Purpose |
|---|---|---|
| GET | `/` | Health check |
| POST | `/api/v1/users/` | Register a new user |
| GET | `/api/v1/users/{id}` | Get user by ID |
| PATCH | `/api/v1/users/{id}` | Update user |
| DELETE | `/api/v1/users/{id}` | Delete user |
| GET | `/api/v1/users/{id}/cart` | Get user's active cart |
| POST | `/api/v1/products/` | Create a product |
| GET | `/api/v1/products/` | List all products with variants |
| GET | `/api/v1/products/{id}` | Get a single product |
| PATCH | `/api/v1/products/{id}` | Update product |
| DELETE | `/api/v1/products/{id}` | Delete product (cascades variants) |
| POST | `/api/v1/products/{id}/variants` | Add a variant to a product |
| GET | `/api/v1/products/variants/{id}` | Get a variant |
| PATCH | `/api/v1/products/variants/{id}` | Update a variant |
| DELETE | `/api/v1/products/variants/{id}` | Delete a variant |
| POST | `/api/v1/carts/` | Create a cart |
| GET | `/api/v1/carts/{id}` | Get cart with items |
| DELETE | `/api/v1/carts/{id}` | Delete a cart |
| POST | `/api/v1/carts/{id}/items` | Add item to cart |
| PATCH | `/api/v1/carts/{id}/items/{item_id}` | Update item quantity |
| DELETE | `/api/v1/carts/{id}/items/{item_id}` | Remove item from cart |
| POST | `/api/v1/carts/{id}/checkout` | Checkout cart |

---

## Response Conventions

### Success (200, 201)
Returns the **actual resource(s)** — e.g. `GET /carts/1` returns the full cart with items, subtotal, total.

### Errors (4xx, 5xx)
Always returns `{"msg": "human-readable message"}` — no field names, types, or internal details leaked.

```json
{ "msg": "Cart with id=99 not found" }
```

---

## Logging

Every request produces a single log line with an outcome tag:

```
RESPONSE SUCCESS POST /api/v1/carts/ status=201 duration=12.4ms msg=Cart created
RESPONSE CLIENT_ERROR GET /api/v1/users/99 status=404 duration=3.1ms msg=User with id=99 not found
RESPONSE SERVER_ERROR POST /api/v1/carts/ status=500 duration=8.7ms msg=A database error occurred...
```

Log level adapts to status code (`INFO` / `WARNING` / `ERROR`).

---

## Roadmap

- [x] Phase 0 — Repo cleanup, logging hygiene
- [ ] Phase 2 — pytest suite + Postman collection (50+ tests)
- [ ] Phase 3 — Dockerfile + docker-compose
- [ ] Phase 4 — GitHub Actions CI/CD → DockerHub
- [ ] Phase 5 — EC2 deploy + CloudWatch logs
- [ ] Phase 6 — Alembic migrations wired into CI/CD

---

## License

MIT
