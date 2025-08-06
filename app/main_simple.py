"""
AI Agent Seller Backend - Simple FastAPI Application (for testing)

A simplified version that skips model initialization for testing startup issues.
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
from app.api.v1.api import api_router

# Setup logging
setup_logging()
logger = get_logger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Simplified application lifespan management - skips model initialization.
    """
    # Startup
    logger.info("🚀 Starting AI Agent Seller Backend (Simple Mode)...")
    
    try:
        logger.info("⏭️ Skipping model initialization for testing")
        logger.info("✅ Backend startup completed successfully!")
        yield
        
    except Exception as e:
        logger.error(f"❌ Failed to start backend: {str(e)}")
        yield
    finally:
        # Shutdown
        logger.info("🛑 Shutting down AI Agent Seller Backend...")
        logger.info("✅ Backend shutdown completed")


# Create FastAPI application
app = FastAPI(
    title="AI Agent Seller Backend (Simple Mode)",
    description="Simplified version for testing startup issues",
    version="2.0.0",
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

# Exception handlers
app.add_exception_handler(BaseCustomException, custom_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    """Simple root endpoint."""
    return {
        "message": "AI Agent Seller Backend (Simple Mode)",
        "version": "2.0.0",
        "status": "operational",
        "mode": "simple (no model initialization)",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """Simple health check."""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "mode": "simple",
        "models": {
            "whisper": False,
            "tts": False,
            "ollama": False,
            "yolo": False,
            "tracker": False
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main_simple:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    ) 