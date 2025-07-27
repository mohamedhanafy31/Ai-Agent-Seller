"""
Audio processing utilities.
"""

import io
import wave
import tempfile
import os
from pathlib import Path
from typing import Tuple, Optional

import numpy as np
import soundfile as sf
import librosa
from loguru import logger


def convert_audio_format(
    input_data: bytes, 
    target_format: str = "wav", 
    target_sample_rate: int = 16000
) -> bytes:
    """
    Convert audio data to target format and sample rate.
    
    Args:
        input_data: Raw audio bytes
        target_format: Target format (wav, mp3, etc.)
        target_sample_rate: Target sample rate
        
    Returns:
        Converted audio bytes
    """
    try:
        # Save input to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.audio') as temp_input:
            temp_input.write(input_data)
            temp_input_path = temp_input.name
        
        # Load audio
        audio, sr = librosa.load(temp_input_path, sr=target_sample_rate)
        
        # Save to target format
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{target_format}') as temp_output:
            sf.write(temp_output.name, audio, target_sample_rate)
            temp_output_path = temp_output.name
        
        # Read converted data
        with open(temp_output_path, 'rb') as f:
            converted_data = f.read()
        
        # Clean up
        os.unlink(temp_input_path)
        os.unlink(temp_output_path)
        
        return converted_data
        
    except Exception as e:
        logger.error(f"Audio conversion failed: {str(e)}")
        raise


def get_audio_duration(audio_data: bytes) -> float:
    """
    Get audio duration in seconds.
    
    Args:
        audio_data: Raw audio bytes
        
    Returns:
        Duration in seconds
    """
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.audio') as temp_file:
            temp_file.write(audio_data)
            temp_path = temp_file.name
        
        # Get duration using librosa
        duration = librosa.get_duration(path=temp_path)
        
        # Clean up
        os.unlink(temp_path)
        
        return duration
        
    except Exception as e:
        logger.error(f"Get audio duration failed: {str(e)}")
        return 0.0


def normalize_audio(audio: np.ndarray) -> np.ndarray:
    """
    Normalize audio amplitude to [-1, 1] range.
    
    Args:
        audio: Audio array
        
    Returns:
        Normalized audio array
    """
    try:
        max_val = np.max(np.abs(audio))
        if max_val > 0:
            return audio / max_val
        return audio
        
    except Exception as e:
        logger.error(f"Audio normalization failed: {str(e)}")
        return audio


def trim_silence(audio: np.ndarray, sample_rate: int, top_db: int = 20) -> np.ndarray:
    """
    Remove silence from beginning and end of audio.
    
    Args:
        audio: Audio array
        sample_rate: Sample rate
        top_db: Threshold for silence detection
        
    Returns:
        Trimmed audio array
    """
    try:
        trimmed_audio, _ = librosa.effects.trim(audio, top_db=top_db)
        return trimmed_audio
        
    except Exception as e:
        logger.error(f"Audio trimming failed: {str(e)}")
        return audio


def resample_audio(audio: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
    """
    Resample audio to target sample rate.
    
    Args:
        audio: Audio array
        orig_sr: Original sample rate
        target_sr: Target sample rate
        
    Returns:
        Resampled audio array
    """
    try:
        if orig_sr == target_sr:
            return audio
            
        resampled = librosa.resample(audio, orig_sr=orig_sr, target_sr=target_sr)
        return resampled
        
    except Exception as e:
        logger.error(f"Audio resampling failed: {str(e)}")
        return audio


def validate_audio_file(file_path: str) -> Tuple[bool, Optional[str]]:
    """
    Validate audio file format and properties.
    
    Args:
        file_path: Path to audio file
        
    Returns:
        (is_valid, error_message)
    """
    try:
        # Check if file exists
        if not Path(file_path).exists():
            return False, "File does not exist"
        
        # Try to load with soundfile
        try:
            data, sample_rate = sf.read(file_path)
            duration = len(data) / sample_rate
            
            # Check basic properties
            if duration < 0.1:
                return False, "Audio too short (minimum 0.1 seconds)"
            
            if duration > 300:  # 5 minutes
                return False, "Audio too long (maximum 5 minutes)"
            
            if sample_rate < 8000:
                return False, "Sample rate too low (minimum 8kHz)"
            
            return True, None
            
        except Exception as sf_error:
            # Try with librosa as fallback
            try:
                data, sample_rate = librosa.load(file_path, sr=None)
                duration = len(data) / sample_rate
                
                if duration < 0.1:
                    return False, "Audio too short (minimum 0.1 seconds)"
                
                if duration > 300:
                    return False, "Audio too long (maximum 5 minutes)"
                
                return True, None
                
            except Exception as librosa_error:
                return False, f"Cannot read audio file: {str(librosa_error)}"
        
    except Exception as e:
        return False, f"Validation error: {str(e)}"


def audio_to_wav_bytes(audio: np.ndarray, sample_rate: int) -> bytes:
    """
    Convert audio array to WAV bytes.
    
    Args:
        audio: Audio array
        sample_rate: Sample rate
        
    Returns:
        WAV format bytes
    """
    try:
        # Ensure audio is in correct format
        if audio.dtype != np.int16:
            # Convert to 16-bit PCM
            audio = (audio * 32767).astype(np.int16)
        
        # Create WAV in memory
        buffer = io.BytesIO()
        
        with wave.open(buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio.tobytes())
        
        buffer.seek(0)
        return buffer.read()
        
    except Exception as e:
        logger.error(f"Audio to WAV conversion failed: {str(e)}")
        raise


def detect_speech_segments(
    audio: np.ndarray, 
    sample_rate: int, 
    min_silence_duration: float = 0.5
) -> list:
    """
    Detect speech segments in audio.
    
    Args:
        audio: Audio array
        sample_rate: Sample rate
        min_silence_duration: Minimum silence duration in seconds
        
    Returns:
        List of (start_time, end_time) tuples
    """
    try:
        # Use librosa to detect non-silent intervals
        intervals = librosa.effects.split(
            audio, 
            top_db=20, 
            frame_length=2048, 
            hop_length=512
        )
        
        # Convert frame indices to time
        segments = []
        for start_frame, end_frame in intervals:
            start_time = start_frame / sample_rate
            end_time = end_frame / sample_rate
            
            # Filter out very short segments
            if end_time - start_time >= 0.1:
                segments.append((start_time, end_time))
        
        return segments
        
    except Exception as e:
        logger.error(f"Speech segment detection failed: {str(e)}")
        return [] 