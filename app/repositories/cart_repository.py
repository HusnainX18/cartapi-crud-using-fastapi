from sqlalchemy.orm import Session, joinedload
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.product_variant import ProductVariant
from app.constants.status import CartStatus
from app.core.logger import get_logger

logger = get_logger(__name__)


class CartRepository:
    """
    SOLID - Single Responsibility Principle:
    This class ONLY handles database operations.
    Business logic lives in CartService, not here.
    """

    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------------------------ #
    # CART CRUD
    # ------------------------------------------------------------------ #

    def create_cart(self, user_id: int, discount: float = 0.0) -> Cart:
        cart = Cart(user_id=user_id, discount=discount, status=CartStatus.ACTIVE)
        self.db.add(cart)
        self.db.commit()
        self.db.refresh(cart)
        logger.info(f"Cart created | cart_id={cart.id} user_id={user_id}")
        return cart

    def get_cart_by_id(self, cart_id: int) -> Cart | None:
        return (
            self.db.query(Cart)
            .options(
                joinedload(Cart.items).joinedload(CartItem.variant).joinedload(
                    ProductVariant.product
                ),
                joinedload(Cart.user),
            )
            .filter(Cart.id == cart_id)
            .first()
        )

    def get_cart_by_user_id(self, user_id: int) -> Cart | None:
        return (
            self.db.query(Cart)
            .options(
                joinedload(Cart.items).joinedload(CartItem.variant).joinedload(
                    ProductVariant.product
                ),
                joinedload(Cart.user),
            )
            .filter(Cart.user_id == user_id, Cart.status == CartStatus.ACTIVE)
            .first()
        )

    def update_cart_status(self, cart: Cart, status: CartStatus) -> Cart:
        cart.status = status
        self.db.commit()
        self.db.refresh(cart)
        logger.info(f"Cart status updated | cart_id={cart.id} status={status}")
        return cart

    def delete_cart(self, cart: Cart) -> None:
        self.db.delete(cart)
        self.db.commit()
        logger.info(f"Cart deleted | cart_id={cart.id}")

    # ------------------------------------------------------------------ #
    # CART ITEM CRUD
    # ------------------------------------------------------------------ #

    def get_item_by_id(self, item_id: int, cart_id: int) -> CartItem | None:
        return (
            self.db.query(CartItem)
            .filter(CartItem.id == item_id, CartItem.cart_id == cart_id)
            .first()
        )

    def get_item_by_variant(self, cart_id: int, variant_id: int) -> CartItem | None:
        return (
            self.db.query(CartItem)
            .filter(
                CartItem.cart_id == cart_id,
                CartItem.product_variant_id == variant_id,
            )
            .first()
        )

    def add_item(
        self,
        cart_id: int,
        variant_id: int,
        quantity: int,
        unit_price: float,
        currency: str,
    ) -> CartItem:
        item = CartItem(
            cart_id=cart_id,
            product_variant_id=variant_id,
            quantity=quantity,
            unit_price=unit_price,
            currency=currency,
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        logger.info(f"Item added | cart_id={cart_id} variant_id={variant_id} qty={quantity}")
        return item

    def update_item_quantity(self, item: CartItem, quantity: int) -> CartItem:
        item.quantity = quantity
        self.db.commit()
        self.db.refresh(item)
        logger.info(f"Item updated | item_id={item.id} new_qty={quantity}")
        return item

    def delete_item(self, item: CartItem) -> None:
        self.db.delete(item)
        self.db.commit()
        logger.info(f"Item deleted | item_id={item.id}")

    # ------------------------------------------------------------------ #
    # VARIANT LOOKUP (used during inventory validation in service)
    # ------------------------------------------------------------------ #

    def get_variant_by_id(self, variant_id: int) -> ProductVariant | None:
        return (
            self.db.query(ProductVariant)
            .options(joinedload(ProductVariant.product))
            .filter(ProductVariant.id == variant_id)
            .first()
        )

    def decrement_inventory(self, variant: ProductVariant, quantity: int) -> None:
        variant.inventory_qty -= quantity
        self.db.commit()
        logger.info(f"Inventory decremented | variant_id={variant.id} by={quantity}")