from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin

class PropertySearch(Base, TimestampMixin):
    __tablename__ = "property_searches"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    phone_number = Column(String, nullable=True, index=True)
    search_criteria = Column(JSON, nullable=False)
    results_count = Column(Integer, nullable=False, default=0)

    user = relationship("User", foreign_keys=[user_id])

