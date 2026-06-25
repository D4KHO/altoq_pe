from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AddressBase(BaseModel):
    name: Optional[str] = None
    street: str
    city: str
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: str = "Peru"
    phone: Optional[str] = None
    is_default: bool = False
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class AddressCreate(AddressBase):
    pass

class AddressUpdate(BaseModel):
    name: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    phone: Optional[str] = None
    is_default: Optional[bool] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class AddressResponse(AddressBase):
    id: int
    user_id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Address(AddressBase):
    id: int
    user_id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
