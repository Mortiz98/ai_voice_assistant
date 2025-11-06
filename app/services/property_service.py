from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.property import Property, PropertyStatus
from app.schemas.property import PropertyCreate, PropertyUpdate

def create_property(db: Session, property: PropertyCreate) -> Property:
    """Crear una nueva propiedad"""
    db_property = Property(
        title=property.title,
        description=property.description,
        address=property.address,
        city=property.city,
        neighborhood=property.neighborhood,
        zip_code=property.zip_code,
        property_type=property.property_type,
        bedrooms=property.bedrooms,
        bathrooms=property.bathrooms,
        square_meters=property.square_meters,
        price=property.price,
        deposit=property.deposit,
        pet_friendly=property.pet_friendly,
        furnished=property.furnished,
        amenities=property.amenities,
        images=property.images,
        latitude=property.latitude,
        longitude=property.longitude,
        owner_id=property.owner_id,
        status=PropertyStatus.available
    )
    db.add(db_property)
    db.commit()
    db.refresh(db_property)
    return db_property

def get_property_by_id(db: Session, property_id: int) -> Optional[Property]:
    """Obtener propiedad por ID"""
    return db.query(Property).filter(Property.id == property_id).first()

def update_property(db: Session, property_id: int, property_update: PropertyUpdate) -> Optional[Property]:
    """Actualizar propiedad"""
    db_property = get_property_by_id(db, property_id)
    if not db_property:
        return None
    
    update_data = property_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_property, field, value)
    
    db.commit()
    db.refresh(db_property)
    return db_property

def delete_property(db: Session, property_id: int) -> bool:
    """Eliminar propiedad"""
    db_property = get_property_by_id(db, property_id)
    if not db_property:
        return False
    
    db.delete(db_property)
    db.commit()
    return True

def get_properties_by_owner(db: Session, owner_id: int, skip: int = 0, limit: int = 100) -> List[Property]:
    """Obtener propiedades de un propietario"""
    return db.query(Property).filter(
        Property.owner_id == owner_id
    ).offset(skip).limit(limit).all()

def format_property_for_voice(property: Property) -> dict:
    """Formatear propiedad para lectura por voz"""
    description_short = property.description[:100] + "..." if property.description and len(property.description) > 100 else property.description
    
    return {
        "id": property.id,
        "title": property.title,
        "address": property.address,
        "city": property.city,
        "neighborhood": property.neighborhood,
        "price": property.price,
        "bedrooms": property.bedrooms,
        "bathrooms": property.bathrooms,
        "description_short": description_short,
        "property_type": property.property_type.value
    }

