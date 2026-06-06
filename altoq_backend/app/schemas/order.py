from pydantic import BaseModel
from datetime import datetime
from typing import List

class OrderItem(BaseModel):
    productId: int
    quantity: int
    price: float

class OrderBase(BaseModel):
    user_id: int
    products: List[OrderItem]
    total_amount: float
    status: str = "pending"

class OrderCreate(OrderBase):
    pass

class OrderResponse(OrderBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Order(OrderBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
