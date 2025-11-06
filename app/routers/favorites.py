from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.models.property_favorite import PropertyFavorite
from app.schemas.property import PropertySummary
from app.services import property_service

router = APIRouter(prefix="/favorites", tags=["favorites"])

@router.post("", status_code=status.HTTP_201_CREATED)
def add_favorite(
    user_id: int,
    property_id: int,
    db: Session = Depends(get_db)
):
    """Agregar propiedad a favoritos"""
    # Verificar que la propiedad existe
    property = property_service.get_property_by_id(db, property_id)
    if not property:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Propiedad no encontrada"
        )
    
    # Verificar si ya está en favoritos
    existing = db.query(PropertyFavorite).filter(
        PropertyFavorite.user_id == user_id,
        PropertyFavorite.property_id == property_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La propiedad ya está en favoritos"
        )
    
    favorite = PropertyFavorite(user_id=user_id, property_id=property_id)
    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    return {"message": "Propiedad agregada a favoritos", "id": favorite.id}

@router.get("", response_model=List[PropertySummary])
def list_favorites(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Listar propiedades favoritas del usuario"""
    favorites = db.query(PropertyFavorite).filter(
        PropertyFavorite.user_id == user_id
    ).all()
    
    properties = [favorite.property for favorite in favorites]
    return [PropertySummary.model_validate(p) for p in properties]

@router.delete("/{property_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_favorite(
    user_id: int,
    property_id: int,
    db: Session = Depends(get_db)
):
    """Quitar propiedad de favoritos"""
    favorite = db.query(PropertyFavorite).filter(
        PropertyFavorite.user_id == user_id,
        PropertyFavorite.property_id == property_id
    ).first()
    
    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La propiedad no está en favoritos"
        )
    
    db.delete(favorite)
    db.commit()
    return None

