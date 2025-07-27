#!/usr/bin/env python3
"""
AI Agent Seller Backend - Entry Point
Run this script to start the backend server.
"""

import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Now we can import the app
from app.main import app
from app.core.config import get_settings

if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    
    print("🚀 Starting AI Agent Seller Backend...")
    print(f"📍 Server: http://{settings.SERVER_HOST}:{settings.SERVER_PORT}")
    print(f"📚 API Docs: http://{settings.SERVER_HOST}:{settings.SERVER_PORT}/docs")
    print(f"🔄 Health Check: http://{settings.SERVER_HOST}:{settings.SERVER_PORT}/health")
    
    uvicorn.run(
        "app.main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True
    ) 