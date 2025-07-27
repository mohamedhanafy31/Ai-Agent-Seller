"""
Person Tracking API schemas.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class TrackingRequest(BaseModel):
    """Tracking analysis request schema."""
    confidence_threshold: Optional[float] = Field(0.25, ge=0.1, le=1.0, description="Detection confidence threshold")
    max_tracks: Optional[int] = Field(100, ge=1, le=1000, description="Maximum number of tracks")
    
    class Config:
        schema_extra = {
            "example": {
                "confidence_threshold": 0.25,
                "max_tracks": 50
            }
        }


class BoundingBox(BaseModel):
    """Bounding box schema."""
    x1: float = Field(..., description="Top-left X coordinate")
    y1: float = Field(..., description="Top-left Y coordinate") 
    x2: float = Field(..., description="Bottom-right X coordinate")
    y2: float = Field(..., description="Bottom-right Y coordinate")
    confidence: Optional[float] = Field(None, ge=0, le=1)


class PersonTrack(BaseModel):
    """Person track schema."""
    track_id: int = Field(..., description="Unique track identifier")
    bbox: BoundingBox = Field(..., description="Bounding box coordinates")
    frame_number: int = Field(..., description="Frame number")
    timestamp: Optional[float] = Field(None, description="Timestamp in video")
    confidence: float = Field(..., ge=0, le=1, description="Track confidence")


class TrackingResult(BaseModel):
    """Tracking analysis result schema."""
    session_id: str = Field(..., description="Tracking session ID")
    video_info: Dict[str, Any] = Field(..., description="Video metadata")
    tracks: List[PersonTrack] = Field(..., description="Detected person tracks")
    total_frames: int = Field(..., description="Total frames processed")
    processing_time: float = Field(..., description="Total processing time")
    fps: Optional[float] = Field(None, description="Video frames per second")
    
    class Config:
        schema_extra = {
            "example": {
                "session_id": "track_123",
                "video_info": {
                    "filename": "store_video.mp4",
                    "duration": 30.0,
                    "resolution": "1920x1080"
                },
                "tracks": [
                    {
                        "track_id": 1,
                        "bbox": {"x1": 100, "y1": 150, "x2": 200, "y2": 400, "confidence": 0.95},
                        "frame_number": 1,
                        "timestamp": 0.033,
                        "confidence": 0.95
                    }
                ],
                "total_frames": 900,
                "processing_time": 15.3,
                "fps": 30.0
            }
        }


class TrackingSession(BaseModel):
    """Tracking session schema."""
    session_id: str = Field(..., description="Unique session identifier")
    status: str = Field(..., description="Session status: uploaded, processing, completed, failed")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(None)
    video_filename: Optional[str] = Field(None)
    error_message: Optional[str] = Field(None)
    result: Optional[TrackingResult] = Field(None)


class TrackingSummary(BaseModel):
    """Tracking session summary schema."""
    total_sessions: int
    active_sessions: int
    completed_sessions: int
    failed_sessions: int 