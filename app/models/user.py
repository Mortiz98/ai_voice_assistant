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
    email = Column(String, nullable=False,unique=True, index=True)
    role = Column(Enum(UserRole), nullable=False)
    properties = relationship("Property", back_populates="owner")