from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class StoreCreate(BaseModel):
    name: str
    email: EmailStr
    owner_name: Optional[str] = None
    phone: Optional[str] = None
    description: Optional[str] = None
    logo: Optional[str] = None
    ruc: Optional[str] = None
    user_id: Optional[int] = None

class StoreResponse(BaseModel):
    id: int
    name: str
    email: str
    owner_name: Optional[str]
    phone: Optional[str]
    description: Optional[str]
    logo: Optional[str]
    ruc: Optional[str]
    user_id: Optional[int]
    created_at: datetime
    status: str

    class Config:
        from_attributes = True

class StoreStatusUpdate(BaseModel):
    status: str  # 'active', 'pending', or 'suspended'
