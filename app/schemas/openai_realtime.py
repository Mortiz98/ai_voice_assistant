from typing import Optional, Dict, Any, List
from pydantic import BaseModel

class FunctionCall(BaseModel):
    name: str
    arguments: Dict[str, Any]

class FunctionCallResponse(BaseModel):
    name: str
    result: Any

class RealtimeEvent(BaseModel):
    event: str
    data: Optional[Dict[str, Any]] = None

class ConversationContext(BaseModel):
    call_sid: str
    phone_number: str
    user_id: Optional[int] = None
    role: Optional[str] = None
    current_step: Optional[str] = None
    context_data: Dict[str, Any] = {}

