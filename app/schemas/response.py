from pydantic import BaseModel, computed_field
from app.constants.status import CartStatus


class CartItemResponse(BaseModel):
    id: int
    product_variant_id: int
    product_name: str
    sku: str
    quantity: int
    unit_price: float
    currency: str

    @computed_field
    @property
    def line_total(self) -> float:
        return round(self.quantity * self.unit_price, 2)

    model_config = {"from_attributes": True}


class CartResponse(BaseModel):
    id: int
    user_id: int | None
    customer_name: str | None
    discount: float
    status: CartStatus
    items: list[CartItemResponse] = []

    @computed_field
    @property
    def subtotal(self) -> float:
        return round(sum(item.line_total for item in self.items), 2)

    @computed_field
    @property
    def total(self) -> float:
        return round(max(self.subtotal - self.discount, 0), 2)

    model_config = {"from_attributes": True}


class MessageResponse(BaseModel):
    msg: str


# ------------------------------------------------------------------ #
# USER
# ------------------------------------------------------------------ #

class UserResponse(BaseModel):
    id: int
    email: str
    name: str

    model_config = {"from_attributes": True}


# ------------------------------------------------------------------ #
# PRODUCT
# ------------------------------------------------------------------ #

class VariantResponse(BaseModel):
    id: int
    product_id: int
    sku: str
    price: float
    currency: str
    inventory_qty: int

    model_config = {"from_attributes": True}


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str | None
    brand: str | None

    model_config = {"from_attributes": True}


class ProductWithVariantsResponse(ProductResponse):
    variants: list[VariantResponse] = []