from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from app.models.call_session import CallSession, CallSessionStatus
from app.models.user import UserRole
from app.schemas.call_session import CallSessionCreate, CallSessionUpdate
from app.services.user_service import get_user_by_phone
from app.services.search_service import advanced_search, format_search_results_for_voice, save_search_history
from app.schemas.property import PropertySearchFilters


def create_or_update_session(
    db: Session,
    call_sid: str,
    phone_number: str,
    role: Optional[UserRole] = None,
    context_data: Optional[Dict[str, Any]] = None
) -> CallSession:
    """Crear o actualizar sesión de llamada"""
    existing_session = db.query(CallSession).filter(
        CallSession.call_sid == call_sid
    ).first()
    
    if existing_session:
        if context_data:
            existing_session.context_data = context_data
        if role:
            existing_session.role = role
        db.commit()
        db.refresh(existing_session)
        return existing_session
    
    # Buscar usuario por teléfono
    user = get_user_by_phone(db, phone_number)
    
    session = CallSession(
        call_sid=call_sid,
        phone_number=phone_number,
        user_id=user.id if user else None,
        role=role or (user.role if user else None),
        context_data=context_data or {}
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

def get_session_by_call_sid(db: Session, call_sid: str) -> Optional[CallSession]:
    """Obtener sesión por call_sid"""
    return db.query(CallSession).filter(CallSession.call_sid == call_sid).first()

def update_session(
    db: Session,
    call_sid: str,
    session_update: CallSessionUpdate
) -> Optional[CallSession]:
    """Actualizar sesión de llamada"""
    session = get_session_by_call_sid(db, call_sid)
    if not session:
        return None
    
    update_data = session_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(session, field, value)
    
    db.commit()
    db.refresh(session)
    return session

def complete_session(db: Session, call_sid: str) -> bool:
    """Marcar sesión como completada"""
    session = get_session_by_call_sid(db, call_sid)
    if not session:
        return False
    
    session.status = CallSessionStatus.completed
    db.commit()
    return True

def extract_search_criteria_from_voice(
    transcript: str,
    existing_criteria: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Extraer criterios de búsqueda de transcripción de voz"""
    criteria = existing_criteria or {}
    
    # Aquí iría la lógica de procesamiento de lenguaje natural
    # Por ahora, retornamos los criterios existentes
    # En el futuro, esto se integraría con un servicio de NLP/IA
    
    return criteria

def generate_search_response_for_voice(
    db: Session,
    filters: PropertySearchFilters,
    phone_number: str,
    user_id: Optional[int] = None,
    limit: int = 5
) -> Dict[str, Any]:
    """Generar respuesta de búsqueda optimizada para voz"""
    properties, total_count = advanced_search(db, filters, skip=0, limit=limit)
    
    # Guardar historial de búsqueda
    save_search_history(
        db,
        filters.model_dump(),
        total_count,
        user_id=user_id,
        phone_number=phone_number
    )
    
    formatted_properties = format_search_results_for_voice(properties)
    
    # Generar mensaje descriptivo
    message = None
    if total_count == 0:
        message = "No se encontraron propiedades que coincidan con tu búsqueda."
    elif total_count == 1:
        message = "Encontré una propiedad que coincide con tu búsqueda."
    else:
        message = f"Encontré {total_count} propiedades. Te mostraré las {len(formatted_properties)} mejores opciones."
    
    return {
        "properties": formatted_properties,
        "total_count": total_count,
        "message": message
    }

