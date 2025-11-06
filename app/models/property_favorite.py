from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin

class PropertyFavorite(Base, TimestampMixin):
    __tablename__ = "property_favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)

    user = relationship("User", back_populates="favorites")
    property = relationship("Property", back_populates="favorites")

    __table_args__ = (
        UniqueConstraint('user_id', 'property_id', name='unique_user_property_favorite'),
    )

