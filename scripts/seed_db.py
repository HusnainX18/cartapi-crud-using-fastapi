import random
import string
import time

from faker import Faker
from sqlalchemy import text

from app.db.database import SessionLocal
from app.models.product import Product
from app.models.product_variant import ProductVariant
from app.models.user import User

fake = Faker()

USERS_COUNT = 10_000
PRODUCTS_COUNT = 50_000
VARIANTS_COUNT = 100_000
BATCH_SIZE = 5_000

def seed_users(db, n: int):
    print(f"Seeding {n:,} users...")
    start = time.perf_counter()
    batch = []
    for i in range(n):
        batch.append({
            "name": fake.name(),
            "email": f"user{i}@example.com",
            "password_hash": fake.sha256(),
        })
        if len(batch) == BATCH_SIZE:
            db.execute(User.__table__.insert(), batch)
            db.commit()
            batch = []
    if batch:
        db.execute(User.__table__.insert(), batch)
        db.commit()
    print(f"  Done in {time.perf_counter() - start:.2f}s")

def seed_products(db, n: int):
    print(f"Seeding {n:,} products...")
    start = time.perf_counter()
    batch = []
    for i in range(n):
        batch.append({
            "name": fake.catch_phrase(),
            "description": fake.text(max_nb_chars=200),
            "brand": fake.company(),
        })
        if len(batch) == BATCH_SIZE:
            db.execute(Product.__table__.insert(), batch)
            db.commit()
            batch = []
    if batch:
        db.execute(Product.__table__.insert(), batch)
        db.commit()
    print(f"  Done in {time.perf_counter() - start:.2f}s")

def seed_variants(db, product_ids: list, n: int):
    print(f"Seeding {n:,} variants...")
    start = time.perf_counter()

    # Pre-generate unique uppercase SKUs
    skus = set()
    while len(skus) < n:
        letters = "".join(random.choices(string.ascii_uppercase, k=4))
        digits = "".join(random.choices(string.digits, k=4))
        skus.add(f"SKU-{letters}-{digits}")
    sku_list = list(skus)

    batch = []
    for i in range(n):
        batch.append({
            "product_id": random.choice(product_ids),
            "sku": sku_list[i],
            "price": round(random.uniform(1.0, 999.99), 2),
            "currency": "USD",
            "inventory_qty": random.randint(0, 1000),
        })
        if len(batch) == BATCH_SIZE:
            db.execute(ProductVariant.__table__.insert(), batch)
            db.commit()
            batch = []
    if batch:
        db.execute(ProductVariant.__table__.insert(), batch)
        db.commit()
    print(f"  Done in {time.perf_counter() - start:.2f}s")

def main():
    db = SessionLocal()
    try:
        # Disable foreign key and unique checks for speed
        db.execute(text("SET FOREIGN_KEY_CHECKS=0"))
        db.execute(text("SET UNIQUE_CHECKS=0"))
        db.commit()

        # Truncate tables to ensure a clean slate and avoid duplicate keys
        db.execute(text("TRUNCATE TABLE cart_items"))
        db.execute(text("TRUNCATE TABLE carts"))
        db.execute(text("TRUNCATE TABLE product_variants"))
        db.execute(text("TRUNCATE TABLE products"))
        db.execute(text("TRUNCATE TABLE users"))
        db.commit()

        seed_users(db, USERS_COUNT)
        seed_products(db, PRODUCTS_COUNT)

        # Get inserted product IDs to map variants
        product_ids = [row[0] for row in db.execute(text("SELECT id FROM products")).fetchall()]

        seed_variants(db, product_ids, VARIANTS_COUNT)

        db.execute(text("SET FOREIGN_KEY_CHECKS=1"))
        db.execute(text("SET UNIQUE_CHECKS=1"))
        db.commit()

        print("\nSeeding complete!")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
