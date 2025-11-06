from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from app.schemas.property import VoicePropertyResponse, PropertySearchFilters

class VoicePropertySearchRequest(BaseModel):
    phone_number: str
    criteria: Dict[str, Any]
    step: Optional[str] = None

class VoicePropertySearchResponse(BaseModel):
    properties: List[VoicePropertyResponse]
    total_count: int
    message: Optional[str] = None

