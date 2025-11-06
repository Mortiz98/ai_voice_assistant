from typing import Optional, Dict, Any
from pydantic import BaseModel
from app.models.call_session import CallSessionStatus
from app.models.user import UserRole
from app.schemas.common import TimestampSchema

class CallSessionBase(BaseModel):
    call_sid: str
    phone_number: str
    role: Optional[UserRole] = None

class CallSessionCreate(CallSessionBase):
    pass

class CallSessionUpdate(BaseModel):
    status: Optional[CallSessionStatus] = None
    current_step: Optional[str] = None
    context_data: Optional[Dict[str, Any]] = None
    user_id: Optional[int] = None
    role: Optional[UserRole] = None

class CallSessionResponse(CallSessionBase, TimestampSchema):
    id: int
    user_id: Optional[int] = None
    status: CallSessionStatus
    current_step: Optional[str] = None
    context_data: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

