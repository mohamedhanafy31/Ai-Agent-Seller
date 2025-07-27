"""
Configuration management for AI Agent Seller Backend.
"""

import os
import secrets
from typing import Any, Dict, Optional, Union
from pydantic import PostgresDsn, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    SERVER_NAME: str = "AI Agent Seller"
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    BACKEND_CORS_ORIGINS: list = ["*"]  # Configure appropriately for production
    
    # Database Configuration
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "Ma3172003"
    POSTGRES_DB: str = "selling"
    POSTGRES_PORT: str = "5432"
    DATABASE_URL: Optional[PostgresDsn] = None
    
    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        
        # Build the database URL manually for compatibility
        postgres_user = values.get("POSTGRES_USER")
        postgres_password = values.get("POSTGRES_PASSWORD")
        postgres_server = values.get("POSTGRES_SERVER")
        postgres_port = values.get("POSTGRES_PORT")
        postgres_db = values.get("POSTGRES_DB")
        
        return f"postgresql+psycopg2://{postgres_user}:{postgres_password}@{postgres_server}:{postgres_port}/{postgres_db}"
    
    # AI Model Configuration
    USE_GPU: bool = True
    CUDA_VISIBLE_DEVICES: str = "0"
    MODEL_CACHE_DIR: str = "./models"
    
    # Whisper STT Configuration
    WHISPER_MODEL: str = "openai/whisper-large-v3-turbo"
    WHISPER_LANGUAGE: str = "ar"
    
    # TTS Configuration
    TTS_MODEL: str = "tts_models/multilingual/multi-dataset/xtts_v2"
    TTS_SPEAKER_WAV: str = "assets/audio/_7JpEjF2Vyk.wav"
    
    # YOLO Tracking Configuration
    YOLO_MODEL_PATH: str = "assets/models/yolov11x-person-mot20val-crowdhuman.pt"
    REID_MODEL_PATH: str = "assets/models/fine_tuned_model_epoch_32.pth"
    
    # Ollama Configuration
    OLLAMA_ENDPOINT: str = "http://localhost:11434/api/generate"
    OLLAMA_MODEL: str = "gemma3:4b"
    OLLAMA_VISION_MODEL: str = "gemma3:4b"
    
    # File Upload Configuration
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_AUDIO_EXTENSIONS: set = {".wav", ".mp3", ".m4a", ".webm", ".mp4"}
    ALLOWED_VIDEO_EXTENSIONS: set = {".mp4", ".avi", ".mov", ".mkv"}
    ALLOWED_IMAGE_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".bmp", ".gif"}
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "backend.log"
    
    # Redis Configuration (for future caching)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    
    @validator("DEBUG", pre=True)
    def set_debug_from_env(cls, v: Union[bool, str]) -> bool:
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings 