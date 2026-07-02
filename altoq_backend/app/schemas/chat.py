from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ChatForOrderCreate(BaseModel):
    seller_id: Optional[int] = None
    product_id: int
    order_id: int


class ChatCreate(BaseModel):
    seller_id: int
    product_id: int

class ChatResponse(BaseModel):
    id: int
    buyer_id: int
    seller_id: int
    product_id: Optional[int] = None
    order_id: Optional[int]
    is_active: Optional[bool] = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    buyer_name: Optional[str] = None
    seller_name: Optional[str] = None
    product_name: Optional[str] = None
    product_image: Optional[str] = None

    class Config:
        from_attributes = True

class MessageCreate(BaseModel):
    content: str

class MessageResponse(BaseModel):
    id: int
    chat_id: int
    sender_id: int
    content: str
    is_read: Optional[bool] = False
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
