from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Request, Form, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import Dict, Optional
import json
import asyncio
import logging
from twilio.request_validator import RequestValidator
from twilio.twiml.voice_response import VoiceResponse, Start, Stream

from app.core.config import settings
from app.db.session import get_db
from app.services.openai_realtime_service import OpenAIRealtimeService
from app.services.media_stream_service import MediaStreamService
from app.services import voice_service
from app.models.user import UserRole

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/webhook", tags=["webhooks"])

# Almacenar conexiones activas
active_connections: Dict[str, Dict] = {}

def validate_twilio_request(request: Request) -> bool:
    """Validar que la petición viene de Twilio"""
    validator = RequestValidator(settings.TWILIO_AUTH_TOKEN)
    signature = request.headers.get("X-Twilio-Signature", "")
    url = str(request.url)
    params = dict(request.form())
    
    return validator.validate(url, params, signature)

@router.post("/voice/connect")
async def voice_connect(
    request: Request,
    CallSid: str = Form(...),
    From: str = Form(...),
    To: str = Form(...),
    CallStatus: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Webhook llamado cuando se conecta una llamada entrante.
    Configura el Media Stream para audio bidireccional.
    """
    # Validar request de Twilio (opcional en desarrollo)
    # if not validate_twilio_request(request):
    #     raise HTTPException(status_code=403, detail="Invalid Twilio signature")
    
    logger.info(f"Call connected: {CallSid} from {From}")
    
    # Crear o actualizar sesión de llamada
    session = voice_service.create_or_update_session(
        db=db,
        call_sid=CallSid,
        phone_number=From,
        role=None  # Se determinará durante la conversación
    )
    
    # Obtener URL base (usar NGROK_URL si está disponible, sino BASE_URL)
    base_url = settings.NGROK_URL or settings.BASE_URL
    # Asegurar que la URL sea WSS para WebSocket
    if base_url.startswith("http://"):
        base_url = base_url.replace("http://", "wss://")
    elif base_url.startswith("https://"):
        base_url = base_url.replace("https://", "wss://")
    elif not base_url.startswith("wss://"):
        base_url = f"wss://{base_url}"
    
    media_stream_url = f"{base_url}/voice/media"

    # Generar TwiML para iniciar Media Stream
    response = VoiceResponse()
    
    # Mensaje de bienvenida
    response.say(
        "Hola, bienvenido al asistente de propiedades. Conectando con nuestro asistente virtual.",
        language="es-MX"
    )
    
    # Iniciar Media Stream
    start = Start()
    start.stream(url=media_stream_url)
    response.append(start)
    
    # Mantener la llamada activa
    response.pause(length=10)  # Máximo 1 hora
    
    return Response(content=str(response), media_type="application/xml")

@router.websocket("/voice/media")
async def voice_media_stream(
    websocket: WebSocket,
    CallSid: str = None
):
    """
    WebSocket para Media Stream bidireccional.
    Conecta Twilio Media Stream con OpenAI Realtime API.
    """
    await websocket.accept()
    logger.info(f"Media stream WebSocket connected")
    
    # Obtener información de la llamada del primer mensaje
    try:
        first_message = await websocket.receive_json()
        logger.info(f"First message: {first_message}")
        
        if first_message.get("event") == "start":
            stream_sid = first_message.get("start", {}).get("streamSid")
            call_info = first_message.get("start", {}).get("call", {})
            phone_number = call_info.get("from")
            call_sid = call_info.get("callSid") or CallSid
            
            logger.info(f"Stream SID: {stream_sid}, Call SID: {call_sid}, From: {phone_number}")
        else:
            await websocket.close()
            return
    except Exception as e:
        logger.error(f"Error receiving initial message: {e}")
        await websocket.close()
        return
    
    # Obtener sesión de base de datos
    from app.db.session import SessionLocal
    db = SessionLocal()
    
    try:
        # Crear servicios
        media_service = MediaStreamService(websocket)
        media_service.stream_sid = stream_sid  # Guardar stream_sid para enviar mensajes
        
        realtime_service = OpenAIRealtimeService(db, call_sid, phone_number)
        
        # Crear sesión de OpenAI Realtime
        session_result = await realtime_service.create_session()
        if session_result.get("status") != "connected":
            logger.error(f"Failed to create OpenAI session: {session_result}")
            await websocket.close()
            return
        
        # Almacenar conexión
        active_connections[call_sid] = {
            "websocket": websocket,
            "media_service": media_service,
            "realtime_service": realtime_service,
            "stream_sid": stream_sid,
            "db": db
        }
        
        # Tareas concurrentes para manejar audio bidireccional
        async def receive_from_twilio():
            """Recibir audio de Twilio y enviarlo a OpenAI"""
            try:
                # Continuar recibiendo mensajes después del inicial
                while True:
                    try:
                        message = await asyncio.wait_for(websocket.receive_json(), timeout=30.0)
                        
                        if message.get("event") == "media":
                            import base64
                            payload = message.get("media", {}).get("payload")
                            if payload:
                                audio_data = base64.b64decode(payload)
                                await realtime_service.send_audio(audio_data)
                        
                        elif message.get("event") == "stop":
                            logger.info("Media stream stopped by Twilio")
                            break
                    except asyncio.TimeoutError:
                        # Timeout, continuar esperando
                        continue
                        
            except WebSocketDisconnect:
                logger.info("Twilio WebSocket disconnected")
            except Exception as e:
                logger.error(f"Error receiving from Twilio: {e}")
        
        async def send_to_twilio():
            """Recibir audio de OpenAI y enviarlo a Twilio"""
            try:
                async for audio_data in realtime_service.get_audio_response():
                    # Enviar audio a Twilio
                    await media_service.send_audio(audio_data)
            except Exception as e:
                logger.error(f"Error sending to Twilio: {e}")
        
        # Ejecutar tareas concurrentemente
        await asyncio.gather(
            receive_from_twilio(),
            send_to_twilio(),
            return_exceptions=True
        )
        
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for call: {call_sid}")
    except Exception as e:
        logger.error(f"Error in media stream: {e}")
    finally:
        # Limpiar conexión
        if call_sid in active_connections:
            await active_connections[call_sid]["realtime_service"].close()
            db.close()
            del active_connections[call_sid]
        logger.info(f"Media stream closed for call: {call_sid}")

@router.post("/voice/status")
async def voice_status(
    request: Request,
    CallSid: str = Form(...),
    CallStatus: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Webhook llamado cuando cambia el estado de la llamada.
    """
    logger.info(f"Call status update: {CallSid} - {CallStatus}")
    
    # Actualizar estado de la sesión
    if CallStatus in ["completed", "busy", "no-answer", "failed", "canceled"]:
        voice_service.complete_session(db, CallSid)
        
        # Limpiar conexión activa si existe
        if CallSid in active_connections:
            await active_connections[CallSid]["realtime_service"].close()
            del active_connections[CallSid]
    
    return Response(content="OK", media_type="text/plain")


