from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import Date, DateTime, Float, Integer, Numeric, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from decimal import Decimal

from ..database import Base


class StoreMetric(Base):
    __tablename__ = "store_metrics"

    __table_args__ = (
        Index("ix_store_metrics_id", "id"),
        Index("ix_store_metrics_store_id", "store_id"),
        Index("ix_store_metrics_date", "date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    store_id: Mapped[int] = mapped_column(
        ForeignKey("stores.id", name="store_metrics_ibfk_1"),
        nullable=False,
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)
    visits: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    products_published: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    orders_delivered: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    revenue: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    chat_sessions: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    template_usage: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    new_users: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    avg_rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    store: Mapped["Store"] = relationship("Store", back_populates="metrics")
