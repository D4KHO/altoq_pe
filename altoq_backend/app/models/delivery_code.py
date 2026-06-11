from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class DeliveryCode(Base):
    __tablename__ = "delivery_codes"

    __table_args__ = (
        Index("ix_delivery_codes_id", "id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", name="delivery_codes_ibfk_1"),
        nullable=False,
        unique=True,  # UNIQUE KEY order_id -> relación 1-a-1 con orders
    )
    code: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)
    is_used: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    used_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="delivery_code")
