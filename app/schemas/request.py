from pydantic import BaseModel, Field


class CreateCartRequest(BaseModel):
    user_id: int = Field(..., gt=0, description="ID of the user who owns the cart")
    discount: float = Field(default=0.0, ge=0, description="Discount amount in cart currency")


class AddItemRequest(BaseModel):
    product_variant_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0, description="Must be at least 1")


class UpdateItemRequest(BaseModel):
    quantity: int = Field(..., gt=0, description="New quantity — must be at least 1")


# ------------------------------------------------------------------ #
# USER
# ------------------------------------------------------------------ #


class CreateUserRequest(BaseModel):
    email: str = Field(..., max_length=255, description="User email address")
    password: str = Field(..., min_length=6, max_length=255, description="Plain-text password")
    name: str = Field(..., min_length=1, max_length=100, description="User display name")


class UpdateUserRequest(BaseModel):
    email: str | None = Field(default=None, max_length=255, description="New email")
    name: str | None = Field(default=None, min_length=1, max_length=100, description="New name")


# ------------------------------------------------------------------ #
# PRODUCT
# ------------------------------------------------------------------ #


class CreateProductRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(default=None)
    brand: str | None = Field(default=None, max_length=100)


class UpdateProductRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None)
    brand: str | None = Field(default=None, max_length=100)


class CreateVariantRequest(BaseModel):
    sku: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0)
    currency: str = Field(default="USD", max_length=10)
    inventory_qty: int = Field(default=0, ge=0)


class UpdateVariantRequest(BaseModel):
    sku: str | None = Field(default=None, min_length=1, max_length=100)
    price: float | None = Field(default=None, gt=0)
    currency: str | None = Field(default=None, max_length=10)
    inventory_qty: int | None = Field(default=None, ge=0)
