from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM
from app.models.base import Base, TimestampMixin
from app.models.user import UserRole
import enum

class CallSessionStatus(str, enum.Enum):
    active = "active"
    completed = "completed"
    abandoned = "abandoned"

class CallSession(Base, TimestampMixin):
    __tablename__ = "call_sessions"

    id = Column(Integer, primary_key=True, index=True)
    call_sid = Column(String, nullable=False, unique=True, index=True)
    phone_number = Column(String, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    role = Column(ENUM(UserRole), nullable=True)
    status = Column(ENUM(CallSessionStatus), nullable=False, default=CallSessionStatus.active, index=True)
    current_step = Column(String, nullable=True)
    context_data = Column(JSON, nullable=True)

    user = relationship("User", foreign_keys=[user_id])

