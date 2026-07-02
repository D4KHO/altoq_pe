from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class InquiryCreate(BaseModel):
    store_id: int
    name: str
    email: str
    phone: Optional[str] = None
    message: str


class InquiryResponse(BaseModel):
    id: int
    store_id: int
    name: str
    email: str
    phone: Optional[str] = None
    message: str
    is_read: Optional[bool] = False
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
