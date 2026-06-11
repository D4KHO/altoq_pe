from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class Chat(Base):
    __tablename__ = "chats"

    __table_args__ = (
        Index("ix_chats_id", "id"),
        Index("ix_chats_buyer_id", "buyer_id"),
        Index("ix_chats_seller_id", "seller_id"),
        Index("ix_chats_product_id", "product_id"),
        Index("ix_chats_order_id", "order_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    buyer_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", name="chats_ibfk_1"),
        nullable=False,
    )
    seller_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", name="chats_ibfk_2"),
        nullable=False,
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", name="chats_ibfk_3"),
        nullable=False,
    )
    order_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("orders.id", name="chats_ibfk_4"),
        nullable=True,
    )
    is_active: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    buyer: Mapped["User"] = relationship("User", foreign_keys=[buyer_id], back_populates="chats_as_buyer")
    seller: Mapped["User"] = relationship("User", foreign_keys=[seller_id], back_populates="chats_as_seller")
    product: Mapped["Product"] = relationship("Product", back_populates="chats")
    order: Mapped[Optional["Order"]] = relationship("Order", back_populates="chats")
    messages: Mapped[List["Message"]] = relationship("Message", back_populates="chat", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    __table_args__ = (
        Index("ix_messages_id", "id"),
        Index("ix_messages_chat_id", "chat_id"),
        Index("ix_messages_sender_id", "sender_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(
        ForeignKey("chats.id", name="messages_ibfk_1"),
        nullable=False,
    )
    sender_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", name="messages_ibfk_2"),
        nullable=False,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    chat: Mapped["Chat"] = relationship("Chat", back_populates="messages")
    sender: Mapped["User"] = relationship("User", back_populates="messages_sent")
