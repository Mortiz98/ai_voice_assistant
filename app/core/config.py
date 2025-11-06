import os
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Twilio Voice AI Assistant"

    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "myuser")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "mypassword")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "ai_assistant")
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    # Twilio Configuration
    TWILIO_ACCOUNT_SID: Optional[str] = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN: Optional[str] = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_PHONE_NUMBER: Optional[str] = os.getenv("TWILIO_PHONE_NUMBER")
    TWILIO_WEBHOOK_URL: Optional[str] = os.getenv("TWILIO_WEBHOOK_URL")

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            username=values.data.get("POSTGRES_USER"),
            password=values.data.get("POSTGRES_PASSWORD"),
            host=values.data.get("POSTGRES_SERVER"),
            path=f"{values.data.get('POSTGRES_DB') or ''}",
        )
 
 
settings= Settings()
