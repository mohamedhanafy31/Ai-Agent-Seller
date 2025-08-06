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


class STTStreamingRequest(BaseModel):
    """STT streaming request schema for WebSocket."""
    audio_data: str = Field(..., description="Base64 encoded audio chunk")
    chunk_index: int = Field(..., description="Sequential chunk number")
    is_final: bool = Field(default=False, description="Whether this is the final chunk")
    language: str = Field(default="ar", description="Target language for transcription")
    sample_rate: int = Field(default=16000, description="Audio sample rate")
    
    class Config:
        schema_extra = {
            "example": {
                "audio_data": "UklGRiQAAABXQVZFZm10IBAAAAABAAEA...",
                "chunk_index": 1,
                "is_final": False,
                "language": "ar",
                "sample_rate": 16000
            }
        }


class STTStreamingResponse(BaseModel):
    """STT streaming response schema for WebSocket."""
    type: str = Field(..., description="Response type: 'partial', 'final', 'error'")
    text: str = Field(default="", description="Transcribed text (partial or complete)")
    chunk_index: int = Field(..., description="Chunk index being processed")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="Transcription confidence")
    is_final: bool = Field(default=False, description="Whether this is the final result")
    message: Optional[str] = Field(None, description="Error message if type='error'")
    
    class Config:
        schema_extra = {
            "example": {
                "type": "partial",
                "text": "أريد شراء",
                "chunk_index": 1,
                "confidence": 0.85,
                "is_final": False
            }
        } 