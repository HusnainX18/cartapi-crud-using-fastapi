from sqlalchemy.orm import Session
from app.repositories.cart_repository import CartRepository
from app.schemas.request import CreateCartRequest, AddItemRequest, UpdateItemRequest
from app.schemas.response import CartResponse, CartItemResponse, MessageResponse
from app.exceptions.custom_exceptions import (
    CartNotFoundException,
    CartItemNotFoundException,
    ProductVariantNotFoundException,
    InsufficientInventoryException,
    ItemAlreadyInCartException,
    CartNotActiveException,
)
from app.constants.status import CartStatus
from app.core.logger import get_logger

logger = get_logger(__name__)


def _build_cart_response(cart) -> CartResponse:
    """
    Maps SQLAlchemy Cart ORM object → CartResponse Pydantic model.
    Kept as a private helper to avoid repeating this mapping in every method.
    """
    items = []
    for item in cart.items:
        items.append(
            CartItemResponse(
                id=item.id,
                product_variant_id=item.product_variant_id,
                product_name=item.variant.product.name,
                sku=item.variant.sku,
                quantity=item.quantity,
                unit_price=float(item.unit_price),
                currency=item.currency,
            )
        )

    return CartResponse(
        id=cart.id,
        user_id=cart.user_id,
        customer_name=cart.user.name if cart.user else None,
        discount=float(cart.discount),
        status=cart.status,
        items=items,
    )


class CartService:
    """
    SOLID - Single Responsibility: handles business rules only.
    SOLID - Dependency Inversion: depends on CartRepository abstraction, not DB directly.
    """

    def __init__(self, db: Session):
        self.repo = CartRepository(db)

    # ------------------------------------------------------------------ #
    # CREATE CART
    # ------------------------------------------------------------------ #

    def create_cart(self, payload: CreateCartRequest) -> CartResponse:
        logger.info(f"Creating cart for user_id={payload.user_id}")
        cart = self.repo.create_cart(
            user_id=payload.user_id, discount=payload.discount
        )
        # Reload with relationships
        cart = self.repo.get_cart_by_id(cart.id)
        return _build_cart_response(cart)

    # ------------------------------------------------------------------ #
    # GET CART
    # ------------------------------------------------------------------ #

    def get_cart(self, cart_id: int) -> CartResponse:
        cart = self.repo.get_cart_by_id(cart_id)
        if not cart:
            raise CartNotFoundException(cart_id)
        return _build_cart_response(cart)

    def get_cart_by_user(self, user_id: int) -> CartResponse:
        cart = self.repo.get_cart_by_user_id(user_id)
        if not cart:
            raise CartNotFoundException(user_id)
        return _build_cart_response(cart)

    # ------------------------------------------------------------------ #
    # ADD ITEM
    # ------------------------------------------------------------------ #

    def add_item(self, cart_id: int, payload: AddItemRequest) -> CartResponse:
        # 1. Cart must exist
        cart = self.repo.get_cart_by_id(cart_id)
        if not cart:
            raise CartNotFoundException(cart_id)

        # 2. Cart must be ACTIVE — can't add items to checked out cart
        if cart.status != CartStatus.ACTIVE:
            raise CartNotActiveException(cart_id, cart.status)

        # 3. Variant must exist
        variant = self.repo.get_variant_by_id(payload.product_variant_id)
        if not variant:
            raise ProductVariantNotFoundException(payload.product_variant_id)

        # 4. No duplicate items — use PATCH to update quantity
        existing = self.repo.get_item_by_variant(cart_id, payload.product_variant_id)
        if existing:
            raise ItemAlreadyInCartException(payload.product_variant_id)

        # 5. Inventory check
        if variant.inventory_qty < payload.quantity:
            raise InsufficientInventoryException(
                variant.sku, variant.inventory_qty, payload.quantity
            )

        self.repo.add_item(
            cart_id=cart_id,
            variant_id=payload.product_variant_id,
            quantity=payload.quantity,
            unit_price=float(variant.price),
            currency=variant.currency,
        )

        cart = self.repo.get_cart_by_id(cart_id)
        return _build_cart_response(cart)

    # ------------------------------------------------------------------ #
    # UPDATE ITEM QUANTITY
    # ------------------------------------------------------------------ #

    def update_item(
        self, cart_id: int, item_id: int, payload: UpdateItemRequest
    ) -> CartResponse:
        cart = self.repo.get_cart_by_id(cart_id)
        if not cart:
            raise CartNotFoundException(cart_id)

        if cart.status != CartStatus.ACTIVE:
            raise CartNotActiveException(cart_id, cart.status)

        item = self.repo.get_item_by_id(item_id, cart_id)
        if not item:
            raise CartItemNotFoundException(item_id)

        # Re-check inventory against new quantity
        variant = self.repo.get_variant_by_id(item.product_variant_id)
        if variant.inventory_qty < payload.quantity:
            raise InsufficientInventoryException(
                variant.sku, variant.inventory_qty, payload.quantity
            )

        self.repo.update_item_quantity(item, payload.quantity)
        cart = self.repo.get_cart_by_id(cart_id)
        return _build_cart_response(cart)

    # ------------------------------------------------------------------ #
    # DELETE ITEM
    # ------------------------------------------------------------------ #

    def delete_item(self, cart_id: int, item_id: int) -> MessageResponse:
        cart = self.repo.get_cart_by_id(cart_id)
        if not cart:
            raise CartNotFoundException(cart_id)

        item = self.repo.get_item_by_id(item_id, cart_id)
        if not item:
            raise CartItemNotFoundException(item_id)

        self.repo.delete_item(item)
        return MessageResponse(message="Item removed from cart", cart_id=cart_id)

    # ------------------------------------------------------------------ #
    # DELETE CART
    # ------------------------------------------------------------------ #

    def delete_cart(self, cart_id: int) -> MessageResponse:
        cart = self.repo.get_cart_by_id(cart_id)
        if not cart:
            raise CartNotFoundException(cart_id)

        self.repo.delete_cart(cart)
        return MessageResponse(message="Cart deleted successfully", cart_id=cart_id)

    # ------------------------------------------------------------------ #
    # CHECKOUT
    # ------------------------------------------------------------------ #

    def checkout(self, cart_id: int) -> MessageResponse:
        cart = self.repo.get_cart_by_id(cart_id)
        if not cart:
            raise CartNotFoundException(cart_id)

        if cart.status != CartStatus.ACTIVE:
            raise CartNotActiveException(cart_id, cart.status)

        if not cart.items:
            raise ValueError("Cannot checkout an empty cart")

        # Validate inventory for ALL items before decrementing any
        for item in cart.items:
            variant = self.repo.get_variant_by_id(item.product_variant_id)
            if variant.inventory_qty < item.quantity:
                raise InsufficientInventoryException(
                    variant.sku, variant.inventory_qty, item.quantity
                )

        # All checks passed — now decrement inventory
        for item in cart.items:
            variant = self.repo.get_variant_by_id(item.product_variant_id)
            self.repo.decrement_inventory(variant, item.quantity)

        # Mark cart as checked out
        self.repo.update_cart_status(cart, CartStatus.CHECKED_OUT)
        logger.info(f"Cart checked out | cart_id={cart_id}")

        return MessageResponse(
            message="Checkout successful. Cart is now closed.", cart_id=cart_id
        )