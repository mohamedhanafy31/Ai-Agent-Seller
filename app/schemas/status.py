"""
Person Status Analysis API schemas.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class StatusAnalysisRequest(BaseModel):
    """Status analysis request schema."""
    include_demographics: bool = Field(True, description="Include age and gender analysis")
    include_emotions: bool = Field(True, description="Include emotion analysis")
    confidence_threshold: Optional[float] = Field(0.5, ge=0.1, le=1.0)
    
    class Config:
        schema_extra = {
            "example": {
                "include_demographics": True,
                "include_emotions": True,
                "confidence_threshold": 0.5
            }
        }


class PersonStatus(BaseModel):
    """Person status analysis result schema."""
    mood: str = Field(..., description="Detected mood/emotion")
    gender: str = Field(..., description="Detected gender")
    age: str = Field(..., description="Estimated age group")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="Overall analysis confidence")
    processing_time: Optional[float] = Field(None, ge=0, description="Processing time in seconds")
    
    class Config:
        schema_extra = {
            "example": {
                "mood": "happy",
                "gender": "female", 
                "age": "adult",
                "confidence": 0.87,
                "processing_time": 1.5
            }
        }


class DetailedPersonStatus(BaseModel):
    """Detailed person status analysis schema."""
    demographics: Dict[str, Any] = Field(..., description="Age and gender analysis")
    emotions: Dict[str, float] = Field(..., description="Emotion probabilities")
    engagement: Dict[str, Any] = Field(..., description="Customer engagement metrics")
    metadata: Dict[str, Any] = Field(..., description="Analysis metadata")
    
    class Config:
        schema_extra = {
            "example": {
                "demographics": {
                    "age_group": "25-35",
                    "age_confidence": 0.82,
                    "gender": "female",
                    "gender_confidence": 0.94
                },
                "emotions": {
                    "happy": 0.65,
                    "neutral": 0.25,
                    "surprised": 0.08,
                    "sad": 0.02
                },
                "engagement": {
                    "attention_level": "high",
                    "interest_score": 0.78,
                    "dwell_time": 5.2
                },
                "metadata": {
                    "model_version": "v2.1",
                    "analysis_timestamp": "2024-01-20T10:30:00Z"
                }
            }
        }


class CameraCapture(BaseModel):
    """Camera capture request schema."""
    camera_id: Optional[int] = Field(0, description="Camera device ID")
    resolution: Optional[str] = Field("640x480", description="Capture resolution")
    quality: Optional[int] = Field(85, ge=10, le=100, description="Image quality (1-100)")


class ImageUploadResponse(BaseModel):
    """Image upload response schema."""
    upload_id: str = Field(..., description="Unique upload identifier")
    filename: str = Field(..., description="Original filename")
    file_size: int = Field(..., description="File size in bytes")
    image_info: Dict[str, Any] = Field(..., description="Image metadata")
    timestamp: datetime = Field(default_factory=datetime.utcnow) 