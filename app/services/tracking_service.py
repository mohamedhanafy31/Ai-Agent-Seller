"""
Tracking Service - Business logic for person detection and tracking.
"""

import asyncio
import time
import uuid
import cv2
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

import torch
from loguru import logger

from app.schemas.tracking import (
    TrackingRequest, TrackingResult, TrackingSession, 
    BoundingBox, PersonTrack, TrackingSummary
)
from app.services.model_manager import ModelManager
from app.core.config import get_settings
from app.core.exceptions import VideoProcessingError, ModelLoadError

settings = get_settings()


class TrackingService:
    """Service for handling person tracking operations."""
    
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
        self.settings = settings
        self.active_sessions: Dict[str, TrackingSession] = {}
        self.upload_dir = Path("uploads/videos")
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    async def process_video(
        self, 
        video_path: str, 
        request: TrackingRequest
    ) -> TrackingResult:
        """Process video for person tracking."""
        start_time = time.time()
        session_id = str(uuid.uuid4())
        
        try:
            # Validate model availability
            if not self.model_manager.is_model_available("yolo"):
                raise ModelLoadError("YOLO", {"reason": "YOLO model not loaded"})
            
            if not self.model_manager.is_model_available("tracker"):
                raise ModelLoadError("Tracker", {"reason": "BoostTrack not loaded"})
            
            # Create tracking session
            session = TrackingSession(
                session_id=session_id,
                status="processing",
                video_filename=Path(video_path).name
            )
            self.active_sessions[session_id] = session
            
            # Process video
            result = await self._track_persons_in_video(
                video_path, 
                request, 
                session_id
            )
            
            # Update session
            session.status = "completed"
            session.completed_at = datetime.utcnow()
            session.result = result
            
            return result
            
        except Exception as e:
            logger.error(f"Video tracking failed: {str(e)}")
            
            # Update session with error
            if session_id in self.active_sessions:
                self.active_sessions[session_id].status = "failed"
                self.active_sessions[session_id].error_message = str(e)
            
            raise VideoProcessingError("video tracking", {"error": str(e)})
    
    async def _track_persons_in_video(
        self, 
        video_path: str, 
        request: TrackingRequest,
        session_id: str
    ) -> TrackingResult:
        """Perform person tracking on video."""
        try:
            # Open video
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise VideoProcessingError("video opening", {"path": video_path})
            
            # Get video info
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = total_frames / fps if fps > 0 else 0
            
            video_info = {
                "filename": Path(video_path).name,
                "duration": duration,
                "resolution": f"{width}x{height}",
                "fps": fps,
                "total_frames": total_frames
            }
            
            # Initialize tracker
            tracker = self.model_manager.tracker_instance
            tracker.reset()
            
            tracks = []
            frame_number = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_number += 1
                timestamp = frame_number / fps if fps > 0 else frame_number * 0.033
                
                # YOLO detection
                detections = await self._detect_persons(frame, request.confidence_threshold)
                
                # Update tracker
                if detections:
                    online_targets = tracker.update(detections, frame)
                    
                    # Convert to tracks
                    for target in online_targets:
                        track = PersonTrack(
                            track_id=target.track_id,
                            bbox=BoundingBox(
                                x1=float(target.tlbr[0]),
                                y1=float(target.tlbr[1]), 
                                x2=float(target.tlbr[2]),
                                y2=float(target.tlbr[3]),
                                confidence=float(target.score)
                            ),
                            frame_number=frame_number,
                            timestamp=timestamp,
                            confidence=float(target.score)
                        )
                        tracks.append(track)
                
                # Limit tracks to prevent memory issues
                if len(tracks) > request.max_tracks * 10:
                    break
            
            cap.release()
            
            processing_time = time.time() - time.time()  # This should be start_time
            
            return TrackingResult(
                session_id=session_id,
                video_info=video_info,
                tracks=tracks,
                total_frames=frame_number,
                processing_time=processing_time,
                fps=fps
            )
            
        except Exception as e:
            logger.error(f"Person tracking failed: {str(e)}")
            raise VideoProcessingError("person tracking", {"error": str(e)})
    
    async def _detect_persons(self, frame: np.ndarray, confidence_threshold: float) -> List[np.ndarray]:
        """Detect persons in frame using YOLO."""
        try:
            # YOLO inference
            results = self.model_manager.yolo_model(frame, conf=confidence_threshold)
            
            detections = []
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Filter for person class (class 0 in COCO)
                        if int(box.cls) == 0:  # Person class
                            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                            conf = float(box.conf[0])
                            
                            # Format detection for tracker: [x1, y1, x2, y2, conf]
                            detection = np.array([x1, y1, x2, y2, conf])
                            detections.append(detection)
            
            return detections
            
        except Exception as e:
            logger.error(f"Person detection failed: {str(e)}")
            return []
    
    async def upload_video(self, file_content: bytes, filename: str) -> TrackingSession:
        """Upload and prepare video for tracking."""
        try:
            session_id = str(uuid.uuid4())
            
            # Save uploaded file
            file_path = self.upload_dir / f"{session_id}_{filename}"
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            # Validate video file
            await self._validate_video_file(str(file_path))
            
            # Create session
            session = TrackingSession(
                session_id=session_id,
                status="uploaded",
                video_filename=filename
            )
            
            self.active_sessions[session_id] = session
            
            return session
            
        except Exception as e:
            logger.error(f"Video upload failed: {str(e)}")
            raise VideoProcessingError("video upload", {"error": str(e)})
    
    async def _validate_video_file(self, file_path: str):
        """Validate video file format and properties."""
        try:
            cap = cv2.VideoCapture(file_path)
            if not cap.isOpened():
                raise VideoProcessingError("validation", {"reason": "Cannot open video file"})
            
            # Check basic properties
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            if frame_count == 0:
                raise VideoProcessingError("validation", {"reason": "No frames in video"})
            
            if fps <= 0:
                raise VideoProcessingError("validation", {"reason": "Invalid FPS"})
            
            # Check duration (max 10 minutes)
            duration = frame_count / fps
            if duration > 600:  # 10 minutes
                raise VideoProcessingError("validation", {"reason": "Video too long (max 10 minutes)"})
            
            cap.release()
            
        except VideoProcessingError:
            raise
        except Exception as e:
            logger.error(f"Video validation failed: {str(e)}")
            raise VideoProcessingError("validation", {"error": str(e)})
    
    async def get_session(self, session_id: str) -> Optional[TrackingSession]:
        """Get tracking session by ID."""
        return self.active_sessions.get(session_id)
    
    async def get_all_sessions(self) -> List[TrackingSession]:
        """Get all tracking sessions."""
        return list(self.active_sessions.values())
    
    async def get_sessions_summary(self) -> TrackingSummary:
        """Get summary of tracking sessions."""
        sessions = list(self.active_sessions.values())
        
        total = len(sessions)
        active = len([s for s in sessions if s.status == "processing"])
        completed = len([s for s in sessions if s.status == "completed"])
        failed = len([s for s in sessions if s.status == "failed"])
        
        return TrackingSummary(
            total_sessions=total,
            active_sessions=active,
            completed_sessions=completed,
            failed_sessions=failed
        )
    
    def get_supported_formats(self) -> List[str]:
        """Get supported video formats."""
        return ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv']
    
    def validate_video_format(self, filename: str) -> bool:
        """Validate video file format."""
        file_ext = Path(filename).suffix.lower()
        return file_ext in self.get_supported_formats() 