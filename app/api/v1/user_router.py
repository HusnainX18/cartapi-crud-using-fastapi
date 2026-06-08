from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.request import CreateUserRequest, UpdateUserRequest
from app.schemas.response import CartResponse, MessageResponse, UserResponse
from app.services.cart_service import CartService
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


# ------------------------------------------------------------------ #
# POST /users — Register a new user
# ------------------------------------------------------------------ #
@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
def create_user(
    payload: CreateUserRequest,
    db: Session = Depends(get_db),
):
    service = UserService(db)
    return service.create_user(payload)


# ------------------------------------------------------------------ #
# GET /users/{user_id} — Get user profile
# ------------------------------------------------------------------ #
@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID",
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
):
    service = UserService(db)
    return service.get_user(user_id)


# ------------------------------------------------------------------ #
# PATCH /users/{user_id} — Update user profile
# ------------------------------------------------------------------ #
@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update user profile",
)
def update_user(
    user_id: int,
    payload: UpdateUserRequest,
    db: Session = Depends(get_db),
):
    service = UserService(db)
    return service.update_user(user_id, payload)


# ------------------------------------------------------------------ #
# DELETE /users/{user_id} — Delete user
# ------------------------------------------------------------------ #
@router.delete(
    "/{user_id}",
    response_model=MessageResponse,
    summary="Delete user",
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
):
    service = UserService(db)
    return service.delete_user(user_id)


# ------------------------------------------------------------------ #
# GET /users/{user_id}/cart — Get active cart for a user
# ------------------------------------------------------------------ #
@router.get(
    "/{user_id}/cart",
    response_model=CartResponse,
    summary="Get active cart for a user",
)
def get_user_cart(
    user_id: int,
    db: Session = Depends(get_db),
):
    service = CartService(db)
    return service.get_cart_by_user(user_id)
