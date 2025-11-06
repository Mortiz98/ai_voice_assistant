from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from app.models.property import PropertyType, PropertyStatus
from app.schemas.common import TimestampSchema
from app.schemas.user import UserResponse

class PropertyBase(BaseModel):
    title: str
    description: Optional[str] = None
    address: str
    city: str
    neighborhood: Optional[str] = None
    zip_code: Optional[str] = None
    property_type: PropertyType
    bedrooms: int
    bathrooms: int
    square_meters: Optional[float] = None
    price: int
    deposit: Optional[int] = None
    pet_friendly: bool = False
    furnished: bool = False
    amenities: Optional[Dict[str, Any]] = None
    images: Optional[List[str]] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class PropertyCreate(PropertyBase):
    owner_id: int

class PropertyUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    neighborhood: Optional[str] = None
    zip_code: Optional[str] = None
    property_type: Optional[PropertyType] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    square_meters: Optional[float] = None
    price: Optional[int] = None
    deposit: Optional[int] = None
    status: Optional[PropertyStatus] = None
    pet_friendly: Optional[bool] = None
    furnished: Optional[bool] = None
    amenities: Optional[Dict[str, Any]] = None
    images: Optional[List[str]] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class PropertyResponse(PropertyBase, TimestampSchema):
    id: int
    status: PropertyStatus
    owner_id: int
    owner: Optional[UserResponse] = None

    class Config:
        from_attributes = True

class PropertySummary(BaseModel):
    id: int
    title: str
    address: str
    city: str
    price: int
    bedrooms: int
    bathrooms: int
    property_type: PropertyType
    status: PropertyStatus

    class Config:
        from_attributes = True

class PropertySearchFilters(BaseModel):
    city: Optional[str] = None
    neighborhood: Optional[str] = None
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    min_bedrooms: Optional[int] = None
    max_bedrooms: Optional[int] = None
    property_type: Optional[PropertyType] = None
    pet_friendly: Optional[bool] = None
    furnished: Optional[bool] = None
    min_square_meters: Optional[float] = None
    max_square_meters: Optional[float] = None
    status: Optional[PropertyStatus] = None

class PropertySearchResponse(BaseModel):
    properties: List[PropertySummary]
    total_count: int
    page: int = 1
    page_size: int = 10

class VoicePropertyResponse(BaseModel):
    id: int
    title: str
    address: str
    city: str
    neighborhood: Optional[str] = None
    price: int
    bedrooms: int
    bathrooms: int
    description_short: Optional[str] = None
    property_type: PropertyType

    class Config:
        from_attributes = True

