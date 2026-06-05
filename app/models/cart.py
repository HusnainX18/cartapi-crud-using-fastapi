from sqlalchemy import Integer, Numeric, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from app.constants.status import CartStatus


class Cart(Base):
    __tablename__ = "carts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    discount: Mapped[float] = mapped_column(Numeric(10, 2), default=0)

    # Mentor requirement: track cart lifecycle
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=CartStatus.ACTIVE
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="carts")
    items: Mapped[list["CartItem"]] = relationship(
        "CartItem", back_populates="cart", cascade="all, delete"
    )