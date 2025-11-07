from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import users, properties, inquiries, voice, favorites, webhooks

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API para bot de voz Twilio que conecta inquilinos y propietarios de propiedades",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
app.include_router(users.router, prefix=settings.API_V1_STR)
app.include_router(properties.router, prefix=settings.API_V1_STR)
app.include_router(inquiries.router, prefix=settings.API_V1_STR)
app.include_router(voice.router, prefix=settings.API_V1_STR)
app.include_router(favorites.router, prefix=settings.API_V1_STR)
app.include_router(webhooks.router)  # Webhooks sin prefijo /api/v1

@app.get("/")
def root():
    """Endpoint raíz"""
    return {
        "message": "Bienvenido a la API de Twilio Voice AI Assistant",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

