"""
Chat API schemas for request/response validation.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Chat message request schema."""
    message: str = Field(..., min_length=1, max_length=1000, description="User message in Arabic")
    session_id: Optional[str] = Field(None, description="Optional session ID for context")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "أريد شراء قميص أزرق",
                "session_id": "sess_123"
            }
        }


class ChatResponse(BaseModel):
    """Chat response schema."""
    response: str = Field(..., description="AI response in Arabic")
    session_id: str = Field(..., description="Session ID for tracking")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="Response confidence")
    
    class Config:
        schema_extra = {
            "example": {
                "response": "عندنا قمصان زرقاء جميلة في المتجر",
                "session_id": "sess_123",
                "timestamp": "2024-01-20T10:30:00Z",
                "processing_time": 1.2,
                "confidence": 0.95
            }
        }


class ChatSession(BaseModel):
    """Chat session schema."""
    session_id: str = Field(..., description="Unique session identifier")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    message_count: int = Field(default=0, ge=0)
    is_active: bool = Field(default=True)
    
    class Config:
        schema_extra = {
            "example": {
                "session_id": "sess_123",
                "created_at": "2024-01-20T10:00:00Z",
                "last_activity": "2024-01-20T10:30:00Z",
                "message_count": 5,
                "is_active": True
            }
        }


class ProductInfo(BaseModel):
    """Product information schema."""
    id: int
    name: str
    price: float
    stock: int
    category: str
    store: str
    
    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "name": "قميص أزرق",
                "price": 150.0,
                "stock": 25,
                "category": "قمصان",
                "store": "المتجر الرئيسي"
            }
        } 