from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Dict, Any
from app.models.property import Property, PropertyStatus, PropertyType
from app.schemas.property import PropertySearchFilters
from app.models.property_search import PropertySearch
from app.services.property_service import format_property_for_voice

def advanced_search(
    db: Session,
    filters: PropertySearchFilters,
    skip: int = 0,
    limit: int = 10
) -> tuple[List[Property], int]:
    """Búsqueda avanzada de propiedades con filtros"""
    query = db.query(Property).filter(Property.status == PropertyStatus.available)
    
    # Aplicar filtros
    if filters.city:
        query = query.filter(Property.city.ilike(f"%{filters.city}%"))
    
    if filters.neighborhood:
        query = query.filter(Property.neighborhood.ilike(f"%{filters.neighborhood}%"))
    
    if filters.min_price:
        query = query.filter(Property.price >= filters.min_price)
    
    if filters.max_price:
        query = query.filter(Property.price <= filters.max_price)
    
    if filters.min_bedrooms:
        query = query.filter(Property.bedrooms >= filters.min_bedrooms)
    
    if filters.max_bedrooms:
        query = query.filter(Property.bedrooms <= filters.max_bedrooms)
    
    if filters.property_type:
        query = query.filter(Property.property_type == filters.property_type)
    
    if filters.pet_friendly is not None:
        query = query.filter(Property.pet_friendly == filters.pet_friendly)
    
    if filters.furnished is not None:
        query = query.filter(Property.furnished == filters.furnished)
    
    if filters.min_square_meters:
        query = query.filter(Property.square_meters >= filters.min_square_meters)
    
    if filters.max_square_meters:
        query = query.filter(Property.square_meters <= filters.max_square_meters)
    
    if filters.status:
        query = query.filter(Property.status == filters.status)
    
    # Contar total
    total_count = query.count()
    
    # Aplicar paginación y ordenar por precio
    properties = query.order_by(Property.price.asc()).offset(skip).limit(limit).all()
    
    return properties, total_count

def save_search_history(
    db: Session,
    search_criteria: Dict[str, Any],
    results_count: int,
    user_id: int = None,
    phone_number: str = None
) -> PropertySearch:
    """Guardar historial de búsqueda"""
    search = PropertySearch(
        user_id=user_id,
        phone_number=phone_number,
        search_criteria=search_criteria,
        results_count=results_count
    )
    db.add(search)
    db.commit()
    db.refresh(search)
    return search

def format_search_results_for_voice(properties: List[Property]) -> List[Dict[str, Any]]:
    """Formatear resultados de búsqueda para voz"""
    return [format_property_for_voice(prop) for prop in properties]

