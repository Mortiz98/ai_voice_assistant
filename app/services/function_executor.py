from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.services import property_service, user_service, inquiry_service, search_service
from app.schemas.property import PropertySearchFilters, PropertyCreate
from app.schemas.inquiry import InquiryCreate
from app.models.property import PropertyType, PropertyStatus
from app.models.user import UserRole
import json

class FunctionExecutor:
    """Ejecuta funciones llamadas por la IA de OpenAI Realtime"""
    
    def __init__(self, db: Session, call_sid: str, phone_number: str):
        self.db = db
        self.call_sid = call_sid
        self.phone_number = phone_number
        self.user = user_service.get_user_by_phone(db, phone_number)
    
    def execute_function(self, function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta una función llamada por la IA"""
        try:
            if function_name == "search_properties":
                return self._search_properties(arguments)
            elif function_name == "get_property_details":
                return self._get_property_details(arguments)
            elif function_name == "create_property":
                return self._create_property(arguments)
            elif function_name == "create_inquiry":
                return self._create_inquiry(arguments)
            elif function_name == "get_user_info":
                return self._get_user_info()
            elif function_name == "save_favorite":
                return self._save_favorite(arguments)
            else:
                return {"error": f"Función desconocida: {function_name}"}
        except Exception as e:
            return {"error": str(e)}
    
    def _search_properties(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Buscar propiedades según criterios"""
        filters = PropertySearchFilters(
            city=args.get("city"),
            neighborhood=args.get("neighborhood"),
            min_price=args.get("min_price"),
            max_price=args.get("max_price"),
            min_bedrooms=args.get("min_bedrooms") or args.get("bedrooms"),
            max_bedrooms=args.get("max_bedrooms"),
            property_type=PropertyType(args.get("property_type")) if args.get("property_type") else None,
            pet_friendly=args.get("pet_friendly"),
            furnished=args.get("furnished"),
            min_square_meters=args.get("min_square_meters"),
            max_square_meters=args.get("max_square_meters"),
            status=PropertyStatus.available
        )
        
        properties, total_count = search_service.advanced_search(self.db, filters, skip=0, limit=5)
        
        # Formatear para respuesta natural
        results = []
        for prop in properties:
            results.append({
                "id": prop.id,
                "title": prop.title,
                "address": f"{prop.address}, {prop.city}",
                "price": f"${prop.price:,}",
                "bedrooms": prop.bedrooms,
                "bathrooms": prop.bathrooms,
                "property_type": prop.property_type.value,
                "description": prop.description[:200] if prop.description else "Sin descripción"
            })
        
        return {
            "total_found": total_count,
            "properties": results,
            "message": f"Encontré {total_count} propiedades. Te muestro las {len(results)} mejores opciones."
        }
    
    def _get_property_details(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Obtener detalles completos de una propiedad"""
        property_id = args.get("property_id")
        if not property_id:
            return {"error": "Se requiere property_id"}
        
        property = property_service.get_property_by_id(self.db, property_id)
        if not property:
            return {"error": "Propiedad no encontrada"}
        
        return {
            "id": property.id,
            "title": property.title,
            "description": property.description or "Sin descripción",
            "address": f"{property.address}, {property.neighborhood or ''}, {property.city}",
            "price": f"${property.price:,}",
            "deposit": f"${property.deposit:,}" if property.deposit else "No especificado",
            "bedrooms": property.bedrooms,
            "bathrooms": property.bathrooms,
            "square_meters": property.square_meters or "No especificado",
            "property_type": property.property_type.value,
            "pet_friendly": "Sí" if property.pet_friendly else "No",
            "furnished": "Sí" if property.furnished else "No",
            "amenities": property.amenities or [],
            "owner_name": property.owner.name if property.owner else "No disponible"
        }
    
    def _create_property(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Crear una nueva propiedad (solo para propietarios)"""
        if not self.user or self.user.role != UserRole.owner:
            return {"error": "Solo los propietarios pueden registrar propiedades"}
        
        try:
            property_data = PropertyCreate(
                title=args.get("title", "Propiedad sin título"),
                description=args.get("description"),
                address=args["address"],
                city=args["city"],
                neighborhood=args.get("neighborhood"),
                zip_code=args.get("zip_code"),
                property_type=PropertyType(args.get("property_type", "apartment")),
                bedrooms=int(args.get("bedrooms", 1)),
                bathrooms=int(args.get("bathrooms", 1)),
                square_meters=args.get("square_meters"),
                price=int(args["price"]),
                deposit=args.get("deposit"),
                pet_friendly=args.get("pet_friendly", False),
                furnished=args.get("furnished", False),
                amenities=args.get("amenities"),
                owner_id=self.user.id
            )
            
            property = property_service.create_property(self.db, property_data)
            
            return {
                "success": True,
                "property_id": property.id,
                "message": f"Propiedad '{property.title}' registrada exitosamente con ID {property.id}"
            }
        except Exception as e:
            return {"error": f"Error al crear propiedad: {str(e)}"}
    
    def _create_inquiry(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Crear una consulta sobre una propiedad"""
        property_id = args.get("property_id")
        message = args.get("message", "Interesado en esta propiedad")
        
        if not property_id:
            return {"error": "Se requiere property_id"}
        
        inquiry_data = InquiryCreate(
            property_id=property_id,
            message=message,
            phone_number=self.phone_number,
            user_id=self.user.id if self.user else None
        )
        
        inquiry = inquiry_service.create_inquiry(self.db, inquiry_data)
        
        return {
            "success": True,
            "inquiry_id": inquiry.id,
            "message": "Tu consulta ha sido registrada. El propietario te contactará pronto."
        }
    
    def _get_user_info(self) -> Dict[str, Any]:
        """Obtener información del usuario actual"""
        if not self.user:
            return {
                "registered": False,
                "message": "No estás registrado en el sistema"
            }
        
        return {
            "registered": True,
            "name": self.user.name,
            "role": self.user.role.value,
            "email": self.user.email,
            "phone": self.user.phone_number
        }
    
    def _save_favorite(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Guardar una propiedad en favoritos"""
        if not self.user:
            return {"error": "Debes estar registrado para guardar favoritos"}
        
        property_id = args.get("property_id")
        if not property_id:
            return {"error": "Se requiere property_id"}
        
        # Verificar que la propiedad existe
        property = property_service.get_property_by_id(self.db, property_id)
        if not property:
            return {"error": "Propiedad no encontrada"}
        
        # Verificar si ya está en favoritos
        from app.models.property_favorite import PropertyFavorite
        existing = self.db.query(PropertyFavorite).filter(
            PropertyFavorite.user_id == self.user.id,
            PropertyFavorite.property_id == property_id
        ).first()
        
        if existing:
            return {"message": "Esta propiedad ya está en tus favoritos"}
        
        favorite = PropertyFavorite(user_id=self.user.id, property_id=property_id)
        self.db.add(favorite)
        self.db.commit()
        
        return {
            "success": True,
            "message": f"Propiedad '{property.title}' agregada a tus favoritos"
        }

