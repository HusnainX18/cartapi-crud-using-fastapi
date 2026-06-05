from sqlalchemy.orm import Session
from app.repositories.product_repository import ProductRepository
from app.schemas.request import (
    CreateProductRequest,
    UpdateProductRequest,
    CreateVariantRequest,
    UpdateVariantRequest,
)
from app.schemas.response import (
    ProductResponse,
    ProductWithVariantsResponse,
    VariantResponse,
    MessageResponse,
)
from app.exceptions.custom_exceptions import (
    ProductNotFoundException,
    ProductVariantNotFoundException,
    SkuAlreadyExistsException,
)
from app.core.logger import get_logger

logger = get_logger(__name__)


class ProductService:

    def __init__(self, db: Session):
        self.repo = ProductRepository(db)

    # ------------------------------------------------------------------ #
    # PRODUCT
    # ------------------------------------------------------------------ #

    def create_product(self, payload: CreateProductRequest) -> ProductResponse:
        product = self.repo.create_product(
            name=payload.name,
            description=payload.description,
            brand=payload.brand,
        )
        return ProductResponse.model_validate(product)

    def get_product(self, product_id: int) -> ProductWithVariantsResponse:
        product = self.repo.get_product_by_id(product_id)
        if not product:
            raise ProductNotFoundException(product_id)
        return ProductWithVariantsResponse.model_validate(product)

    def get_all_products(self) -> list[ProductWithVariantsResponse]:
        products = self.repo.get_all_products()
        return [ProductWithVariantsResponse.model_validate(p) for p in products]

    def update_product(self, product_id: int, payload: UpdateProductRequest) -> ProductResponse:
        product = self.repo.get_product_by_id(product_id)
        if not product:
            raise ProductNotFoundException(product_id)

        product = self.repo.update_product(
            product,
            name=payload.name,
            description=payload.description,
            brand=payload.brand,
        )
        return ProductResponse.model_validate(product)

    def delete_product(self, product_id: int) -> MessageResponse:
        product = self.repo.get_product_by_id(product_id)
        if not product:
            raise ProductNotFoundException(product_id)

        self.repo.delete_product(product)
        return MessageResponse(message=f"Product id={product_id} deleted successfully")

    # ------------------------------------------------------------------ #
    # VARIANT
    # ------------------------------------------------------------------ #

    def create_variant(self, product_id: int, payload: CreateVariantRequest) -> VariantResponse:
        product = self.repo.get_product_by_id(product_id)
        if not product:
            raise ProductNotFoundException(product_id)

        existing = self.repo.get_variant_by_sku(payload.sku)
        if existing:
            raise SkuAlreadyExistsException(payload.sku)

        variant = self.repo.create_variant(
            product_id=product_id,
            sku=payload.sku,
            price=payload.price,
            currency=payload.currency,
            inventory_qty=payload.inventory_qty,
        )
        return VariantResponse.model_validate(variant)

    def get_variant(self, variant_id: int) -> VariantResponse:
        variant = self.repo.get_variant_by_id(variant_id)
        if not variant:
            raise ProductVariantNotFoundException(variant_id)
        return VariantResponse.model_validate(variant)

    def update_variant(
        self, variant_id: int, payload: UpdateVariantRequest
    ) -> VariantResponse:
        variant = self.repo.get_variant_by_id(variant_id)
        if not variant:
            raise ProductVariantNotFoundException(variant_id)

        if payload.sku is not None:
            existing = self.repo.get_variant_by_sku(payload.sku)
            if existing and existing.id != variant_id:
                raise SkuAlreadyExistsException(payload.sku)

        variant = self.repo.update_variant(
            variant,
            sku=payload.sku,
            price=payload.price,
            currency=payload.currency,
            inventory_qty=payload.inventory_qty,
        )
        return VariantResponse.model_validate(variant)

    def delete_variant(self, variant_id: int) -> MessageResponse:
        variant = self.repo.get_variant_by_id(variant_id)
        if not variant:
            raise ProductVariantNotFoundException(variant_id)

        self.repo.delete_variant(variant)
        return MessageResponse(message=f"Variant id={variant_id} deleted successfully")
