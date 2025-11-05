from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin

class Inquiry(Base, TimestampMixin):
    __tablename__ = "inquiries"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(String, nullable=False)
    property_id = Column(Integer, ForeignKey("properties.id"))

    property = relationship("Property", back_populates="inquiries")
