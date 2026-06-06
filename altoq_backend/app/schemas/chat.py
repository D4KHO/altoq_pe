from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ChatCreate(BaseModel):
    seller_id: int
    product_id: int

class ChatResponse(BaseModel):
    id: int
    buyer_id: int
    seller_id: int
    product_id: int
    order_id: Optional[int]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class MessageCreate(BaseModel):
    content: str

class MessageResponse(BaseModel):
    id: int
    chat_id: int
    sender_id: int
    content: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True
