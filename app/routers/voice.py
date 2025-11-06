from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.db.session import get_db
from app.schemas.voice import VoicePropertySearchRequest, VoicePropertySearchResponse
from app.schemas.property import PropertySearchFilters, VoicePropertyResponse
from app.schemas.call_session import CallSessionCreate, CallSessionUpdate, CallSessionResponse
from app.schemas.user import UserByPhone
from app.models.call_session import CallSessionStatus
from app.models.user import UserRole
from app.services import voice_service, user_service, property_service

router = APIRouter(prefix="/voice", tags=["voice"])

@router.get("/properties/search", response_model=VoicePropertySearchResponse)
def search_properties_for_voice(
    phone_number: str = Query(..., description="Número de teléfono del usuario"),
    city: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    min_bedrooms: Optional[int] = None,
    property_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Búsqueda de propiedades optimizada para voz"""
    # Buscar usuario por teléfono
    user = user_service.get_user_by_phone(db, phone_number)
    
    # Crear filtros de búsqueda
    filters = PropertySearchFilters(
        city=city,
        min_price=min_price,
        max_price=max_price,
        min_bedrooms=min_bedrooms,
        property_type=property_type
    )
    
    # Generar respuesta
    result = voice_service.generate_search_response_for_voice(
        db, filters, phone_number, user_id=user.id if user else None, limit=5
    )
    
    return VoicePropertySearchResponse(
        properties=[VoicePropertyResponse(**p) for p in result["properties"]],
        total_count=result["total_count"],
        message=result["message"]
    )

@router.post("/properties/search", response_model=VoicePropertySearchResponse)
def search_properties_for_voice_post(
    request: VoicePropertySearchRequest,
    db: Session = Depends(get_db)
):
    """Búsqueda de propiedades por criterios flexibles (para voz)"""
    user = user_service.get_user_by_phone(db, request.phone_number)
    
    # Convertir criterios a filtros
    filters = PropertySearchFilters(**request.criteria)
    
    result = voice_service.generate_search_response_for_voice(
        db, filters, request.phone_number, user_id=user.id if user else None, limit=5
    )
    
    return VoicePropertySearchResponse(
        properties=[VoicePropertyResponse(**p) for p in result["properties"]],
        total_count=result["total_count"],
        message=result["message"]
    )

@router.get("/properties/{property_id}", response_model=VoicePropertyResponse)
def get_property_for_voice(property_id: int, db: Session = Depends(get_db)):
    """Obtener propiedad formateada para voz"""
    property = property_service.get_property_by_id(db, property_id)
    if not property:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Propiedad no encontrada"
        )
    
    formatted = property_service.format_property_for_voice(property)
    return VoicePropertyResponse(**formatted)

@router.get("/users/by-phone/{phone_number}", response_model=UserByPhone)
def get_user_by_phone_for_voice(phone_number: str, db: Session = Depends(get_db)):
    """Obtener usuario por teléfono (para Twilio)"""
    user = user_service.get_user_by_phone(db, phone_number)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    return user

@router.post("/sessions", response_model=CallSessionResponse, status_code=status.HTTP_201_CREATED)
def create_call_session(session: CallSessionCreate, db: Session = Depends(get_db)):
    """Crear o actualizar sesión de llamada"""
    return voice_service.create_or_update_session(
        db, session.call_sid, session.phone_number, session.role
    )

@router.get("/sessions/{call_sid}", response_model=CallSessionResponse)
def get_call_session(call_sid: str, db: Session = Depends(get_db)):
    """Obtener sesión de llamada por call_sid"""
    session = voice_service.get_session_by_call_sid(db, call_sid)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sesión no encontrada"
        )
    return session

@router.put("/sessions/{call_sid}", response_model=CallSessionResponse)
def update_call_session(
    call_sid: str,
    session_update: CallSessionUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar sesión de llamada"""
    session = voice_service.update_session(db, call_sid, session_update)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sesión no encontrada"
        )
    return session

