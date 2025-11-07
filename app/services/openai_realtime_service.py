import json
import asyncio
import websockets
from typing import Dict, Any, Optional, AsyncGenerator
import logging
from app.core.config import settings
from app.services.function_executor import FunctionExecutor
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class OpenAIRealtimeService:
    """Servicio para manejar conexiones con OpenAI Realtime API via WebSocket"""
    
    def __init__(self, db: Session, call_sid: str, phone_number: str):
        self.db = db
        self.call_sid = call_sid
        self.phone_number = phone_number
        self.function_executor = FunctionExecutor(db, call_sid, phone_number)
        self.websocket = None
        self.audio_queue = asyncio.Queue()
        self.event_queue = asyncio.Queue()
        self.session_id = None
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        
    def get_functions_definition(self) -> list:
        """Define las funciones que la IA puede llamar"""
        return [
            {
                "type": "function",
                "name": "search_properties",
                "description": "Buscar propiedades disponibles según los criterios del usuario. Usa esto cuando el usuario quiera buscar propiedades para rentar.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "Ciudad donde buscar propiedades"
                        },
                        "neighborhood": {
                            "type": "string",
                            "description": "Barrio o zona específica"
                        },
                        "min_price": {
                            "type": "integer",
                            "description": "Precio mínimo de renta mensual"
                        },
                        "max_price": {
                            "type": "integer",
                            "description": "Precio máximo de renta mensual"
                        },
                        "bedrooms": {
                            "type": "integer",
                            "description": "Número de habitaciones deseado"
                        },
                        "min_bedrooms": {
                            "type": "integer",
                            "description": "Número mínimo de habitaciones"
                        },
                        "max_bedrooms": {
                            "type": "integer",
                            "description": "Número máximo de habitaciones"
                        },
                        "property_type": {
                            "type": "string",
                            "enum": ["apartment", "house", "studio", "townhouse", "condo"],
                            "description": "Tipo de propiedad"
                        },
                        "pet_friendly": {
                            "type": "boolean",
                            "description": "Si acepta mascotas"
                        },
                        "furnished": {
                            "type": "boolean",
                            "description": "Si está amueblada"
                        },
                        "min_square_meters": {
                            "type": "number",
                            "description": "Metros cuadrados mínimos"
                        },
                        "max_square_meters": {
                            "type": "number",
                            "description": "Metros cuadrados máximos"
                        }
                    }
                },
                "strict": False
            },
            {
                "type": "function",
                "name": "get_property_details",
                "description": "Obtener información detallada de una propiedad específica. Usa esto cuando el usuario pregunte por detalles de una propiedad o quiera más información.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "property_id": {
                            "type": "integer",
                            "description": "ID de la propiedad"
                        }
                    },
                    "required": ["property_id"]
                },
                "strict": True
            },
            {
                "type": "function",
                "name": "create_property",
                "description": "Registrar una nueva propiedad en el sistema. Solo para propietarios que quieren publicar su propiedad.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Título o nombre de la propiedad"
                        },
                        "description": {
                            "type": "string",
                            "description": "Descripción detallada de la propiedad"
                        },
                        "address": {
                            "type": "string",
                            "description": "Dirección completa de la propiedad",
                            "required": True
                        },
                        "city": {
                            "type": "string",
                            "description": "Ciudad donde está ubicada",
                            "required": True
                        },
                        "neighborhood": {
                            "type": "string",
                            "description": "Barrio o zona"
                        },
                        "zip_code": {
                            "type": "string",
                            "description": "Código postal"
                        },
                        "property_type": {
                            "type": "string",
                            "enum": ["apartment", "house", "studio", "townhouse", "condo"],
                            "description": "Tipo de propiedad"
                        },
                        "bedrooms": {
                            "type": "integer",
                            "description": "Número de habitaciones",
                            "required": True
                        },
                        "bathrooms": {
                            "type": "integer",
                            "description": "Número de baños",
                            "required": True
                        },
                        "square_meters": {
                            "type": "number",
                            "description": "Metros cuadrados"
                        },
                        "price": {
                            "type": "integer",
                            "description": "Precio de renta mensual",
                            "required": True
                        },
                        "deposit": {
                            "type": "integer",
                            "description": "Depósito requerido"
                        },
                        "pet_friendly": {
                            "type": "boolean",
                            "description": "Si acepta mascotas"
                        },
                        "furnished": {
                            "type": "boolean",
                            "description": "Si está amueblada"
                        },
                        "amenities": {
                            "type": "object",
                            "description": "Amenidades adicionales (parking, pool, etc.)"
                        }
                    },
                    "required": ["address", "city", "bedrooms", "bathrooms", "price"]
                },
                "strict": False
            },
            {
                "type": "function",
                "name": "create_inquiry",
                "description": "Crear una consulta o interés sobre una propiedad. Usa esto cuando el usuario quiera contactar al propietario o mostrar interés en una propiedad.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "property_id": {
                            "type": "integer",
                            "description": "ID de la propiedad de interés",
                            "required": True
                        },
                        "message": {
                            "type": "string",
                            "description": "Mensaje o comentario del interesado"
                        }
                    },
                    "required": ["property_id"]
                },
                "strict": False
            },
            {
                "type": "function",
                "name": "get_user_info",
                "description": "Obtener información del usuario actual. Usa esto para verificar si el usuario está registrado y qué rol tiene.",
                "parameters": {
                    "type": "object",
                    "properties": {}
                },
                "strict": True
            },
            {
                "type": "function",
                "name": "save_favorite",
                "description": "Guardar una propiedad en la lista de favoritos del usuario. Usa esto cuando el usuario quiera guardar una propiedad para verla después.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "property_id": {
                            "type": "integer",
                            "description": "ID de la propiedad a guardar",
                            "required": True
                        }
                    },
                    "required": ["property_id"]
                },
                "strict": True
            }
        ]
    
    def get_system_instruction(self) -> str:
        """Instrucciones del sistema para la IA"""
        user_info = self.function_executor._get_user_info()
        role_context = ""
        
        if user_info.get("registered"):
            if user_info["role"] == "owner":
                role_context = "Eres un asistente de voz para propietarios. Puedes ayudar a registrar propiedades y gestionar consultas de interesados."
            else:
                role_context = "Eres un asistente de voz para inquilinos. Puedes ayudar a buscar propiedades disponibles y obtener información sobre ellas."
        else:
            role_context = "Eres un asistente de voz que ayuda tanto a propietarios como a inquilinos. Puedes ayudar a buscar propiedades o registrar nuevas propiedades."
        
        return f"""{role_context}

INSTRUCCIONES:
- Habla de forma natural, amigable y profesional
- Cuando el usuario busque propiedades, usa la función search_properties con los criterios mencionados
- Cuando el usuario quiera detalles de una propiedad, usa get_property_details
- Si es propietario y quiere registrar una propiedad, usa create_property
- Si el usuario muestra interés en una propiedad, usa create_inquiry
- Presenta la información de forma clara y fácil de entender
- Si no hay resultados, sugiere ajustar los criterios de búsqueda
- Responde en español de forma natural y conversacional
- Mantén las respuestas concisas pero informativas
"""
    
    async def create_session(self) -> Dict[str, Any]:
        """Crear una sesión de Realtime API via WebSocket"""
        try:
            # URL del WebSocket de OpenAI Realtime API
            # La API key se envía en el header Authorization
            ws_url = f"wss://api.openai.com/v1/realtime?model={self.model}"
            
            # Conectar al WebSocket con headers de autenticación
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "OpenAI-Beta": "realtime=v1"
            }
            
            # Conectar al WebSocket
            self.websocket = await websockets.connect(ws_url, extra_headers=headers)
            
            # Configurar la sesión
            config = {
                "type": "session.update",
                "session": {
                    "modalities": ["text", "audio"],
                    "instructions": self.get_system_instruction(),
                    "voice": "alloy",
                    "input_audio_format": "pcm16",
                    "output_audio_format": "pcm16",
                    "input_audio_transcription": {
                        "model": "whisper-1"
                    },
                    "turn_detection": {
                        "type": "server_vad",
                        "threshold": 0.5,
                        "prefix_padding_ms": 300,
                        "silence_duration_ms": 500
                    },
                    "temperature": 0.8,
                    "tools": self.get_functions_definition()
                }
            }
            
            await self.websocket.send(json.dumps(config))
            
            # Iniciar tarea para recibir eventos
            asyncio.create_task(self._receive_events())
            
            return {"status": "connected", "session_id": self.call_sid}
        except Exception as e:
            logger.error(f"Error creating OpenAI session: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _receive_events(self):
        """Recibir eventos del WebSocket de OpenAI"""
        try:
            async for message in self.websocket:
                event = json.loads(message)
                event_type = event.get("type")
                
                if event_type == "session.created":
                    self.session_id = event.get("session", {}).get("id")
                    logger.info(f"OpenAI session created: {self.session_id}")
                
                elif event_type == "response.audio_transcript.delta":
                    # Transcripción del audio
                    transcript = event.get("delta", "")
                    logger.debug(f"Transcript: {transcript}")
                
                elif event_type == "response.audio.delta":
                    # Audio de respuesta
                    audio_base64 = event.get("delta", "")
                    if audio_base64:
                        audio_data = bytes.fromhex(audio_base64)
                        await self.audio_queue.put(audio_data)
                
                elif event_type == "response.function_call_arguments.delta":
                    # Argumentos de función en progreso
                    pass
                
                elif event_type == "response.function_call_arguments.done":
                    # Función completada, ejecutarla
                    function_name = event.get("name")
                    arguments_str = event.get("arguments", "{}")
                    arguments = json.loads(arguments_str)
                    
                    # Ejecutar función
                    result = self.function_executor.execute_function(function_name, arguments)
                    
                    # Enviar resultado
                    response = {
                        "type": "response.function_call_output_item.add",
                        "item": {
                            "type": "function_call_output",
                            "call_id": event.get("call_id"),
                            "output": json.dumps(result)
                        }
                    }
                    await self.websocket.send(json.dumps(response))
                
                elif event_type == "response.done":
                    # Respuesta completada
                    logger.debug("Response done")
                
                # Poner evento en cola para procesamiento
                await self.event_queue.put(event)
                
        except websockets.exceptions.ConnectionClosed:
            logger.info("OpenAI WebSocket connection closed")
        except Exception as e:
            logger.error(f"Error receiving events: {e}")
    
    async def handle_event(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Manejar eventos de la sesión de Realtime (legacy, ahora se maneja en _receive_events)"""
        # Este método se mantiene por compatibilidad pero la lógica está en _receive_events
        pass
    
    async def send_audio(self, audio_data: bytes):
        """Enviar audio a la sesión de Realtime"""
        if self.websocket:
            try:
                # Convertir audio a hex string
                audio_hex = audio_data.hex()
                
                # Enviar audio al buffer
                append_message = {
                    "type": "input_audio_buffer.append",
                    "audio": audio_hex
                }
                await self.websocket.send(json.dumps(append_message))
                
                # Commit el buffer
                commit_message = {
                    "type": "input_audio_buffer.commit"
                }
                await self.websocket.send(json.dumps(commit_message))
            except Exception as e:
                logger.error(f"Error sending audio: {e}")
    
    async def get_audio_response(self) -> AsyncGenerator[bytes, None]:
        """Obtener audio de respuesta de la IA"""
        while True:
            try:
                audio_data = await asyncio.wait_for(self.audio_queue.get(), timeout=1.0)
                yield audio_data
            except asyncio.TimeoutError:
                break
    
    async def close(self):
        """Cerrar la sesión"""
        if self.websocket:
            try:
                # Enviar evento de cierre
                close_message = {
                    "type": "session.update",
                    "session": {
                        "instructions": None
                    }
                }
                await self.websocket.send(json.dumps(close_message))
                await self.websocket.close()
            except Exception as e:
                logger.error(f"Error closing session: {e}")

