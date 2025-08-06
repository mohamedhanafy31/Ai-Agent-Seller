"""
AI Model Management Service.

Handles loading, caching, and management of all AI models.
"""

import os
import asyncio
from typing import Optional, Dict, Any
from pathlib import Path

import torch
from loguru import logger

from app.core.config import get_settings
from app.core.exceptions import ModelLoadError, ExternalServiceError

settings = get_settings()


class ModelManager:
    """Centralized AI model management."""
    
    def __init__(self):
        self.whisper_model = None
        self.tts_model = None
        self.tts_streamer = None
        self.yolo_model = None
        self.tracker_instance = None
        self.ollama_available = False
        self.device = "cuda" if torch.cuda.is_available() and settings.USE_GPU else "cpu"
        self._model_status: Dict[str, bool] = {}
        
        logger.info(f"ModelManager initialized with device: {self.device}")
    
    async def initialize_all_models(self) -> None:
        """Initialize all AI models."""
        logger.info("Starting model initialization...")
        
        # Track which models failed to load
        failed_models = []
        
        try:
            # Initialize models in parallel where possible
            results = await asyncio.gather(
                self._load_whisper_model(),
                self._load_tts_model(),
                self._check_ollama_availability(),
                return_exceptions=True
            )
            
            # Check results and log failures
            model_names = ["whisper", "tts", "ollama"]
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Failed to load {model_names[i]}: {str(result)}")
                    failed_models.append(model_names[i])
                    self._model_status[model_names[i]] = False
                else:
                    logger.info(f"✅ {model_names[i]} initialized successfully")
            
            # These require sequential loading due to dependencies
            try:
                await self._load_tracking_models()
                logger.info("✅ Tracking models initialized successfully")
            except Exception as e:
                logger.error(f"Failed to load tracking models: {str(e)}")
                failed_models.extend(["yolo", "tracker"])
                self._model_status["yolo"] = False
                self._model_status["tracker"] = False
            
            if failed_models:
                logger.warning(f"⚠️ Some models failed to load: {failed_models}")
                logger.info("Models will be loaded on first request")
            else:
                logger.info("✅ All models initialized successfully")
            
        except Exception as e:
            logger.error(f"Model initialization failed: {str(e)}")
            # Don't raise - let the application start with degraded functionality
            logger.warning("⚠️ Starting with degraded functionality - models will be loaded on first request")
    
    async def _load_whisper_model(self) -> None:
        """Load Whisper model for speech-to-text."""
        try:
            logger.info("Loading Whisper model...")
            
            from transformers import pipeline
            
            self.whisper_model = pipeline(
                "automatic-speech-recognition",
                model=settings.WHISPER_MODEL,
                generate_kwargs={"language": settings.WHISPER_LANGUAGE},
                device=0 if self.device == "cuda" else -1
            )
            
            self._model_status["whisper"] = True
            logger.info("✅ Whisper model loaded successfully")
            return None
            
        except Exception as e:
            self._model_status["whisper"] = False
            logger.error(f"❌ Failed to load Whisper model: {str(e)}")
            return e
    
    async def _load_tts_model(self) -> None:
        """Load XTTS-v2 model for text-to-speech."""
        try:
            logger.info("Loading TTS model...")
            
            from TTS.api import TTS
            
            self.tts_model = TTS(
                settings.TTS_MODEL,
                gpu=self.device == "cuda"
            )
            
            # Initialize TTS streamer if speaker file exists
            speaker_wav_path = Path(settings.TTS_SPEAKER_WAV)
            if speaker_wav_path.exists():
                from app.services.tts_service import TTSStreamer
                self.tts_streamer = TTSStreamer(self.tts_model, str(speaker_wav_path))
                logger.info("✅ TTS model and streamer loaded successfully")
            else:
                logger.warning(f"⚠️ Speaker reference file {settings.TTS_SPEAKER_WAV} not found")
            
            self._model_status["tts"] = True
            return None
            
        except Exception as e:
            self._model_status["tts"] = False
            logger.error(f"❌ Failed to load TTS model: {str(e)}")
            return e
    
    async def _load_tracking_models(self) -> None:
        """Load YOLO and BoostTrack models for person tracking."""
        try:
            logger.info("Loading tracking models...")
            
            # Check for model files
            yolo_path = Path(settings.YOLO_MODEL_PATH)
            reid_path = Path(settings.REID_MODEL_PATH)
            
            if not yolo_path.exists():
                logger.warning(f"⚠️ YOLO model file {settings.YOLO_MODEL_PATH} not found")
                self._model_status["yolo"] = False
                self._model_status["tracker"] = False
                return Exception(f"YOLO model file {settings.YOLO_MODEL_PATH} not found")
            
            # Load YOLO model
            from ultralytics import YOLO
            self.yolo_model = YOLO(str(yolo_path))
            
            # Initialize tracking service
            from app.services.tracking_service import TrackingService
            self.tracker_instance = TrackingService(self)
            
            self._model_status["yolo"] = True
            self._model_status["tracker"] = True
            logger.info(f"✅ Tracking models loaded with: {settings.YOLO_MODEL_PATH}")
            return None
            
        except Exception as e:
            self._model_status["yolo"] = False
            self._model_status["tracker"] = False
            logger.error(f"❌ Failed to load tracking models: {str(e)}")
            return e
    
    async def _check_ollama_availability(self) -> None:
        """Check if Ollama service is available."""
        try:
            import aiohttp
            
            # Test Ollama connection
            async with aiohttp.ClientSession() as session:
                tags_url = settings.OLLAMA_ENDPOINT.replace("/api/generate", "/api/tags")
                async with session.get(tags_url, timeout=5) as response:
                    if response.status == 200:
                        self.ollama_available = True
                        self._model_status["ollama"] = True
                        logger.info("✅ Ollama service is available")
                        return None
                    else:
                        self.ollama_available = False
                        self._model_status["ollama"] = False
                        logger.warning("⚠️ Ollama service is not responding correctly")
                        return Exception("Ollama service not responding correctly")
        
        except Exception as e:
            self.ollama_available = False
            self._model_status["ollama"] = False
            logger.warning(f"⚠️ Ollama not available: {str(e)}")
            return e
    
    def get_model_status(self) -> Dict[str, Any]:
        """Get the status of all models."""
        return {
            "device": self.device,
            "models": self._model_status,
            "gpu_available": torch.cuda.is_available(),
            "cuda_device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
        }
    
    def is_model_available(self, model_name: str) -> bool:
        """Check if a specific model is available."""
        return self._model_status.get(model_name, False)
    
    async def cleanup(self) -> None:
        """Clean up model resources."""
        logger.info("Cleaning up model resources...")
        
        # Clear GPU cache if using CUDA
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        # Additional cleanup can be added here
        logger.info("✅ Model cleanup completed")


# Global model manager instance
model_manager = ModelManager()


def get_model_manager() -> ModelManager:
    """Get the global model manager instance."""
    return model_manager 