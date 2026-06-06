from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from ..database import Base

class UserRole(str, Enum):
    BUYER = "BUYER"
    SELLER = "SELLER"
    BOTH = "BOTH"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    password = Column(String(255), nullable=False)
    address = Column(String(255), nullable=True)  # Deprecated, use addresses table
    phone = Column(String(20), nullable=True)
    role = Column(SQLEnum(UserRole), default=UserRole.BUYER, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    addresses = relationship("Address", back_populates="user", cascade="all, delete-orphan")
