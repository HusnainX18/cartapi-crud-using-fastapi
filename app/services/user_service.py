from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.schemas.request import CreateUserRequest, UpdateUserRequest
from app.schemas.response import UserResponse, MessageResponse
from app.exceptions.custom_exceptions import (
    UserNotFoundException,
    EmailAlreadyExistsException,
)
from app.core.logger import get_logger

import hashlib

logger = get_logger(__name__)


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


class UserService:

    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def create_user(self, payload: CreateUserRequest) -> UserResponse:
        existing = self.repo.get_user_by_email(payload.email)
        if existing:
            raise EmailAlreadyExistsException(payload.email)

        password_hash = _hash_password(payload.password)
        user = self.repo.create_user(
            email=payload.email,
            password_hash=password_hash,
            name=payload.name,
        )
        return UserResponse.model_validate(user)

    def get_user(self, user_id: int) -> UserResponse:
        user = self.repo.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundException(user_id)
        return UserResponse.model_validate(user)

    def update_user(self, user_id: int, payload: UpdateUserRequest) -> UserResponse:
        user = self.repo.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundException(user_id)

        if payload.email is not None:
            existing = self.repo.get_user_by_email(payload.email)
            if existing and existing.id != user_id:
                raise EmailAlreadyExistsException(payload.email)

        user = self.repo.update_user(user, email=payload.email, name=payload.name)
        return UserResponse.model_validate(user)

    def delete_user(self, user_id: int) -> MessageResponse:
        user = self.repo.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundException(user_id)

        self.repo.delete_user(user)
        return MessageResponse(message=f"User id={user_id} deleted successfully")
