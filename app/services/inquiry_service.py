from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.inquiry import Inquiry, InquiryStatus
from app.schemas.inquiry import InquiryCreate, InquiryUpdate

def create_inquiry(db: Session, inquiry: InquiryCreate) -> Inquiry:
    """Crear una nueva consulta"""
    db_inquiry = Inquiry(
        message=inquiry.message,
        phone_number=inquiry.phone_number,
        preferred_contact_time=inquiry.preferred_contact_time,
        property_id=inquiry.property_id,
        user_id=inquiry.user_id,
        status=InquiryStatus.pending
    )
    db.add(db_inquiry)
    db.commit()
    db.refresh(db_inquiry)
    return db_inquiry

def get_inquiry_by_id(db: Session, inquiry_id: int) -> Optional[Inquiry]:
    """Obtener consulta por ID"""
    return db.query(Inquiry).filter(Inquiry.id == inquiry_id).first()

def update_inquiry_status(
    db: Session,
    inquiry_id: int,
    status: InquiryStatus
) -> Optional[Inquiry]:
    """Actualizar estado de consulta"""
    db_inquiry = get_inquiry_by_id(db, inquiry_id)
    if not db_inquiry:
        return None
    
    db_inquiry.status = status
    db.commit()
    db.refresh(db_inquiry)
    return db_inquiry

def update_inquiry(
    db: Session,
    inquiry_id: int,
    inquiry_update: InquiryUpdate
) -> Optional[Inquiry]:
    """Actualizar consulta"""
    db_inquiry = get_inquiry_by_id(db, inquiry_id)
    if not db_inquiry:
        return None
    
    update_data = inquiry_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_inquiry, field, value)
    
    db.commit()
    db.refresh(db_inquiry)
    return db_inquiry

def list_inquiries(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    property_id: Optional[int] = None,
    user_id: Optional[int] = None,
    status: Optional[InquiryStatus] = None
) -> List[Inquiry]:
    """Listar consultas con filtros opcionales"""
    query = db.query(Inquiry)
    
    if property_id:
        query = query.filter(Inquiry.property_id == property_id)
    
    if user_id:
        query = query.filter(Inquiry.user_id == user_id)
    
    if status:
        query = query.filter(Inquiry.status == status)
    
    return query.order_by(Inquiry.created_at.desc()).offset(skip).limit(limit).all()

def get_inquiries_by_property(db: Session, property_id: int) -> List[Inquiry]:
    """Obtener todas las consultas de una propiedad"""
    return db.query(Inquiry).filter(
        Inquiry.property_id == property_id
    ).order_by(Inquiry.created_at.desc()).all()

