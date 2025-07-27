"""
AI Agent Seller Backend - Test Version (No AI Models)

A minimal version for testing the API structure without loading AI models.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime

# Mock settings for testing
class MockSettings:
    API_V1_STR = "/api/v1"
    SERVER_HOST = "0.0.0.0"
    SERVER_PORT = 8000
    BACKEND_CORS_ORIGINS = ["*"]
    ENVIRONMENT = "development"
    DEBUG = True

settings = MockSettings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management for test version."""
    print("🚀 Starting AI Agent Seller Backend (Test Mode)...")
    print("⚠️  Running in test mode - AI models not loaded")
    yield
    print("🛑 Shutting down AI Agent Seller Backend...")

# Create FastAPI application
app = FastAPI(
    title="AI Agent Seller Backend (Test Mode)",
    description="Test version without AI models loaded",
    version="2.0.0-test",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """API Information for test mode."""
    return {
        "message": "AI Agent Seller Backend (Test Mode)",
        "version": "2.0.0-test",
        "status": "operational",
        "environment": "test",
        "docs": "/docs",
        "redoc": "/redoc",
        "api": settings.API_V1_STR,
        "health": "/health",
        "note": "Running in test mode - AI models not loaded",
        "services": {
            "chat": {
                "name": "Arabic Conversational AI (Mock)",
                "endpoint": f"{settings.API_V1_STR}/chat",
                "status": "mock"
            },
            "stt": {
                "name": "Speech-to-Text (Mock)",
                "endpoint": f"{settings.API_V1_STR}/stt",
                "status": "mock"
            },
            "tts": {
                "name": "Text-to-Speech (Mock)",
                "endpoint": f"{settings.API_V1_STR}/tts",
                "status": "mock"
            },
            "tracking": {
                "name": "Person Tracking (Mock)",
                "endpoint": f"{settings.API_V1_STR}/tracking",
                "status": "mock"
            },
            "status": {
                "name": "Person Status Analysis (Mock)",
                "endpoint": f"{settings.API_V1_STR}/status",
                "status": "mock"
            }
        }
    }

@app.get("/health")
async def health_check():
    """System health check for test mode."""
    return {
        "status": "healthy",
        "version": "2.0.0-test",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "environment": "test",
        "models": {
            "device": "cpu",
            "gpu_available": False,
            "cuda_device_count": 0,
            "models_loaded": {
                "whisper": False,
                "tts": False,
                "ollama": False,
                "yolo": False,
                "tracker": False
            }
        },
        "services": {
            "chat": False,
            "stt": False,
            "tts": False,
            "tracking": False,
            "status_analysis": False
        },
        "note": "Test mode - AI models not loaded"
    }

# Mock API endpoints
@app.get("/api/v1/chat/")
async def chat_info():
    """Mock chat service information."""
    return {
        "name": "Arabic Chat Interface (Mock)",
        "description": "Mock conversational AI for testing",
        "version": "2.0.0-test",
        "status": "mock",
        "note": "This is a mock endpoint for testing"
    }

@app.post("/api/v1/chat/message")
async def chat_message():
    """Mock chat message endpoint."""
    return {
        "response": "هذا رد تجريبي للاختبار (This is a test response)",
        "session_id": "test_session_123",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "processing_time": 0.1,
        "confidence": 0.95,
        "status": "mock"
    }

@app.get("/api/v1/stt/")
async def stt_info():
    """Mock STT service information."""
    return {
        "name": "Speech-to-Text (Mock)",
        "description": "Mock speech recognition for testing",
        "status": "mock"
    }

@app.get("/api/v1/tts/")
async def tts_info():
    """Mock TTS service information."""
    return {
        "name": "Text-to-Speech (Mock)",
        "description": "Mock speech synthesis for testing",
        "status": "mock"
    }

@app.get("/api/v1/tracking/")
async def tracking_info():
    """Mock tracking service information."""
    return {
        "name": "Person Tracking (Mock)",
        "description": "Mock person tracking for testing",
        "status": "mock"
    }

@app.get("/api/v1/status/")
async def status_info():
    """Mock status analysis service information."""
    return {
        "name": "Person Status Analysis (Mock)",
        "description": "Mock person analysis for testing",
        "status": "mock"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main_test:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.DEBUG,
    ) 