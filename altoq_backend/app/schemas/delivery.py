from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class DeliveryCodeResponse(BaseModel):
    id: int
    order_id: int
    code: str
    is_used: bool
    used_at: Optional[datetime]
    expires_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

class DeliveryValidation(BaseModel):
    code: str
