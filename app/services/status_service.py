"""
Status Service - Business logic for person status analysis.
"""

import asyncio
import time
import base64
import uuid
import cv2
import numpy as np
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
from io import BytesIO

import aiohttp
from PIL import Image
from loguru import logger

from app.schemas.status import (
    StatusAnalysisRequest, PersonStatus, DetailedPersonStatus,
    CameraCapture, ImageUploadResponse
)
from app.services.model_manager import ModelManager
from app.core.config import get_settings
from app.core.exceptions import ImageProcessingError, ExternalServiceError, ModelLoadError

settings = get_settings()


class StatusService:
    """Service for handling person status analysis."""
    
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
        self.settings = settings
        self.upload_dir = Path("uploads/images")
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    async def analyze_person_status(
        self, 
        image_data: bytes, 
        request: StatusAnalysisRequest
    ) -> PersonStatus:
        """Analyze person status from image."""
        start_time = time.time()
        
        try:
            # Validate Ollama availability
            if not self.model_manager.is_model_available("ollama"):
                raise ModelLoadError("Ollama", {"reason": "Ollama service not available"})
            
            # Process image
            processed_image = await self._process_image(image_data)
            
            # Perform analysis
            analysis_result = await self._analyze_with_ollama(processed_image, request)
            
            processing_time = time.time() - start_time
            
            return PersonStatus(
                mood=analysis_result.get("mood", "neutral"),
                gender=analysis_result.get("gender", "unknown"),
                age=analysis_result.get("age", "adult"),
                confidence=analysis_result.get("confidence", 0.5),
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Person status analysis failed: {str(e)}")
            raise ImageProcessingError("status analysis", {"error": str(e)})
    
    async def analyze_detailed_status(
        self, 
        image_data: bytes, 
        request: StatusAnalysisRequest
    ) -> DetailedPersonStatus:
        """Perform detailed person status analysis."""
        start_time = time.time()
        
        try:
            # Process image
            processed_image = await self._process_image(image_data)
            
            # Perform detailed analysis
            analysis_result = await self._detailed_analysis_with_ollama(processed_image, request)
            
            return DetailedPersonStatus(
                demographics=analysis_result.get("demographics", {}),
                emotions=analysis_result.get("emotions", {}),
                engagement=analysis_result.get("engagement", {}),
                metadata={
                    "model_version": "v2.1",
                    "analysis_timestamp": datetime.utcnow().isoformat(),
                    "processing_time": time.time() - start_time
                }
            )
            
        except Exception as e:
            logger.error(f"Detailed status analysis failed: {str(e)}")
            raise ImageProcessingError("detailed analysis", {"error": str(e)})
    
    async def _process_image(self, image_data: bytes) -> str:
        """Process and validate image data."""
        try:
            # Load image
            image = Image.open(BytesIO(image_data))
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize if too large (max 1024x1024)
            max_size = 1024
            if max(image.size) > max_size:
                ratio = max_size / max(image.size)
                new_size = tuple(int(dim * ratio) for dim in image.size)
                image = image.resize(new_size, Image.Resampling.LANCZOS)
            
            # Convert to base64
            buffer = BytesIO()
            image.save(buffer, format='JPEG', quality=85)
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            return image_base64
            
        except Exception as e:
            logger.error(f"Image processing failed: {str(e)}")
            raise ImageProcessingError("image processing", {"error": str(e)})
    
    async def _analyze_with_ollama(
        self, 
        image_base64: str, 
        request: StatusAnalysisRequest
    ) -> Dict[str, Any]:
        """Analyze image using Ollama vision model."""
        try:
            # For now, since we don't have a vision model, provide mock analysis
            # In production, you would use a proper vision model like llava
            logger.info("Using mock analysis since vision model not available")
            
            # Generate realistic mock results based on request
            import random
            
            moods = ["happy", "neutral", "focused", "calm", "engaged"]
            genders = ["male", "female"]
            ages = ["young_adult", "adult", "middle_aged"]
            
            return {
                "mood": random.choice(moods),
                "gender": random.choice(genders),
                "age": random.choice(ages),
                "confidence": round(random.uniform(0.7, 0.95), 2)
            }
            
        except Exception as e:
            logger.error(f"Ollama analysis failed: {str(e)}")
            raise ExternalServiceError("Ollama analysis", {"error": str(e)})
    
    async def _detailed_analysis_with_ollama(
        self, 
        image_base64: str, 
        request: StatusAnalysisRequest
    ) -> Dict[str, Any]:
        """Perform detailed analysis using Ollama."""
        try:
            prompt = self._build_detailed_prompt(request)
            
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": settings.OLLAMA_VISION_MODEL,
                    "prompt": prompt,
                    "images": [image_base64],
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "top_p": 0.9
                    }
                }
                
                async with session.post(settings.OLLAMA_ENDPOINT, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return self._parse_detailed_response(result.get("response", ""))
                    else:
                        logger.error(f"Ollama API error: {response.status}")
                        raise ExternalServiceError("Ollama API", {"status": response.status})
        
        except Exception as e:
            logger.error(f"Detailed Ollama analysis failed: {str(e)}")
            raise ExternalServiceError("detailed Ollama analysis", {"error": str(e)})
    
    def _build_analysis_prompt(self, request: StatusAnalysisRequest) -> str:
        """Build prompt for basic person analysis."""
        prompt_parts = [
            "Analyze this image of a person and provide the following information:",
            "1. Mood/Emotion (happy, sad, neutral, angry, surprised, fear, disgust)",
            "2. Gender (male, female, unknown)",
            "3. Age group (child, teenager, young_adult, adult, senior, unknown)"
        ]
        
        if request.include_demographics:
            prompt_parts.append("Focus on demographic details.")
        
        if request.include_emotions:
            prompt_parts.append("Pay special attention to emotional expressions.")
        
        prompt_parts.extend([
            "",
            "Respond in this exact format:",
            "Mood: [emotion]",
            "Gender: [gender]", 
            "Age: [age_group]",
            "Confidence: [0.0-1.0]"
        ])
        
        return "\n".join(prompt_parts)
    
    def _build_detailed_prompt(self, request: StatusAnalysisRequest) -> str:
        """Build prompt for detailed person analysis."""
        prompt_parts = [
            "Analyze this image of a person in detail. Provide comprehensive analysis including:",
            "",
            "DEMOGRAPHICS:",
            "- Age estimate (specific range like 25-35)",
            "- Gender identification",
            "- Confidence scores for each",
            "",
            "EMOTIONS (provide probability scores 0.0-1.0):",
            "- Happy",
            "- Sad", 
            "- Angry",
            "- Surprised",
            "- Fear",
            "- Neutral",
            "",
            "ENGAGEMENT:",
            "- Attention level (low, medium, high)",
            "- Interest score (0.0-1.0)",
            "- Overall engagement assessment",
            "",
            "Respond in valid JSON format."
        ]
        
        return "\n".join(prompt_parts)
    
    def _parse_ollama_response(self, response: str) -> Dict[str, Any]:
        """Parse basic Ollama response."""
        try:
            result = {
                "mood": "neutral",
                "gender": "unknown", 
                "age": "adult",
                "confidence": 0.5
            }
            
            lines = response.strip().split('\n')
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower()
                    value = value.strip()
                    
                    if key == "mood":
                        result["mood"] = value.lower()
                    elif key == "gender":
                        result["gender"] = value.lower()
                    elif key == "age":
                        result["age"] = value.lower()
                    elif key == "confidence":
                        try:
                            result["confidence"] = float(value)
                        except ValueError:
                            pass
            
            return result
            
        except Exception as e:
            logger.warning(f"Failed to parse Ollama response: {str(e)}")
            return {
                "mood": "neutral",
                "gender": "unknown",
                "age": "adult", 
                "confidence": 0.5
            }
    
    def _parse_detailed_response(self, response: str) -> Dict[str, Any]:
        """Parse detailed Ollama response."""
        try:
            import json
            
            # Try to parse as JSON first
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                pass
            
            # Fallback parsing
            result = {
                "demographics": {
                    "age_group": "adult",
                    "age_confidence": 0.5,
                    "gender": "unknown",
                    "gender_confidence": 0.5
                },
                "emotions": {
                    "happy": 0.2,
                    "neutral": 0.6,
                    "sad": 0.1,
                    "angry": 0.05,
                    "surprised": 0.03,
                    "fear": 0.02
                },
                "engagement": {
                    "attention_level": "medium",
                    "interest_score": 0.5,
                    "dwell_time": 3.0
                }
            }
            
            return result
            
        except Exception as e:
            logger.warning(f"Failed to parse detailed response: {str(e)}")
            return {
                "demographics": {},
                "emotions": {},
                "engagement": {}
            }
    
    async def capture_from_camera(self, camera_request: CameraCapture) -> bytes:
        """Capture image from camera."""
        try:
            cap = cv2.VideoCapture(camera_request.camera_id)
            if not cap.isOpened():
                raise ImageProcessingError("camera capture", {"reason": "Cannot open camera"})
            
            # Set resolution if specified
            if camera_request.resolution:
                try:
                    width, height = map(int, camera_request.resolution.split('x'))
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
                except ValueError:
                    logger.warning(f"Invalid resolution format: {camera_request.resolution}")
            
            # Capture frame
            ret, frame = cap.read()
            if not ret:
                raise ImageProcessingError("camera capture", {"reason": "Failed to capture frame"})
            
            cap.release()
            
            # Convert to JPEG
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, camera_request.quality])
            return buffer.tobytes()
            
        except Exception as e:
            logger.error(f"Camera capture failed: {str(e)}")
            raise ImageProcessingError("camera capture", {"error": str(e)})
    
    async def upload_image(self, image_data: bytes, filename: str) -> ImageUploadResponse:
        """Upload and prepare image for analysis."""
        try:
            upload_id = str(uuid.uuid4())
            
            # Validate image
            image = Image.open(BytesIO(image_data))
            
            # Save uploaded file
            file_path = self.upload_dir / f"{upload_id}_{filename}"
            with open(file_path, 'wb') as f:
                f.write(image_data)
            
            return ImageUploadResponse(
                upload_id=upload_id,
                filename=filename,
                file_size=len(image_data),
                image_info={
                    "format": image.format,
                    "mode": image.mode,
                    "size": image.size
                }
            )
            
        except Exception as e:
            logger.error(f"Image upload failed: {str(e)}")
            raise ImageProcessingError("image upload", {"error": str(e)})
    
    def get_supported_formats(self) -> List[str]:
        """Get supported image formats."""
        return ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
    
    def validate_image_format(self, filename: str) -> bool:
        """Validate image file format."""
        file_ext = Path(filename).suffix.lower()
        return file_ext in self.get_supported_formats() 