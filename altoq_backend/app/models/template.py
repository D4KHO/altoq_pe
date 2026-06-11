from __future__ import annotations

from datetime import datetime
from typing import Optional, Any, List

from sqlalchemy import String, Text, Integer, Boolean, DateTime, JSON, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class ProductTemplate(Base):
    __tablename__ = "product_templates"

    __table_args__ = (
        Index("ix_product_templates_id", "id"),
        Index("ix_product_templates_category_id", "category_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", name="product_templates_ibfk_1"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # JSON validado por CHECK (json_valid) en MySQL
    keywords: Mapped[Any] = mapped_column(JSON, nullable=False)
    fields: Mapped[Any] = mapped_column(JSON, nullable=False)
    is_active: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    category: Mapped["Category"] = relationship("Category", back_populates="templates")
    template_fields: Mapped[List["TemplateField"]] = relationship(
        "TemplateField", back_populates="template", cascade="all, delete-orphan"
    )


class TemplateField(Base):
    __tablename__ = "template_fields"

    __table_args__ = (
        Index("ix_template_fields_id", "id"),
        Index("ix_template_fields_template_id", "template_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    template_id: Mapped[int] = mapped_column(
        ForeignKey("product_templates.id", name="template_fields_ibfk_1"),
        nullable=False,
    )
    field_name: Mapped[str] = mapped_column(String(50), nullable=False)
    field_label: Mapped[str] = mapped_column(String(100), nullable=False)
    field_type: Mapped[str] = mapped_column(String(20), nullable=False)
    # JSON validado por CHECK (json_valid) en MySQL
    options: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    is_required: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    placeholder: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    validation_regex: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    order: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Relationships
    template: Mapped["ProductTemplate"] = relationship("ProductTemplate", back_populates="template_fields")
