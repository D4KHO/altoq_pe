from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class ReviewCreate(BaseModel):
    product_id: int
    order_id: int
    rating: float
    store_rating: float = 5.0
    comment: Optional[str] = None
    image_url: Optional[str] = None

class ReviewResponse(BaseModel):
    id: int
    user_id: int
    user_name: Optional[str] = None
    product_id: int
    store_id: int
    order_id: int
    rating: float
    store_rating: float
    comment: Optional[str] = None
    image_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
