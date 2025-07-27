"""
Dependency injection for FastAPI endpoints.
"""

from typing import Generator

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.services.model_manager import ModelManager, get_model_manager
from app.core.exceptions import ModelLoadError


def get_db() -> Generator:
    """Get database session."""
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_model_manager() -> ModelManager:
    """Get model manager instance."""
    from app.services.model_manager import get_model_manager as _get_model_manager
    return _get_model_manager()


def require_whisper_model(models: ModelManager = Depends(get_model_manager)) -> ModelManager:
    """Require Whisper STT model to be loaded."""
    if not models.is_model_available("whisper"):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Whisper speech recognition model is not available. Please check model loading."
        )
    return models


def require_tts_model(models: ModelManager = Depends(get_model_manager)) -> ModelManager:
    """Require TTS model to be loaded."""
    if not models.is_model_available("tts"):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="TTS model is not available. Please check model loading."
        )
    return models


def require_tracking_models(models: ModelManager = Depends(get_model_manager)) -> ModelManager:
    """Require both YOLO and tracker models to be loaded."""
    if not models.is_model_available("yolo"):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="YOLO detection model is not available. Please check model loading."
        )
    
    if not models.is_model_available("tracker"):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="BoostTrack tracking model is not available. Please check model loading."
        )
    
    return models


def require_ollama_service(models: ModelManager = Depends(get_model_manager)) -> ModelManager:
    """Require Ollama service to be available."""
    if not models.is_model_available("ollama"):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Ollama service is not available. Please check Ollama server status."
        )
    return models


def require_database(db: Session = Depends(get_db)) -> Session:
    """Require database connection."""
    return db 