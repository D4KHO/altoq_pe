from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict

class ProductBase(BaseModel):
    name: str
    description: str
    price: float
    image: Optional[str] = None
    category: str
    store_name: Optional[str] = None
    rating: float = 0.0
    rating_count: int = 0
    stock: int = 0
    sales: Optional[int] = 0
    specifications: Optional[Dict[str, str]] = None
    store_id: Optional[int] = None
    category_id: Optional[int] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    image: Optional[str] = None
    category: Optional[str] = None
    stock: Optional[int] = None

class ProductResponse(ProductBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
