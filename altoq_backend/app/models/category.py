from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, Text, ForeignKey, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class Category(Base):
    __tablename__ = "categories"

    __table_args__ = (
        Index("ix_categories_id", "id"),
        Index("ix_categories_slug", "slug", unique=True),
        Index("idx_parent", "parent_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    icon: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    parent_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL", name="categories_ibfk_1"),
        nullable=True,
    )
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, default=datetime.utcnow)

    # Self-referential relationship (árbol de categorías)
    parent: Mapped[Optional["Category"]] = relationship("Category", remote_side="Category.id", back_populates="children")
    children: Mapped[List["Category"]] = relationship("Category", back_populates="parent")

    # Relationships
    products: Mapped[List["Product"]] = relationship("Product", back_populates="category_rel")
    templates: Mapped[List["ProductTemplate"]] = relationship("ProductTemplate", back_populates="category")
