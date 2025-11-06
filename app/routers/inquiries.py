from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.schemas.inquiry import InquiryCreate, InquiryUpdate, InquiryResponse
from app.models.inquiry import InquiryStatus
from app.services import inquiry_service

router = APIRouter(prefix="/inquiries", tags=["inquiries"])

@router.post("", response_model=InquiryResponse, status_code=status.HTTP_201_CREATED)
def create_inquiry(inquiry: InquiryCreate, db: Session = Depends(get_db)):
    """Crear una nueva consulta"""
    return inquiry_service.create_inquiry(db, inquiry)

@router.get("", response_model=List[InquiryResponse])
def list_inquiries(
    skip: int = 0,
    limit: int = 100,
    property_id: Optional[int] = None,
    user_id: Optional[int] = None,
    status: Optional[InquiryStatus] = None,
    db: Session = Depends(get_db)
):
    """Listar consultas con filtros opcionales"""
    return inquiry_service.list_inquiries(
        db, skip=skip, limit=limit,
        property_id=property_id,
        user_id=user_id,
        status=status
    )

@router.get("/{inquiry_id}", response_model=InquiryResponse)
def get_inquiry(inquiry_id: int, db: Session = Depends(get_db)):
    """Obtener consulta por ID"""
    inquiry = inquiry_service.get_inquiry_by_id(db, inquiry_id)
    if not inquiry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consulta no encontrada"
        )
    return inquiry

@router.put("/{inquiry_id}", response_model=InquiryResponse)
def update_inquiry(
    inquiry_id: int,
    inquiry_update: InquiryUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar consulta"""
    inquiry = inquiry_service.update_inquiry(db, inquiry_id, inquiry_update)
    if not inquiry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consulta no encontrada"
        )
    return inquiry

@router.put("/{inquiry_id}/status", response_model=InquiryResponse)
def update_inquiry_status(
    inquiry_id: int,
    status: InquiryStatus,
    db: Session = Depends(get_db)
):
    """Actualizar estado de consulta"""
    inquiry = inquiry_service.update_inquiry_status(db, inquiry_id, status)
    if not inquiry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consulta no encontrada"
        )
    return inquiry

@router.get("/property/{property_id}", response_model=List[InquiryResponse])
def get_property_inquiries(property_id: int, db: Session = Depends(get_db)):
    """Obtener todas las consultas de una propiedad"""
    return inquiry_service.get_inquiries_by_property(db, property_id)

