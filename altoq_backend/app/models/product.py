from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=False)
    price = Column(Float, nullable=False)
    image = Column(String(255), nullable=True)
    category = Column(String(50), nullable=False)  # Keep for backward compatibility
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    store_name = Column(String(100), nullable=True)
    store_id = Column(Integer, ForeignKey('stores.id'), nullable=True)
    rating = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)
    stock = Column(Integer, default=0)
    specifications = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    category_rel = relationship("Category", back_populates="products")
    store_rel = relationship("Store", back_populates="products")
