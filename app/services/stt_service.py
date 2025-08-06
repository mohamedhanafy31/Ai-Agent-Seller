"""
Speech-to-Text Service - Business logic for Arabic speech recognition.
"""

import time
import tempfile
import os
import base64
import io
from typing import Optional, AsyncGenerator
from pathlib import Path

import soundfile as sf
import librosa
import numpy as np
from loguru import logger

from app.schemas.stt import (
    TranscriptionRequest, TranscriptionResponse, AudioInfo,
    STTStreamingRequest, STTStreamingResponse
)
from app.services.model_manager import ModelManager
from app.core.config import get_settings
from app.core.exceptions import AudioProcessingError, ModelLoadError

settings = get_settings()


class STTService:
    """Service for handling speech-to-text processing."""
    
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
        self.settings = settings
        # Buffer for streaming audio chunks
        self.audio_buffer = []
        self.accumulated_audio = np.array([])
        self.sample_rate = 16000
    
    async def transcribe_audio(
        self, 
        audio_file_path: str, 
        request: Optional[TranscriptionRequest] = None
    ) -> TranscriptionResponse:
        """Transcribe audio file to text."""
        start_time = time.time()
        
        try:
            # Validate model availability
            if not self.model_manager.is_model_available("whisper"):
                raise ModelLoadError("Whisper", {"reason": "Model not loaded"})
            
            # Process audio file
            audio_info = await self._process_audio_file(audio_file_path)
            
            # Perform transcription
            transcription_result = await self._perform_transcription(
                audio_file_path, 
                request.language if request else "ar"
            )
            
            processing_time = time.time() - start_time
            
            return TranscriptionResponse(
                text=transcription_result["text"],
                language=request.language if request else "ar",
                confidence=transcription_result.get("confidence"),
                duration=audio_info.duration,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Audio transcription failed: {str(e)}")
            raise AudioProcessingError("transcription", {"error": str(e)})
    
    async def _process_audio_file(self, file_path: str) -> AudioInfo:
        """Process and validate audio file."""
        try:
            # Get file info
            file_stat = os.stat(file_path)
            filename = Path(file_path).name
            
            # Try to load audio with soundfile first
            try:
                audio_data, sample_rate = sf.read(file_path)
                duration = len(audio_data) / sample_rate
                channels = 1 if len(audio_data.shape) == 1 else audio_data.shape[1]
                
            except Exception as sf_error:
                logger.warning(f"Soundfile failed, trying librosa: {sf_error}")
                
                # Fallback to librosa
                try:
                    audio_data, sample_rate = librosa.load(file_path, sr=None)
                    duration = len(audio_data) / sample_rate
                    channels = 1
                    
                except Exception as librosa_error:
                    logger.error(f"Both soundfile and librosa failed: {librosa_error}")
                    raise AudioProcessingError(
                        "audio loading", 
                        {"soundfile_error": str(sf_error), "librosa_error": str(librosa_error)}
                    )
            
            # Validate audio
            if duration < 0.1:
                raise AudioProcessingError("validation", {"reason": "Audio too short"})
            
            if duration > 300:  # 5 minutes max
                raise AudioProcessingError("validation", {"reason": "Audio too long (max 5 minutes)"})
            
            return AudioInfo(
                filename=filename,
                file_size=file_stat.st_size,
                duration=duration,
                sample_rate=sample_rate,
                channels=channels,
                format=Path(file_path).suffix
            )
            
        except AudioProcessingError:
            raise
        except Exception as e:
            logger.error(f"Audio processing failed: {str(e)}")
            raise AudioProcessingError("processing", {"error": str(e)})
    
    async def _perform_transcription(self, file_path: str, language: str) -> dict:
        """Perform the actual transcription using Whisper."""
        try:
            # Preprocess audio for better results
            processed_path = await self._preprocess_audio(file_path)
            
            # Transcribe using Whisper
            result = self.model_manager.whisper_model(
                processed_path,
                generate_kwargs={"language": language}
            )
            
            # Clean up processed file if different from original
            if processed_path != file_path:
                try:
                    os.unlink(processed_path)
                except:
                    pass
            
            # Extract confidence if available (Whisper doesn't always provide this)
            confidence = None
            if hasattr(result, 'confidence'):
                confidence = result.confidence
            elif isinstance(result, dict) and 'confidence' in result:
                confidence = result['confidence']
            
            return {
                "text": result["text"].strip(),
                "confidence": confidence
            }
            
        except Exception as e:
            logger.error(f"Whisper transcription failed: {str(e)}")
            raise AudioProcessingError("whisper transcription", {"error": str(e)})
    
    async def _preprocess_audio(self, file_path: str) -> str:
        """Preprocess audio for better transcription results."""
        try:
            # Load audio
            audio, sr = librosa.load(file_path, sr=16000)  # Whisper prefers 16kHz
            
            # Basic preprocessing
            # 1. Normalize volume
            audio = librosa.util.normalize(audio)
            
            # 2. Remove silence from beginning and end
            audio, _ = librosa.effects.trim(audio, top_db=20)
            
            # 3. Ensure mono
            if len(audio.shape) > 1:
                audio = np.mean(audio, axis=1)
            
            # Save preprocessed audio
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                sf.write(temp_file.name, audio, sr)
                return temp_file.name
                
        except Exception as e:
            logger.warning(f"Audio preprocessing failed, using original: {str(e)}")
            return file_path
    
    def get_supported_formats(self) -> list:
        """Get list of supported audio formats."""
        return ['.wav', '.mp3', '.m4a', '.ogg', '.flac', '.webm']
    
    def validate_audio_format(self, filename: str) -> bool:
        """Validate if audio format is supported."""
        file_ext = Path(filename).suffix.lower()
        return file_ext in self.get_supported_formats()
    
    async def get_audio_info(self, file_path: str) -> AudioInfo:
        """Get audio file information without transcription."""
        try:
            return await self._process_audio_file(file_path)
        except Exception as e:
            logger.error(f"Get audio info failed: {str(e)}")
            raise AudioProcessingError("audio info", {"error": str(e)})
    
    async def process_audio_chunk(self, request: STTStreamingRequest) -> STTStreamingResponse:
        """Process a streaming audio chunk and return partial/final transcription."""
        try:
            # Validate model availability
            if not self.model_manager.is_model_available("whisper"):
                return STTStreamingResponse(
                    type="error",
                    chunk_index=request.chunk_index,
                    message="Whisper model not available"
                )
            
            # Decode base64 audio data
            try:
                audio_bytes = base64.b64decode(request.audio_data)
            except Exception as e:
                return STTStreamingResponse(
                    type="error",
                    chunk_index=request.chunk_index,
                    message=f"Invalid base64 audio data: {str(e)}"
                )
            
            # Convert bytes to numpy array
            try:
                audio_chunk = self._bytes_to_audio(audio_bytes, request.sample_rate)
            except Exception as e:
                return STTStreamingResponse(
                    type="error",
                    chunk_index=request.chunk_index,
                    message=f"Audio conversion failed: {str(e)}"
                )
            
            # Accumulate audio data
            if len(self.accumulated_audio) == 0:
                self.accumulated_audio = audio_chunk
            else:
                self.accumulated_audio = np.concatenate([self.accumulated_audio, audio_chunk])
            
            # Process transcription
            if request.is_final or len(self.accumulated_audio) >= request.sample_rate * 2:  # At least 2 seconds
                result = await self._transcribe_audio_array(
                    self.accumulated_audio, 
                    request.sample_rate, 
                    request.language
                )
                
                response_type = "final" if request.is_final else "partial"
                
                # Reset buffer if final
                if request.is_final:
                    self.accumulated_audio = np.array([])
                
                return STTStreamingResponse(
                    type=response_type,
                    text=result["text"],
                    chunk_index=request.chunk_index,
                    confidence=result.get("confidence"),
                    is_final=request.is_final
                )
            else:
                # Not enough audio for transcription yet
                return STTStreamingResponse(
                    type="partial",
                    text="",
                    chunk_index=request.chunk_index,
                    confidence=0.0,
                    is_final=False
                )
                
        except Exception as e:
            logger.error(f"Streaming transcription failed: {str(e)}")
            return STTStreamingResponse(
                type="error",
                chunk_index=request.chunk_index,
                message=f"Processing failed: {str(e)}"
            )
    
    def _bytes_to_audio(self, audio_bytes: bytes, sample_rate: int) -> np.ndarray:
        """Convert audio bytes to numpy array."""
        try:
            # Try to read as WAV first
            with io.BytesIO(audio_bytes) as audio_io:
                audio_data, sr = sf.read(audio_io)
                
                # Resample if needed
                if sr != sample_rate:
                    audio_data = librosa.resample(audio_data, orig_sr=sr, target_sr=sample_rate)
                
                # Ensure mono
                if len(audio_data.shape) > 1:
                    audio_data = np.mean(audio_data, axis=1)
                
                return audio_data.astype(np.float32)
                
        except Exception as e:
            # Fallback: assume raw PCM data
            try:
                audio_data = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
                return audio_data
            except Exception as fallback_error:
                logger.error(f"Audio conversion failed: {str(e)}, fallback failed: {str(fallback_error)}")
                raise AudioProcessingError("audio conversion", {"error": str(e)})
    
    async def _transcribe_audio_array(self, audio_data: np.ndarray, sample_rate: int, language: str) -> dict:
        """Transcribe audio numpy array using Whisper."""
        try:
            # Save audio array to temporary file for Whisper
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                sf.write(temp_file.name, audio_data, sample_rate)
                temp_path = temp_file.name
            
            try:
                # Preprocess audio for better results
                processed_path = await self._preprocess_audio(temp_path)
                
                # Transcribe using Whisper
                result = self.model_manager.whisper_model(
                    processed_path,
                    generate_kwargs={"language": language}
                )
                
                # Clean up files
                if processed_path != temp_path:
                    try:
                        os.unlink(processed_path)
                    except:
                        pass
                
                # Extract confidence if available
                confidence = None
                if hasattr(result, 'confidence'):
                    confidence = result.confidence
                elif isinstance(result, dict) and 'confidence' in result:
                    confidence = result['confidence']
                
                return {
                    "text": result["text"].strip(),
                    "confidence": confidence
                }
                
            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_path)
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"Array transcription failed: {str(e)}")
            raise AudioProcessingError("array transcription", {"error": str(e)})
    
    def reset_streaming_buffer(self):
        """Reset the streaming audio buffer."""
        self.accumulated_audio = np.array([])
        self.audio_buffer = [] 