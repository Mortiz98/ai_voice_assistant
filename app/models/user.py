from app.models.base import Base, TimestampMixin
from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, ARRAY, JSON, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM
import enum

class UserRole(str, enum.Enum):
    tenant = "tenant"
    owner = "owner"

class User(Base, TimestampMixin):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    phone_number = Column(String, nullable=False, unique=True, index=True)
    role = Column(ENUM(UserRole), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    preferences = Column(JSON, nullable=True)
    
    properties = relationship("Property", back_populates="owner")
    inquiries = relationship("Inquiry", back_populates="user")
    favorites = relationship("PropertyFavorite", back_populates="user")
   