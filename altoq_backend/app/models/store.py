from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, DateTime, Enum, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class Store(Base):
    __tablename__ = "stores"

    __table_args__ = (
        Index("ix_stores_id", "id"),
        Index("ix_stores_email", "email", unique=True),
        Index("idx_status", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    password_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    owner_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    logo: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, default=datetime.utcnow)
    status: Mapped[Optional[str]] = mapped_column(
        Enum("active", "pending", "suspended", name="store_status"),
        nullable=True,
        default="pending",
    )
    ruc: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    theme: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, default="default")
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)

    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="stores")
    products: Mapped[List["Product"]] = relationship("Product", back_populates="store")
    metrics: Mapped[List["StoreMetric"]] = relationship("StoreMetric", back_populates="store")
