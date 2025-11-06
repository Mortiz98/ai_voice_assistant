from sqlalchemy import Column, Integer, String, ForeignKey, Float, Boolean, Text, JSON, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM
from app.models.base import Base, TimestampMixin
import enum


class PropertyType(str, enum.Enum):
    apartment = "apartment"
    house = "house"
    studio = "studio"
    townhouse = "townhouse"
    condo = "condo"

class PropertyStatus(str, enum.Enum):
    available = "available"
    rented = "rented"
    unavailable = "unavailable"

class Property(Base, TimestampMixin):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    address = Column(String, nullable=False)
    city = Column(String, nullable=False, index=True)
    neighborhood = Column(String, nullable=True, index=True)
    zip_code = Column(String, nullable=True)
    property_type = Column(ENUM(PropertyType), nullable=False)
    bedrooms = Column(Integer, nullable=False)
    bathrooms = Column(Integer, nullable=False)
    square_meters = Column(Float, nullable=True)
    price = Column(Integer, nullable=False, index=True)
    deposit = Column(Integer, nullable=True)
    status = Column(ENUM(PropertyStatus), nullable=False, default=PropertyStatus.available, index=True)
    pet_friendly = Column(Boolean, default=False, nullable=False)
    furnished = Column(Boolean, default=False, nullable=False)
    amenities = Column(JSON, nullable=True)
    images = Column(ARRAY(String), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="properties")
    inquiries = relationship("Inquiry", back_populates="property")
    favorites = relationship("PropertyFavorite", back_populates="property")
