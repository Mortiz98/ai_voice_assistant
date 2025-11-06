from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

def create_user(db: Session, user: UserCreate) -> User:
    """Crear un nuevo usuario"""
    db_user = User(
        name=user.name,
        email=user.email,
        phone_number=user.phone_number,
        role=user.role,
        preferences=user.preferences
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Obtener usuario por ID"""
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_phone(db: Session, phone_number: str) -> Optional[User]:
    """Obtener usuario por número de teléfono"""
    return db.query(User).filter(User.phone_number == phone_number).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Obtener usuario por email"""
    return db.query(User).filter(User.email == email).first()

def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
    """Actualizar usuario"""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int) -> bool:
    """Eliminar usuario (soft delete)"""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return False
    
    db_user.is_active = False
    db.commit()
    return True

def list_users(db: Session, skip: int = 0, limit: int = 100, role: Optional[str] = None) -> List[User]:
    """Listar usuarios con filtros opcionales"""
    query = db.query(User).filter(User.is_active == True)
    
    if role:
        query = query.filter(User.role == role)
    
    return query.offset(skip).limit(limit).all()

