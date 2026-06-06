from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class AdminCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class AdminLogin(BaseModel):
    username: str
    password: str

class AdminResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True

class AdminToken(BaseModel):
    access_token: str
    token_type: str = "bearer"
    admin: AdminResponse
