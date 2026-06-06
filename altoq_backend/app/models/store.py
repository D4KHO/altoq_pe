from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base
import enum

class StoreStatus(str, enum.Enum):
    active = "active"
    pending = "pending"
    suspended = "suspended"

class Store(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)  # Opcional para tiendas de usuarios normales
    owner_name = Column(String(100))
    phone = Column(String(20), nullable=True)
    description = Column(String(500), nullable=True)
    logo = Column(String(255), nullable=True)
    ruc = Column(String(20), nullable=True)  # RUC del vendedor
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)  # Asociación con usuario normal
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum(StoreStatus), default=StoreStatus.pending)

    # Relationships
    user = relationship("User", backref="stores")
    products = relationship("Product", back_populates="store_rel")
