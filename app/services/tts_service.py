"""
Text-to-Speech Service - Business logic for Arabic voice synthesis.
"""

import time
import tempfile
import os
import base64
import asyncio
from typing import Optional, Dict, Any, AsyncGenerator
from pathlib import Path

import soundfile as sf
import numpy as np
from loguru import logger

from app.schemas.tts import TTSRequest, TTSResponse, TTSStreamingRequest, TTSStreamingResponse
from app.services.model_manager import ModelManager
from app.core.config import get_settings
from app.core.exceptions import AudioProcessingError, ModelLoadError

settings = get_settings()


class TTSService:
    """Service for handling text-to-speech processing."""
    
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
        self.settings = settings
        self.output_dir = Path("uploads/audio")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    async def synthesize_speech(self, request: TTSRequest) -> TTSResponse:
        """Synthesize speech from text."""
        start_time = time.time()
        
        try:
            # Validate model availability
            if not self.model_manager.is_model_available("tts"):
                raise ModelLoadError("TTS", {"reason": "Model not loaded"})
            
            # Generate unique filename
            import uuid
            output_filename = f"tts_{uuid.uuid4().hex[:8]}.wav"
            output_path = self.output_dir / output_filename
            
            # Synthesize audio
            await self._synthesize_audio(request, str(output_path))
            
            # Get audio info
            audio_info = await self._get_audio_info(str(output_path))
            
            processing_time = time.time() - start_time
            
            return TTSResponse(
                audio_url=f"/audio/{output_filename}",
                duration=audio_info["duration"],
                sample_rate=audio_info["sample_rate"],
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"TTS synthesis failed: {str(e)}")
            raise AudioProcessingError("TTS synthesis", {"error": str(e)})
    
    async def _synthesize_audio(self, request: TTSRequest, output_path: str):
        """Perform the actual TTS synthesis."""
        try:
            # Check if speaker reference file exists
            speaker_wav_path = Path(settings.TTS_SPEAKER_WAV)
            if not speaker_wav_path.exists():
                raise AudioProcessingError(
                    "speaker reference", 
                    {"reason": f"Speaker file {settings.TTS_SPEAKER_WAV} not found"}
                )
            
            # Use TTS model to synthesize
            if hasattr(self.model_manager, 'tts_streamer') and self.model_manager.tts_streamer:
                # Use streamer if available
                audio = self.model_manager.tts_streamer.synthesize(
                    text=request.text,
                    language=request.language,
                    speed=request.speed
                )
            else:
                # Use basic TTS model
                audio = self.model_manager.tts_model.tts(
                    text=request.text,
                    speaker_wav=str(speaker_wav_path),
                    language=request.language
                )
            
            # Adjust speed if needed
            if request.speed != 1.0:
                audio = self._adjust_speed(audio, request.speed)
            
            # Save audio file
            sf.write(output_path, audio, 22050)
            
        except Exception as e:
            logger.error(f"Audio synthesis failed: {str(e)}")
            raise AudioProcessingError("audio synthesis", {"error": str(e)})
    
    def _adjust_speed(self, audio: np.ndarray, speed: float) -> np.ndarray:
        """Adjust audio playback speed."""
        try:
            import librosa
            return librosa.effects.time_stretch(audio, rate=speed)
        except ImportError:
            logger.warning("librosa not available for speed adjustment")
            return audio
        except Exception as e:
            logger.warning(f"Speed adjustment failed: {str(e)}")
            return audio
    
    async def _get_audio_info(self, file_path: str) -> Dict[str, Any]:
        """Get audio file information."""
        try:
            audio, sample_rate = sf.read(file_path)
            duration = len(audio) / sample_rate
            
            return {
                "duration": duration,
                "sample_rate": sample_rate,
                "channels": 1 if len(audio.shape) == 1 else audio.shape[1]
            }
            
        except Exception as e:
            logger.error(f"Get audio info failed: {str(e)}")
            return {"duration": 0, "sample_rate": 22050, "channels": 1}


class TTSStreamer:
    """TTS Streaming service for real-time audio generation."""
    
    def __init__(self, tts_model, speaker_wav_path: str):
        self.tts_model = tts_model
        self.speaker_wav_path = speaker_wav_path
        
    def synthesize(self, text: str, language: str = "ar", speed: float = 1.0) -> np.ndarray:
        """Synthesize audio from text."""
        try:
            audio = self.tts_model.tts(
                text=text,
                speaker_wav=self.speaker_wav_path,
                language=language
            )
            return np.array(audio)
            
        except Exception as e:
            logger.error(f"TTS synthesis failed: {str(e)}")
            raise AudioProcessingError("TTS synthesis", {"error": str(e)})
    
    async def stream_synthesis(
        self, 
        request: TTSStreamingRequest
    ) -> AsyncGenerator[TTSStreamingResponse, None]:
        """Stream audio synthesis in chunks."""
        try:
            # Synthesize full audio
            audio = self.synthesize(request.text, request.language)
            
            # Convert to bytes
            audio_bytes = (audio * 32767).astype(np.int16).tobytes()
            
            # Send metadata first
            yield TTSStreamingResponse(
                type="metadata",
                metadata={
                    "sample_rate": 22050,
                    "channels": 1,
                    "duration": len(audio) / 22050,
                    "total_chunks": len(audio_bytes) // request.chunk_size + 1
                },
                is_final=False
            )
            
            # Stream audio in chunks
            chunk_index = 0
            for i in range(0, len(audio_bytes), request.chunk_size):
                chunk = audio_bytes[i:i + request.chunk_size]
                chunk_base64 = base64.b64encode(chunk).decode('utf-8')
                
                is_final = i + request.chunk_size >= len(audio_bytes)
                
                yield TTSStreamingResponse(
                    type="audio_chunk",
                    data=chunk_base64,
                    chunk_index=chunk_index,
                    is_final=is_final
                )
                
                chunk_index += 1
                
                # Small delay to prevent overwhelming the client
                await asyncio.sleep(0.01)
                
            # Send completion message
            yield TTSStreamingResponse(
                type="complete",
                is_final=True
            )
            
        except Exception as e:
            logger.error(f"TTS streaming failed: {str(e)}")
            yield TTSStreamingResponse(
                type="error",
                metadata={"error": str(e)},
                is_final=True
            ) 