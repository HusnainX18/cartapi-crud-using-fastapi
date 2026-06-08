from sqlalchemy.orm import Session

from app.core.logger import get_logger
from app.models.user import User

logger = get_logger(__name__)


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, email: str, password_hash: str, name: str) -> User:
        user = User(email=email, password_hash=password_hash, name=name)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        logger.info(f"User created | user_id={user.id} email={email}")
        return user

    def get_user_by_id(self, user_id: int) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def update_user(self, user: User, email: str | None, name: str | None) -> User:
        if email is not None:
            user.email = email
        if name is not None:
            user.name = name
        self.db.commit()
        self.db.refresh(user)
        logger.info(f"User updated | user_id={user.id}")
        return user

    def delete_user(self, user: User) -> None:
        self.db.delete(user)
        self.db.commit()
        logger.info(f"User deleted | user_id={user.id}")
