"""
Speech-to-Text API schemas.
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class TranscriptionRequest(BaseModel):
    """STT transcription request schema."""
    language: str = Field(default="ar", description="Target language for transcription")
    model: Optional[str] = Field(None, description="Specific model to use")
    
    class Config:
        schema_extra = {
            "example": {
                "language": "ar",
                "model": "whisper-large-v3-turbo"
            }
        }


class TranscriptionResponse(BaseModel):
    """STT transcription response schema."""
    text: str = Field(..., description="Transcribed text")
    language: str = Field(..., description="Detected/specified language")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="Transcription confidence")
    duration: Optional[float] = Field(None, ge=0, description="Audio duration in seconds")
    processing_time: Optional[float] = Field(None, ge=0, description="Processing time in seconds")
    
    class Config:
        schema_extra = {
            "example": {
                "text": "أريد شراء حذاء رياضي",
                "language": "ar",
                "confidence": 0.92,
                "duration": 3.5,
                "processing_time": 1.2
            }
        }


class AudioInfo(BaseModel):
    """Audio file information schema."""
    filename: str
    file_size: int
    duration: Optional[float] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    format: Optional[str] = None 