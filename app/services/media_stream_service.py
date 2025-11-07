import asyncio
import base64
import struct
from typing import Optional, AsyncGenerator
from fastapi import WebSocket
import logging

logger = logging.getLogger(__name__)

class MediaStreamService:
    """Servicio para manejar Media Streams de Twilio"""
    
    # Twilio Media Stream usa formato PCM16 (16-bit, 8000Hz, mono)
    SAMPLE_RATE = 8000
    CHANNELS = 1
    SAMPLE_WIDTH = 2  # 16-bit = 2 bytes
    
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        self.audio_buffer = bytearray()
        self.stream_sid = None  # Se establecerá cuando se reciba el mensaje de inicio
    
    async def receive_audio(self) -> AsyncGenerator[bytes, None]:
        """Recibir audio del Media Stream de Twilio"""
        try:
            while True:
                message = await self.websocket.receive_json()
                
                if message.get("event") == "media":
                    # Decodificar audio base64
                    payload = message.get("media", {}).get("payload")
                    if payload:
                        audio_data = base64.b64decode(payload)
                        yield audio_data
                
                elif message.get("event") == "start":
                    logger.info("Media stream started")
                
                elif message.get("event") == "stop":
                    logger.info("Media stream stopped")
                    break
                    
        except Exception as e:
            logger.error(f"Error receiving audio: {e}")
            raise
    
    async def send_audio(self, audio_data: bytes):
        """Enviar audio al Media Stream de Twilio"""
        try:
            if not self.stream_sid:
                logger.warning("Stream SID not set, cannot send audio")
                return
            
            # Codificar audio en base64
            payload = base64.b64encode(audio_data).decode('utf-8')
            
            message = {
                "event": "media",
                "streamSid": self.stream_sid,
                "media": {
                    "payload": payload
                }
            }
            
            await self.websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending audio: {e}")
            raise
    
    def convert_pcm_to_linear16(self, pcm_data: bytes) -> bytes:
        """Convertir PCM a formato linear16 si es necesario"""
        # Twilio ya usa PCM16, así que normalmente no hay conversión necesaria
        return pcm_data
    
    def convert_linear16_to_pcm(self, linear16_data: bytes) -> bytes:
        """Convertir linear16 a PCM si es necesario"""
        # OpenAI Realtime usa PCM16, compatible con Twilio
        return linear16_data

