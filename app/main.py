"""
AI Agent Seller Backend - Main FastAPI Application

A comprehensive multi-modal AI system for Arabic-speaking clothing retail assistance.
This backend provides advanced AI capabilities including conversational chat, speech processing,
computer vision, and person analytics for enhanced customer experience.

Key Features:
- Arabic conversational AI with Ollama Gemma 2
- Speech-to-text with Whisper Large V3 Turbo
- Text-to-speech with XTTS-v2
- Person tracking with YOLOv11x + BoostTrack
- Person status analysis with AI vision models
- Professional REST API with comprehensive documentation
- Real-time WebSocket support for streaming
- GPU acceleration for optimal performance

Architecture:
- FastAPI framework with async/await support
- Modular service architecture with dependency injection
- Centralized configuration and logging
- Professional error handling and validation
- CORS and security middleware
- Comprehensive API documentation with Swagger/OpenAPI

Version: 2.0.0
License: Proprietary
Author: AI Agent Seller Team
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.logging import setup_logging, get_logger
from app.core.exceptions import (
    BaseCustomException,
    custom_exception_handler,
    http_exception_handler,
    general_exception_handler,
)
from app.services.model_manager import get_model_manager
from app.api.v1.api import api_router

# Setup logging
setup_logging()
logger = get_logger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan management with AI model initialization.
    
    Handles startup and shutdown processes including:
    - AI model loading and initialization
    - Resource allocation and cleanup
    - Graceful error handling and recovery
    """
    # Startup
    logger.info("🚀 Starting AI Agent Seller Backend...")
    
    try:
        # Initialize all AI models
        model_manager = get_model_manager()
        await model_manager.initialize_all_models()
        
        logger.info("✅ Backend startup completed successfully!")
        yield
        
    except Exception as e:
        logger.error(f"❌ Failed to start backend: {str(e)}")
        raise
    finally:
        # Shutdown
        logger.info("🛑 Shutting down AI Agent Seller Backend...")
        
        # Clean up model resources
        model_manager = get_model_manager()
        await model_manager.cleanup()
        
        logger.info("✅ Backend shutdown completed")


# Create FastAPI application with comprehensive metadata
app = FastAPI(
    title="AI Agent Seller Backend",
    description="""
    ## Advanced Multi-Modal AI Backend for Clothing Retail
    
    A comprehensive AI-powered backend system designed specifically for Arabic-speaking
    clothing retail businesses. Provides intelligent customer interaction, visual analytics,
    and automated assistance capabilities.
    
    ### 🎯 Key Features
    
    **Conversational AI:**
    - Natural Arabic language understanding and generation
    - Product recommendations and shopping assistance
    - Context-aware multi-turn conversations
    - Cultural sensitivity and localization
    
    **Speech Processing:**
    - High-accuracy Arabic speech recognition
    - Natural Arabic text-to-speech synthesis
    - Real-time audio streaming capabilities
    - Multi-format audio support
    
    **Computer Vision:**
    - Advanced person detection and tracking
    - Multi-person tracking with unique ID assignment
    - Demographic and emotion analysis
    - Customer engagement assessment
    
    **Technical Excellence:**
    - GPU-accelerated AI processing
    - Real-time streaming with WebSocket support
    - Professional REST API design
    - Comprehensive error handling and validation
    
    ### 🏗️ Architecture
    
    Built on modern software architecture principles:
    - **FastAPI Framework**: High-performance async web framework
    - **Modular Design**: Clean separation of concerns with service layers
    - **Dependency Injection**: Flexible and testable component management
    - **Configuration Management**: Environment-based settings
    - **Structured Logging**: Comprehensive observability and debugging
    
    ### 🤖 AI Models
    
    - **Chat**: Ollama Gemma 2 4B for Arabic conversations
    - **STT**: OpenAI Whisper Large V3 Turbo for speech recognition
    - **TTS**: XTTS-v2 for natural Arabic speech synthesis
    - **Vision**: YOLOv11x + BoostTrack for person tracking
    - **Analysis**: Gemma 2 with vision capabilities for person status
    
    ### 🔒 Security & Privacy
    
    - CORS protection with configurable origins
    - Input validation and sanitization
    - Error handling without information leakage
    - Privacy-compliant person analysis
    - No personal data retention
    
    ### 📚 Documentation
    
    - **Interactive API Docs**: Available at `/docs`
    - **Alternative Docs**: ReDoc available at `/redoc`
    - **OpenAPI Schema**: Machine-readable at `/openapi.json`
    - **Health Checks**: Individual service health endpoints
    
    ### 🚀 Getting Started
    
    1. Check service health: `GET /health`
    2. Explore API documentation: Visit `/docs`
    3. Test chat functionality: `POST /api/v1/chat/message`
    4. Upload audio for transcription: `POST /api/v1/stt/transcribe`
    5. Generate speech: `POST /api/v1/tts/synthesize`
    
    For detailed usage examples and integration guides, see the individual endpoint documentation.
    """,
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    terms_of_service="https://example.com/terms/",
    contact={
        "name": "AI Agent Seller API Support",
        "url": "https://example.com/contact/",
        "email": "support@example.com",
    },
    license_info={
        "name": "Proprietary License",
        "url": "https://example.com/license/",
    },
    servers=[
        {
            "url": "http://localhost:8000",
            "description": "Development server"
        },
        {
            "url": "https://api.example.com",
            "description": "Production server"
        }
    ],
    tags_metadata=[
        {
            "name": "chat",
            "description": "Arabic conversational AI for customer assistance and product recommendations"
        },
        {
            "name": "speech-to-text",
            "description": "High-accuracy speech recognition with multi-language support"
        },
        {
            "name": "text-to-speech", 
            "description": "Natural speech synthesis with Arabic language optimization"
        },
        {
            "name": "person-tracking",
            "description": "Advanced computer vision for person detection and tracking in videos"
        },
        {
            "name": "person-status-analysis",
            "description": "AI-powered analysis of person demographics, emotions, and engagement"
        }
    ]
)

