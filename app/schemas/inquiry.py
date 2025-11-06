from typing import Optional
from pydantic import BaseModel
from app.models.inquiry import InquiryStatus
from app.schemas.common import TimestampSchema
from app.schemas.property import PropertySummary
from app.schemas.user import UserResponse

class InquiryBase(BaseModel):
    message: str
    phone_number: Optional[str] = None
    preferred_contact_time: Optional[str] = None

class InquiryCreate(InquiryBase):
    property_id: int
    user_id: Optional[int] = None

class InquiryUpdate(BaseModel):
    status: Optional[InquiryStatus] = None
    message: Optional[str] = None

class InquiryResponse(InquiryBase, TimestampSchema):
    id: int
    status: InquiryStatus
    property_id: int
    user_id: Optional[int] = None
    property: Optional[PropertySummary] = None
    user: Optional[UserResponse] = None

    class Config:
        from_attributes = True

