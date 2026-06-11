from __future__ import annotations

from datetime import datetime
from typing import Optional, Any, List

from sqlalchemy import String, Float, Integer, DateTime, JSON, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class Product(Base):
    __tablename__ = "products"

    __table_args__ = (
        Index("ix_products_id", "id"),
        Index("fk_product_category", "category_id"),
        Index("ix_products_store_id", "store_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    image: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    # Columna legacy de categoría (texto libre); se mantiene por compatibilidad
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    store_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    stock: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=0.0)
    rating_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=0)
    # JSON validado por CHECK (json_valid) en MySQL
    specifications: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    category_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL", name="fk_product_category"),
        nullable=True,
    )
    store_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("stores.id", name="products_ibfk_1"),
        nullable=True,
    )

    # Relationships
    category_rel: Mapped[Optional["Category"]] = relationship("Category", back_populates="products")
    store: Mapped[Optional["Store"]] = relationship("Store", back_populates="products")
    chats: Mapped[List["Chat"]] = relationship("Chat", back_populates="product")
