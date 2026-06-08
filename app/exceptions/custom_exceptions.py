class CartNotFoundException(Exception):
    def __init__(self, cart_id: int):
        self.message = f"Cart with id={cart_id} not found"
        super().__init__(self.message)


class CartItemNotFoundException(Exception):
    def __init__(self, item_id: int):
        self.message = f"Cart item with id={item_id} not found"
        super().__init__(self.message)


class ProductVariantNotFoundException(Exception):
    def __init__(self, variant_id: int):
        self.message = f"Product variant with id={variant_id} not found"
        super().__init__(self.message)


class InsufficientInventoryException(Exception):
    def __init__(self, sku: str, available: int, requested: int):
        self.message = (
            f"Insufficient inventory for SKU={sku}. Available={available}, Requested={requested}"
        )
        super().__init__(self.message)


class ItemAlreadyInCartException(Exception):
    def __init__(self, variant_id: int):
        self.message = (
            f"Variant id={variant_id} is already in the cart. Use PATCH to update quantity."
        )
        super().__init__(self.message)


class CartNotActiveException(Exception):
    def __init__(self, cart_id: int, status: str):
        self.message = f"Cart id={cart_id} is not active. Current status: {status}"
        super().__init__(self.message)


class UserNotFoundException(Exception):
    def __init__(self, user_id: int):
        self.message = f"User with id={user_id} not found"
        super().__init__(self.message)


class EmailAlreadyExistsException(Exception):
    def __init__(self, email: str):
        self.message = f"User with email={email} already exists"
        super().__init__(self.message)


class ProductNotFoundException(Exception):
    def __init__(self, product_id: int):
        self.message = f"Product with id={product_id} not found"
        super().__init__(self.message)


class SkuAlreadyExistsException(Exception):
    def __init__(self, sku: str):
        self.message = f"Variant with SKU={sku} already exists"
        super().__init__(self.message)


class EmptyCartException(Exception):
    def __init__(self, cart_id: int):
        self.message = f"Cart id={cart_id} is empty. Add items before checkout."
        super().__init__(self.message)
