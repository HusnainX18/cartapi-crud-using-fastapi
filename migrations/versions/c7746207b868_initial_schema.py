"""initial schema

Revision ID: c7746207b868
Revises:
Create Date: 2026-06-06 01:43:05.755027

================================================================================
SNAPSHOT BASELINE - "Alembic snapshot pattern"
================================================================================
This is the *first* migration in the chain. It recreates the schema as it
exists in the live MySQL database on 2026-06-06. From this point on, every
schema change is applied as a new revision; this file is never edited.

Why hand-written (not autogenerate)?
    The DB and the SQLAlchemy models are already in sync, so
    `alembic revision --autogenerate` emits an empty `upgrade()`/`downgrade()`.
    That would be useless for fresh deployments (Docker, CI, EC2) where the
    DB does not exist yet - it would do nothing and leave the DB empty.

    The right tool is a manual "snapshot" migration: the upgrade() function
    rebuilds the exact DDL that the live DB already has, so running it on a
    fresh DB produces the same shape as the existing one.

How to use this on a fresh DB (e.g. Docker, EC2):
    $ alembic upgrade head
    # -> tables are created in the correct FK order:
    #    users, products, product_variants, carts, cart_items
    # -> alembic_version row is stamped with c7746207b868

How to use this against the existing XAMPP DB (where the schema already exists):
    $ alembic stamp head
    # -> alembic_version row is set to c7746207b768, but the migration is NOT run
    # -> use this any time you wipe the alembic_version table on a populated DB

Known drifts between model and DB (intentionally not fixed here):
  1. cart_items.quantity: model declares `CheckConstraint("quantity > 0")`
     but the DB has no such check. Constraint enforcement is missing.
  2. cart_items.product_variant_id: model declares `ondelete="RESTRICT"` on
     the FK, but the DB has no ON DELETE clause (default RESTRICT in MySQL,
     so the *behavior* matches, but the DDL differs).

These are out of scope for the snapshot baseline. A follow-up migration
should add them so future fresh deployments match the model.

================================================================================
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c7746207b868"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Recreate the 5 tables of the shopping-cart schema.

    Order matters: parent tables (users, products) must exist before
    children (product_variants, carts) reference them; cart_items references
    both carts and product_variants, so it comes last.
    """
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email", name="email"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_general_ci",
    )

    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("brand", sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_general_ci",
    )

    op.create_table(
        "product_variants",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("sku", sa.String(length=100), nullable=False),
        sa.Column("price", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column(
            "currency",
            sa.String(length=10),
            nullable=False,
            server_default="USD",
        ),
        sa.Column(
            "inventory_qty",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("sku", name="sku"),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            name="fk_product",
            ondelete="CASCADE",
        ),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_general_ci",
    )

    op.create_table(
        "carts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column(
            "discount",
            sa.Numeric(precision=10, scale=2),
            nullable=True,
            server_default=sa.text("0.00"),
        ),
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
            server_default=sa.text("'ACTIVE'"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_cart_user",
            ondelete="SET NULL",
        ),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_general_ci",
    )

    op.create_table(
        "cart_items",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("cart_id", sa.Integer(), nullable=False),
        sa.Column("product_variant_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unit_price", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("currency", sa.String(length=10), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("cart_id", "product_variant_id", name="uq_cart_variant"),
        sa.ForeignKeyConstraint(
            ["cart_id"],
            ["carts.id"],
            name="fk_cart",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["product_variant_id"],
            ["product_variants.id"],
            name="fk_variant",
        ),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_general_ci",
    )


def downgrade() -> None:
    """Drop all 5 tables in reverse FK order (children first)."""
    op.drop_table("cart_items")
    op.drop_table("carts")
    op.drop_table("product_variants")
    op.drop_table("products")
    op.drop_table("users")
