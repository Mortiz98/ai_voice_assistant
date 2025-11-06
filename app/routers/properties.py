from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.schemas.property import (
    PropertyCreate, PropertyUpdate, PropertyResponse, PropertySummary,
    PropertySearchFilters, PropertySearchResponse
)
from app.services import property_service, search_service

router = APIRouter(prefix="/properties", tags=["properties"])

@router.post("", response_model=PropertyResponse, status_code=status.HTTP_201_CREATED)
def create_property(property: PropertyCreate, db: Session = Depends(get_db)):
    """Crear una nueva propiedad"""
    return property_service.create_property(db, property)

@router.get("", response_model=List[PropertySummary])
def list_properties(
    skip: int = 0,
    limit: int = 10,
    city: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Listar propiedades con filtros básicos"""
    filters = PropertySearchFilters(
        city=city,
        min_price=min_price,
        max_price=max_price
    )
    properties, total = search_service.advanced_search(db, filters, skip=skip, limit=limit)
    return properties

@router.get("/search", response_model=PropertySearchResponse)
def search_properties(
    filters: PropertySearchFilters = Depends(),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Búsqueda avanzada de propiedades"""
    skip = (page - 1) * page_size
    properties, total_count = search_service.advanced_search(db, filters, skip=skip, limit=page_size)
    
    return PropertySearchResponse(
        properties=[PropertySummary.model_validate(p) for p in properties],
        total_count=total_count,
        page=page,
        page_size=page_size
    )

@router.post("/search", response_model=PropertySearchResponse)
def search_properties_post(
    filters: PropertySearchFilters,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Búsqueda avanzada de propiedades (POST)"""
    skip = (page - 1) * page_size
    properties, total_count = search_service.advanced_search(db, filters, skip=skip, limit=page_size)
    
    return PropertySearchResponse(
        properties=[PropertySummary.model_validate(p) for p in properties],
        total_count=total_count,
        page=page,
        page_size=page_size
    )

@router.get("/{property_id}", response_model=PropertyResponse)
def get_property(property_id: int, db: Session = Depends(get_db)):
    """Obtener propiedad por ID"""
    property = property_service.get_property_by_id(db, property_id)
    if not property:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Propiedad no encontrada"
        )
    return property

@router.put("/{property_id}", response_model=PropertyResponse)
def update_property(
    property_id: int,
    property_update: PropertyUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar propiedad"""
    property = property_service.update_property(db, property_id, property_update)
    if not property:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Propiedad no encontrada"
        )
    return property

@router.delete("/{property_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_property(property_id: int, db: Session = Depends(get_db)):
    """Eliminar propiedad"""
    success = property_service.delete_property(db, property_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Propiedad no encontrada"
        )
    return None

@router.get("/{property_id}/summary", response_model=PropertySummary)
def get_property_summary(property_id: int, db: Session = Depends(get_db)):
    """Obtener resumen de propiedad (optimizado para voz)"""
    property = property_service.get_property_by_id(db, property_id)
    if not property:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Propiedad no encontrada"
        )
    return property

