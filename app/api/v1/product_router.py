from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.product_service import ProductService
from app.schemas.request import (
    CreateProductRequest,
    UpdateProductRequest,
    CreateVariantRequest,
    UpdateVariantRequest,
)
from app.schemas.response import (
    MessageResponse,
    ProductResponse,
    ProductWithVariantsResponse,
    VariantResponse,
)

router = APIRouter(prefix="/products", tags=["Products"])


def get_product_service(db: Session = Depends(get_db)) -> ProductService:
    return ProductService(db)


# ------------------------------------------------------------------ #
# POST /products — Create a product
# ------------------------------------------------------------------ #
@router.post(
    "/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new product",
)
def create_product(
    payload: CreateProductRequest,
    service: ProductService = Depends(get_product_service),
):
    return service.create_product(payload)


# ------------------------------------------------------------------ #
# GET /products — List all products
# ------------------------------------------------------------------ #
@router.get(
    "/",
    response_model=list[ProductWithVariantsResponse],
    summary="List all products with variants",
)
def list_products(
    service: ProductService = Depends(get_product_service),
):
    return service.get_all_products()


# ------------------------------------------------------------------ #
# GET /products/{product_id} — Get product with variants
# ------------------------------------------------------------------ #
@router.get(
    "/{product_id}",
    response_model=ProductWithVariantsResponse,
    summary="Get product by ID with variants",
)
def get_product(
    product_id: int,
    service: ProductService = Depends(get_product_service),
):
    return service.get_product(product_id)


# ------------------------------------------------------------------ #
# PATCH /products/{product_id} — Update product
# ------------------------------------------------------------------ #
@router.patch(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Update product details",
)
def update_product(
    product_id: int,
    payload: UpdateProductRequest,
    service: ProductService = Depends(get_product_service),
):
    return service.update_product(product_id, payload)


# ------------------------------------------------------------------ #
# DELETE /products/{product_id} — Delete product (cascades variants)
# ------------------------------------------------------------------ #
@router.delete(
    "/{product_id}",
    response_model=MessageResponse,
    summary="Delete product and all its variants",
)
def delete_product(
    product_id: int,
    service: ProductService = Depends(get_product_service),
):
    return service.delete_product(product_id)


# ------------------------------------------------------------------ #
# POST /products/{product_id}/variants — Add variant to product
# ------------------------------------------------------------------ #
@router.post(
    "/{product_id}/variants",
    response_model=VariantResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a variant to a product",
)
def create_variant(
    product_id: int,
    payload: CreateVariantRequest,
    service: ProductService = Depends(get_product_service),
):
    return service.create_variant(product_id, payload)


# ------------------------------------------------------------------ #
# GET /variants/{variant_id} — Get a single variant
# ------------------------------------------------------------------ #
@router.get(
    "/variants/{variant_id}",
    response_model=VariantResponse,
    summary="Get a variant by ID",
)
def get_variant(
    variant_id: int,
    service: ProductService = Depends(get_product_service),
):
    return service.get_variant(variant_id)


# ------------------------------------------------------------------ #
# PATCH /variants/{variant_id} — Update variant
# ------------------------------------------------------------------ #
@router.patch(
    "/variants/{variant_id}",
    response_model=VariantResponse,
    summary="Update variant details",
)
def update_variant(
    variant_id: int,
    payload: UpdateVariantRequest,
    service: ProductService = Depends(get_product_service),
):
    return service.update_variant(variant_id, payload)


# ------------------------------------------------------------------ #
# DELETE /variants/{variant_id} — Delete variant
# ------------------------------------------------------------------ #
@router.delete(
    "/variants/{variant_id}",
    response_model=MessageResponse,
    summary="Delete a variant",
)
def delete_variant(
    variant_id: int,
    service: ProductService = Depends(get_product_service),
):
    return service.delete_variant(variant_id)
