from __future__ import annotations

from datetime import datetime
from typing import Optional, Any, List

from sqlalchemy import String, Float, DateTime, JSON, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class Order(Base):
    __tablename__ = "orders"

    __table_args__ = (
        Index("ix_orders_id", "id"),
        Index("ix_orders_user_id", "user_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", name="orders_ibfk_1"),
        nullable=False,
    )
    # Campo JSON con CHECK json_valid en MySQL; se mapea como JSON
    products: Mapped[Any] = mapped_column(JSON, nullable=False)
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    shipping_address: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    contact_phone: Mapped[str] = mapped_column(String(20), nullable=False, default="")

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="orders")
    chats: Mapped[List["Chat"]] = relationship("Chat", back_populates="order")
    delivery_code: Mapped[Optional["DeliveryCode"]] = relationship("DeliveryCode", back_populates="order", uselist=False)
