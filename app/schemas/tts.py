"""
Text-to-Speech API schemas.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class TTSRequest(BaseModel):
    """TTS synthesis request schema."""
    text: str = Field(..., min_length=1, max_length=1000, description="Text to synthesize")
    language: str = Field(default="ar", description="Target language")
    voice: Optional[str] = Field(None, description="Voice model to use")
    speed: Optional[float] = Field(1.0, ge=0.5, le=2.0, description="Speech speed multiplier")
    
    class Config:
        schema_extra = {
            "example": {
                "text": "مرحباً بكم في متجرنا",
                "language": "ar",
                "voice": "default",
                "speed": 1.0
            }
        }


class TTSResponse(BaseModel):
    """TTS synthesis response schema."""
    audio_url: Optional[str] = Field(None, description="URL to generated audio file")
    duration: Optional[float] = Field(None, ge=0, description="Audio duration in seconds")
    sample_rate: int = Field(default=22050, description="Audio sample rate")
    processing_time: Optional[float] = Field(None, ge=0, description="Processing time in seconds")
    
    class Config:
        schema_extra = {
            "example": {
                "audio_url": "/audio/output_12345.wav",
                "duration": 2.8,
                "sample_rate": 22050,
                "processing_time": 0.8
            }
        }


class TTSStreamingRequest(BaseModel):
    """TTS streaming request schema for WebSocket."""
    text: str = Field(..., min_length=1, max_length=1000)
    language: str = Field(default="ar")
    chunk_size: Optional[int] = Field(1024, ge=512, le=8192, description="Audio chunk size")


class TTSStreamingResponse(BaseModel):
    """TTS streaming response schema for WebSocket."""
    type: str = Field(..., description="Message type: 'audio_chunk', 'metadata', 'complete'")
    data: Optional[str] = Field(None, description="Base64 encoded audio data")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Audio metadata")
    chunk_index: Optional[int] = Field(None, description="Chunk sequence number")
    is_final: bool = Field(default=False, description="Whether this is the final chunk") 