import re
from typing import Optional

def validate_phone_number(phone_number: str) -> bool:
    """Validar formato de número de teléfono (E.164 básico)"""
    # Formato E.164: +[código país][número]
    pattern = r'^\+[1-9]\d{1,14}$'
    return bool(re.match(pattern, phone_number))

def normalize_phone_number(phone_number: str) -> Optional[str]:
    """Normalizar número de teléfono a formato E.164"""
    # Remover espacios, guiones, paréntesis
    cleaned = re.sub(r'[\s\-\(\)]', '', phone_number)
    
    # Si no empieza con +, asumir código de país (ajustar según necesidad)
    if not cleaned.startswith('+'):
        # Por defecto, agregar +1 (EE.UU./Canadá)
        # En producción, esto debería ser configurable
        cleaned = '+1' + cleaned
    
    if validate_phone_number(cleaned):
        return cleaned
    
    return None

def validate_property_data(data: dict) -> tuple[bool, Optional[str]]:
    """Validar datos de propiedad"""
    required_fields = ['title', 'address', 'city', 'property_type', 'bedrooms', 'bathrooms', 'price']
    
    for field in required_fields:
        if field not in data or data[field] is None:
            return False, f"Campo requerido faltante: {field}"
    
    if data.get('price', 0) <= 0:
        return False, "El precio debe ser mayor a 0"
    
    if data.get('bedrooms', 0) < 0:
        return False, "El número de habitaciones no puede ser negativo"
    
    if data.get('bathrooms', 0) < 0:
        return False, "El número de baños no puede ser negativo"
    
    return True, None

def validate_search_criteria(criteria: dict) -> tuple[bool, Optional[str]]:
    """Validar criterios de búsqueda"""
    if 'min_price' in criteria and 'max_price' in criteria:
        if criteria['min_price'] > criteria['max_price']:
            return False, "El precio mínimo no puede ser mayor al precio máximo"
    
    if 'min_bedrooms' in criteria and 'max_bedrooms' in criteria:
        if criteria['min_bedrooms'] > criteria['max_bedrooms']:
            return False, "El número mínimo de habitaciones no puede ser mayor al máximo"
    
    return True, None

