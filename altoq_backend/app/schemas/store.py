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
    theme: Optional[str] = "default"
    user_id: Optional[int] = None

class StoreResponse(BaseModel):
    id: int
    name: str
    email: str
    owner_name: Optional[str] = None
    phone: Optional[str] = None
    description: Optional[str] = None
    logo: Optional[str] = None
    ruc: Optional[str] = None
    theme: Optional[str] = None
    user_id: Optional[int] = None
    created_at: datetime
    status: str

    class Config:
        from_attributes = True

class StoreStatusUpdate(BaseModel):
    status: str  # 'active', 'pending', or 'suspended'