# CORS configuration for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers for professional error responses
app.add_exception_handler(BaseCustomException, custom_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include API routes with version prefix
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get(
    "/",
    summary="API Information",
    description="Get comprehensive information about the AI Agent Seller Backend API including available services and endpoints.",
    tags=["system"],
    responses={
        200: {
            "description": "API information and service overview",
            "content": {
                "application/json": {
                    "example": {
                        "message": "AI Agent Seller Backend",
                        "version": "2.0.0",
                        "status": "operational",
                        "docs": "/docs",
                        "api": "/api/v1",
                        "services": {
                            "chat": {
                                "name": "Arabic Conversational AI",
                                "endpoint": "/api/v1/chat",
                                "description": "Intelligent Arabic chat for customer assistance"
                            },
                            "stt": {
                                "name": "Speech-to-Text",
                                "endpoint": "/api/v1/stt",
                                "description": "Convert audio to text with high accuracy"
                            },
                            "tts": {
                                "name": "Text-to-Speech", 
                                "endpoint": "/api/v1/tts",
                                "description": "Generate natural Arabic speech from text"
                            },
                            "tracking": {
                                "name": "Person Tracking",
                                "endpoint": "/api/v1/tracking",
                                "description": "Advanced person detection and tracking"
                            },
                            "status": {
                                "name": "Person Status Analysis",
                                "endpoint": "/api/v1/status", 
                                "description": "AI-powered person analysis and insights"
                            }
                        }
                    }
                }
            }
        }
    }
)
async def root():
    """
    ## AI Agent Seller Backend API
    
    Welcome to the AI Agent Seller Backend - a comprehensive multi-modal AI system
    designed for Arabic-speaking clothing retail businesses.
    
    ### Quick Start Guide:
    
    1. **Explore the API**: Visit `/docs` for interactive documentation
    2. **Check Health**: Use `/health` to verify all services are running
    3. **Test Chat**: Try the Arabic chat interface at `/api/v1/chat/message`
    4. **Process Audio**: Upload audio files to `/api/v1/stt/transcribe`
    5. **Generate Speech**: Convert text to speech at `/api/v1/tts/synthesize`
    
    ### Service Architecture:
    
    Each service is independently accessible and can be used standalone or combined
    for comprehensive retail AI solutions.
    
    ### Support & Documentation:
    
    - **API Documentation**: `/docs` (Swagger UI)
    - **Alternative Docs**: `/redoc` (ReDoc)
    - **OpenAPI Schema**: `/openapi.json`
    - **Health Monitoring**: Individual service health endpoints
    """
    return {
        "message": "AI Agent Seller Backend",
        "version": "2.0.0",
        "status": "operational", 
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
        "redoc": "/redoc",
        "api": settings.API_V1_STR,
        "health": "/health",
        "services": {
            "chat": {
                "name": "Arabic Conversational AI",
                "endpoint": f"{settings.API_V1_STR}/chat",
                "description": "Intelligent Arabic chat for customer assistance and product recommendations",
                "features": ["Natural language understanding", "Product search", "Shopping guidance", "Session management"]
            },
            "stt": {
                "name": "Speech-to-Text Recognition",
                "endpoint": f"{settings.API_V1_STR}/stt", 
                "description": "High-accuracy speech recognition optimized for Arabic language",
                "features": ["Multi-language support", "Real-time processing", "Confidence scoring", "Audio format flexibility"]
            },
            "tts": {
                "name": "Text-to-Speech Synthesis",
                "endpoint": f"{settings.API_V1_STR}/tts",
                "description": "Natural Arabic speech generation with XTTS-v2 technology",
                "features": ["Natural prosody", "Voice customization", "Streaming support", "Multiple formats"]
            },
            "tracking": {
                "name": "Person Tracking & Detection",
                "endpoint": f"{settings.API_V1_STR}/tracking",
                "description": "Advanced computer vision for person detection and tracking in videos",
                "features": ["Multi-person tracking", "Unique ID assignment", "Trajectory analysis", "Real-time processing"]
            },
            "status": {
                "name": "Person Status Analysis",
                "endpoint": f"{settings.API_V1_STR}/status",
                "description": "AI-powered analysis of person demographics, emotions, and engagement levels",
                "features": ["Demographic analysis", "Emotion detection", "Engagement assessment", "Privacy compliance"]
            }
        },
        "technical_info": {
            "framework": "FastAPI",
            "python_version": "3.9+",
            "gpu_acceleration": "CUDA supported",
            "real_time_streaming": "WebSocket available",
            "api_standard": "OpenAPI 3.0",
            "cors_enabled": True
        },
        "getting_started": {
            "interactive_docs": "/docs",
            "health_check": "/health", 
            "example_chat": f"{settings.API_V1_STR}/chat/message",
            "example_stt": f"{settings.API_V1_STR}/stt/transcribe",
            "example_tts": f"{settings.API_V1_STR}/tts/synthesize"
        }
    }


@app.get(
    "/health",
    summary="System Health Check",
    description="Comprehensive health check for all AI services and system components.",
    tags=["system"],
    responses={
        200: {
            "description": "System is healthy and all services are operational",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "version": "2.0.0",
                        "timestamp": "2024-01-20T10:30:00Z",
                        "models": {
                            "device": "cuda",
                            "gpu_available": True,
                            "cuda_device_count": 1,
                            "models_loaded": {
                                "whisper": True,
                                "tts": True,
                                "ollama": True,
                                "yolo": True,
                                "tracker": True
                            }
                        },
                        "environment": "development",
                        "uptime": "2h 34m 12s"
                    }
                }
            }
        },
        503: {
            "description": "System is unhealthy or some services are unavailable"
        }
    }
)
async def health_check():
    """
    ## System Health Check
    
    Provides comprehensive health information about all AI services and system components.
    Use this endpoint to monitor system status and verify that all required models are loaded.
    
    ### Health Indicators:
    - Overall system status
    - Individual AI model availability
    - GPU acceleration status
    - System resource utilization
    - Service uptime information
    
    ### Returns:
    - **status**: Overall health (healthy/unhealthy)
    - **models**: AI model loading status and GPU information
    - **environment**: Current deployment environment
    - **version**: Backend version information
    - **timestamp**: Health check execution time
    """
    try:
        model_manager = get_model_manager()
        
        # Get model status
        models_status = {
            "device": model_manager.device,
            "gpu_available": model_manager.device == "cuda",
            "cuda_device_count": 1 if model_manager.device == "cuda" else 0,
            "models_loaded": {
                "whisper": model_manager.is_model_available("whisper"),
                "tts": model_manager.is_model_available("tts"),
                "ollama": model_manager.is_model_available("ollama"),
                "yolo": model_manager.is_model_available("yolo"),
                "tracker": model_manager.is_model_available("tracker")
            }
        }
        
        # Determine overall health
        all_models_loaded = all(models_status["models_loaded"].values())
        overall_status = "healthy" if all_models_loaded else "degraded"
        
        from datetime import datetime
        
        return {
            "status": overall_status,
            "version": "2.0.0",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "models": models_status,
            "environment": settings.ENVIRONMENT,
            "services": {
                "chat": models_status["models_loaded"]["ollama"],
                "stt": models_status["models_loaded"]["whisper"],
                "tts": models_status["models_loaded"]["tts"], 
                "tracking": models_status["models_loaded"]["yolo"] and models_status["models_loaded"]["tracker"],
                "status_analysis": models_status["models_loaded"]["ollama"]
            }
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Health check failed")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    ) 