from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class User(Base):
    __tablename__ = "users"

    __table_args__ = (
        Index("ix_users_id", "id"),
        Index("ix_users_email", "email", unique=True),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    role: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, default="buyer")

    # Relationships
    addresses: Mapped[List["Address"]] = relationship("Address", back_populates="user", cascade="all, delete-orphan")
    stores: Mapped[List["Store"]] = relationship("Store", back_populates="user")
    orders: Mapped[List["Order"]] = relationship("Order", back_populates="user")
    chats_as_buyer: Mapped[List["Chat"]] = relationship("Chat", foreign_keys="Chat.buyer_id", back_populates="buyer")
    chats_as_seller: Mapped[List["Chat"]] = relationship("Chat", foreign_keys="Chat.seller_id", back_populates="seller")
    messages_sent: Mapped[List["Message"]] = relationship("Message", back_populates="sender")

    @property
    def has_store(self) -> bool:
        """Returns True if the user has at least one registered store."""
        return len(self.stores) > 0
