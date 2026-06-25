from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class DeliveryCodeResponse(BaseModel):
    id: int
    order_id: int
    code: str
    is_used: Optional[bool] = False
    used_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class DeliveryValidation(BaseModel):
    code: str
    order_id: Optional[int] = None

class DeliveryLocationUpdate(BaseModel):
    latitude: float
    longitude: float

class DeliveryStart(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class DeliveryTrackingResponse(BaseModel):
    order_id: int
    total_amount: float
    shipping_address: str
    shipping_latitude: Optional[float] = None
    shipping_longitude: Optional[float] = None
    delivery_latitude: Optional[float] = None
    delivery_longitude: Optional[float] = None
    delivery_status: Optional[str] = None
    client_name: Optional[str] = None
    contact_phone: Optional[str] = None
    store_name: Optional[str] = None
    products: Optional[list] = None

    class Config:
        from_attributes = True
