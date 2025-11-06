from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr
from app.models.user import UserRole
from app.schemas.common import TimestampSchema

class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone_number: str
    role: UserRole

class UserCreate(UserBase):
    preferences: Optional[Dict[str, Any]] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase, TimestampSchema):
    id: int
    is_active: bool
    preferences: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class UserByPhone(BaseModel):
    id: int
    name: str
    phone_number: str
    role: UserRole
    is_active: bool

    class Config:
        from_attributes = True

