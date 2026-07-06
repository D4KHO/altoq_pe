from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Float, ForeignKey, Index, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class Review(Base):
    __tablename__ = "reviews"

    __table_args__ = (
        Index("ix_reviews_id", "id"),
        Index("ix_reviews_user_id", "user_id"),
        Index("ix_reviews_product_id", "product_id"),
        Index("ix_reviews_store_id", "store_id"),
        Index("ix_reviews_order_id", "order_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", name="reviews_ibfk_1"),
        nullable=False,
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", name="reviews_ibfk_2"),
        nullable=False,
    )
    store_id: Mapped[int] = mapped_column(
        ForeignKey("stores.id", name="reviews_ibfk_3"),
        nullable=False,
    )
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", name="reviews_ibfk_4"),
        nullable=False,
    )
    rating: Mapped[float] = mapped_column(Float, nullable=False)
    store_rating: Mapped[float] = mapped_column(Float, nullable=False, default=5.0)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    image_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, default=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    product: Mapped["Product"] = relationship("Product", foreign_keys=[product_id])
    store: Mapped["Store"] = relationship("Store", foreign_keys=[store_id])
    order: Mapped["Order"] = relationship("Order", foreign_keys=[order_id])
