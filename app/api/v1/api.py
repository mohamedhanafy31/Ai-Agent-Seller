"""
Main API router for v1 endpoints.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import chat, stt, tts, tracking, status

api_router = APIRouter()

# Include all endpoint routers with proper prefixes and tags
api_router.include_router(
    chat.router, 
    prefix="/chat", 
    tags=["chat"]
)

api_router.include_router(
    stt.router, 
    prefix="/stt", 
    tags=["speech-to-text"]
)

api_router.include_router(
    tts.router, 
    prefix="/tts", 
    tags=["text-to-speech"]
)

api_router.include_router(
    tracking.router, 
    prefix="/tracking", 
    tags=["person-tracking"]
)

api_router.include_router(
    status.router, 
    prefix="/status", 
    tags=["person-status"]
) 