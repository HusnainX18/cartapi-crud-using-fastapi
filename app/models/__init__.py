# Import all models here so SQLAlchemy Base is aware of them
# This is required for Base.metadata.create_all() to work correctly

from app.models.user import User
from app.models.product import Product
from app.models.product_variant import ProductVariant
from app.models.cart import Cart
from app.models.cart_item import CartItem

__all__ = ["User", "Product", "ProductVariant", "Cart", "CartItem"]