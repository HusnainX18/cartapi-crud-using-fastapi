from sqlalchemy.orm import Session, joinedload
from app.models.product import Product
from app.models.product_variant import ProductVariant
from app.core.logger import get_logger

logger = get_logger(__name__)


class ProductRepository:

    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------------------------ #
    # PRODUCT CRUD
    # ------------------------------------------------------------------ #

    def create_product(self, name: str, description: str | None, brand: str | None) -> Product:
        product = Product(name=name, description=description, brand=brand)
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        logger.info(f"Product created | product_id={product.id} name={name}")
        return product

    def get_product_by_id(self, product_id: int) -> Product | None:
        return (
            self.db.query(Product)
            .options(joinedload(Product.variants))
            .filter(Product.id == product_id)
            .first()
        )

    def get_all_products(self) -> list[Product]:
        return (
            self.db.query(Product)
            .options(joinedload(Product.variants))
            .all()
        )

    def update_product(
        self, product: Product, name: str | None, description: str | None, brand: str | None
    ) -> Product:
        if name is not None:
            product.name = name
        if description is not None:
            product.description = description
        if brand is not None:
            product.brand = brand
        self.db.commit()
        self.db.refresh(product)
        logger.info(f"Product updated | product_id={product.id}")
        return product

    def delete_product(self, product: Product) -> None:
        self.db.delete(product)
        self.db.commit()
        logger.info(f"Product deleted | product_id={product.id}")

    # ------------------------------------------------------------------ #
    # VARIANT CRUD
    # ------------------------------------------------------------------ #

    def create_variant(
        self,
        product_id: int,
        sku: str,
        price: float,
        currency: str,
        inventory_qty: int,
    ) -> ProductVariant:
        variant = ProductVariant(
            product_id=product_id,
            sku=sku,
            price=price,
            currency=currency,
            inventory_qty=inventory_qty,
        )
        self.db.add(variant)
        self.db.commit()
        self.db.refresh(variant)
        logger.info(f"Variant created | variant_id={variant.id} sku={sku}")
        return variant

    def get_variant_by_id(self, variant_id: int) -> ProductVariant | None:
        return (
            self.db.query(ProductVariant)
            .options(joinedload(ProductVariant.product))
            .filter(ProductVariant.id == variant_id)
            .first()
        )

    def get_variant_by_sku(self, sku: str) -> ProductVariant | None:
        return self.db.query(ProductVariant).filter(ProductVariant.sku == sku).first()

    def get_variants_by_product(self, product_id: int) -> list[ProductVariant]:
        return (
            self.db.query(ProductVariant)
            .filter(ProductVariant.product_id == product_id)
            .all()
        )

    def update_variant(
        self,
        variant: ProductVariant,
        sku: str | None,
        price: float | None,
        currency: str | None,
        inventory_qty: int | None,
    ) -> ProductVariant:
        if sku is not None:
            variant.sku = sku
        if price is not None:
            variant.price = price
        if currency is not None:
            variant.currency = currency
        if inventory_qty is not None:
            variant.inventory_qty = inventory_qty
        self.db.commit()
        self.db.refresh(variant)
        logger.info(f"Variant updated | variant_id={variant.id}")
        return variant

    def delete_variant(self, variant: ProductVariant) -> None:
        self.db.delete(variant)
        self.db.commit()
        logger.info(f"Variant deleted | variant_id={variant.id}")
