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
    background_color: Optional[str] = None
    layout_type: Optional[str] = None
    auto_confirm_orders: bool = True
    user_id: Optional[int] = None
    created_at: datetime
    status: str
    rating: Optional[float] = 0.0
    rating_count: Optional[int] = 0
    sales: Optional[int] = 0
    clients: Optional[int] = 0

    class Config:
        from_attributes = True

class StoreStatusUpdate(BaseModel):
    status: str  # 'active', 'pending', or 'suspended'

class StoreUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    owner_name: Optional[str] = None
    phone: Optional[str] = None
    description: Optional[str] = None
    logo: Optional[str] = None
    ruc: Optional[str] = None
    theme: Optional[str] = None
    background_color: Optional[str] = None
    layout_type: Optional[str] = None

class StorePublicResponse(BaseModel):
    """Schema de tienda para uso público (sin datos sensibles)"""
    id: int
    name: str
    owner_name: Optional[str] = None
    phone: Optional[str] = None
    description: Optional[str] = None
    logo: Optional[str] = None
    ruc: Optional[str] = None
    theme: Optional[str] = None
    status: Optional[str] = None
    background_color: Optional[str] = None
    layout_type: Optional[str] = None
    rating: Optional[float] = 0.0
    rating_count: Optional[int] = 0
    sales: Optional[int] = 0

    class Config:
        from_attributes = True
