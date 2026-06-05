from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.cart_service import CartService
from app.schemas.request import CreateCartRequest, AddItemRequest, UpdateItemRequest
from app.schemas.response import MessageResponse, CartResponse

router = APIRouter(prefix="/carts", tags=["Carts"])


def get_cart_service(db: Session = Depends(get_db)) -> CartService:
    return CartService(db)


# ------------------------------------------------------------------ #
# POST /carts — Create a new cart
# ------------------------------------------------------------------ #
@router.post(
    "/",
    response_model=CartResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new cart",
)
def create_cart(
    payload: CreateCartRequest,
    service: CartService = Depends(get_cart_service),
):
    return service.create_cart(payload)


# ------------------------------------------------------------------ #
# GET /carts/{cart_id} — Get cart with all items
# ------------------------------------------------------------------ #
@router.get(
    "/{cart_id}",
    response_model=CartResponse,
    summary="Get cart details with all items",
)
def get_cart(
    cart_id: int,
    service: CartService = Depends(get_cart_service),
):
    return service.get_cart(cart_id)


# ------------------------------------------------------------------ #
# POST /carts/{cart_id}/items — Add item to cart
# ------------------------------------------------------------------ #
@router.post(
    "/{cart_id}/items",
    response_model=CartResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a product variant to cart",
)
def add_item(
    cart_id: int,
    payload: AddItemRequest,
    service: CartService = Depends(get_cart_service),
):
    return service.add_item(cart_id, payload)


# ------------------------------------------------------------------ #
# PATCH /carts/{cart_id}/items/{item_id} — Update item quantity
# ------------------------------------------------------------------ #
@router.patch(
    "/{cart_id}/items/{item_id}",
    response_model=CartResponse,
    summary="Update quantity of a cart item",
)
def update_item(
    cart_id: int,
    item_id: int,
    payload: UpdateItemRequest,
    service: CartService = Depends(get_cart_service),
):
    return service.update_item(cart_id, item_id, payload)


# ------------------------------------------------------------------ #
# DELETE /carts/{cart_id}/items/{item_id} — Remove item from cart
# ------------------------------------------------------------------ #
@router.delete(
    "/{cart_id}/items/{item_id}",
    response_model=MessageResponse,
    summary="Remove an item from cart",
)
def delete_item(
    cart_id: int,
    item_id: int,
    service: CartService = Depends(get_cart_service),
):
    return service.delete_item(cart_id, item_id)


# ------------------------------------------------------------------ #
# DELETE /carts/{cart_id} — Delete entire cart
# ------------------------------------------------------------------ #
@router.delete(
    "/{cart_id}",
    response_model=MessageResponse,
    summary="Delete a cart and all its items",
)
def delete_cart(
    cart_id: int,
    service: CartService = Depends(get_cart_service),
):
    return service.delete_cart(cart_id)


# ------------------------------------------------------------------ #
# POST /carts/{cart_id}/checkout — Checkout cart
# ------------------------------------------------------------------ #
@router.post(
    "/{cart_id}/checkout",
    response_model=CartResponse,
    summary="Checkout cart — decrements inventory and closes cart",
)
def checkout(
    cart_id: int,
    service: CartService = Depends(get_cart_service),
):
    return service.checkout(cart_id)
