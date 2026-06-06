from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum

class UserRole(str, Enum):
    BUYER = "BUYER"
    SELLER = "SELLER"
    BOTH = "BOTH"

class UserBase(BaseModel):
    email: str
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    role: UserRole = UserRole.BUYER

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None  # Deprecated field
    role: Optional[UserRole] = None

class PasswordChange(BaseModel):
    old_password: str
    new_password: str

class UserLogin(BaseModel):
    email: str
    password: str

class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Alias for admin routes
UserResponse = User

class Token(BaseModel):
    token: str
    user: User
