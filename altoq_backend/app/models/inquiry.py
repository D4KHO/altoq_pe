from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class StoreInquiry(Base):
    """Consultas generales enviadas por visitantes desde el formulario de Contacto."""

    __tablename__ = "store_inquiries"

    __table_args__ = (
        Index("ix_store_inquiries_id", "id"),
        Index("ix_store_inquiries_store_id", "store_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    store_id: Mapped[int] = mapped_column(
        ForeignKey("stores.id", name="store_inquiries_ibfk_1"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True, default=False)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, default=datetime.utcnow
    )

    # Relationships
    store: Mapped["Store"] = relationship("Store", back_populates="inquiries")
