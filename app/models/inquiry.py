from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM
from app.models.base import Base, TimestampMixin
import enum


class InquiryStatus(str, enum.Enum):
    pending = "pending"
    responded = "responded"
    closed = "closed"


class Inquiry(Base, TimestampMixin):
    __tablename__ = "inquiries"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(Text, nullable=False)
    phone_number = Column(String, nullable=True)
    preferred_contact_time = Column(String, nullable=True)
    status = Column(ENUM(InquiryStatus), nullable=False, default=InquiryStatus.pending, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    property = relationship("Property", back_populates="inquiries")
    user = relationship("User", back_populates="inquiries")
