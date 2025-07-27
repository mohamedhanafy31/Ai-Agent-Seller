"""
Image processing utilities.
"""

import io
import base64
from typing import Tuple, Optional, Dict, Any
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from loguru import logger


def resize_image(
    image: Image.Image, 
    max_size: Tuple[int, int] = (1024, 1024), 
    maintain_aspect: bool = True
) -> Image.Image:
    """
    Resize image while maintaining aspect ratio.
    
    Args:
        image: PIL Image
        max_size: Maximum (width, height)
        maintain_aspect: Whether to maintain aspect ratio
        
    Returns:
        Resized PIL Image
    """
    try:
        if maintain_aspect:
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            return image
        else:
            return image.resize(max_size, Image.Resampling.LANCZOS)
            
    except Exception as e:
        logger.error(f"Image resize failed: {str(e)}")
        return image


def normalize_image(image: Image.Image) -> Image.Image:
    """
    Normalize image format and properties.
    
    Args:
        image: PIL Image
        
    Returns:
        Normalized PIL Image
    """
    try:
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Auto-enhance if needed
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(1.1)
        
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.1)
        
        return image
        
    except Exception as e:
        logger.error(f"Image normalization failed: {str(e)}")
        return image


def image_to_base64(image: Image.Image, format: str = "JPEG", quality: int = 85) -> str:
    """
    Convert PIL Image to base64 string.
    
    Args:
        image: PIL Image
        format: Output format (JPEG, PNG, etc.)
        quality: JPEG quality (1-100)
        
    Returns:
        Base64 encoded string
    """
    try:
        buffer = io.BytesIO()
        
        if format.upper() == "JPEG":
            image.save(buffer, format=format, quality=quality, optimize=True)
        else:
            image.save(buffer, format=format)
        
        buffer.seek(0)
        image_bytes = buffer.read()
        
        return base64.b64encode(image_bytes).decode('utf-8')
        
    except Exception as e:
        logger.error(f"Image to base64 conversion failed: {str(e)}")
        raise


def base64_to_image(base64_string: str) -> Image.Image:
    """
    Convert base64 string to PIL Image.
    
    Args:
        base64_string: Base64 encoded image
        
    Returns:
        PIL Image
    """
    try:
        image_bytes = base64.b64decode(base64_string)
        image = Image.open(io.BytesIO(image_bytes))
        return image
        
    except Exception as e:
        logger.error(f"Base64 to image conversion failed: {str(e)}")
        raise


def validate_image_file(file_path: str) -> Tuple[bool, Optional[str]]:
    """
    Validate image file format and properties.
    
    Args:
        file_path: Path to image file
        
    Returns:
        (is_valid, error_message)
    """
    try:
        # Check if file exists
        if not Path(file_path).exists():
            return False, "File does not exist"
        
        # Try to open with PIL
        try:
            with Image.open(file_path) as image:
                # Check basic properties
                if image.size[0] < 32 or image.size[1] < 32:
                    return False, "Image too small (minimum 32x32 pixels)"
                
                if image.size[0] > 4096 or image.size[1] > 4096:
                    return False, "Image too large (maximum 4096x4096 pixels)"
                
                # Check file size (10MB max)
                file_size = Path(file_path).stat().st_size
                if file_size > 10 * 1024 * 1024:  # 10 MB
                    return False, "File too large (maximum 10MB)"
                
                return True, None
                
        except Exception as pil_error:
            return False, f"Cannot read image file: {str(pil_error)}"
        
    except Exception as e:
        return False, f"Validation error: {str(e)}"


def detect_faces(image: np.ndarray) -> list:
    """
    Detect faces in image using OpenCV.
    
    Args:
        image: Image array (BGR format)
        
    Returns:
        List of face bounding boxes [(x, y, w, h), ...]
    """
    try:
        # Load face cascade classifier
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        return faces.tolist()
        
    except Exception as e:
        logger.error(f"Face detection failed: {str(e)}")
        return []


def crop_face(image: Image.Image, face_box: Tuple[int, int, int, int], padding: float = 0.2) -> Image.Image:
    """
    Crop face region from image with padding.
    
    Args:
        image: PIL Image
        face_box: (x, y, width, height) of face
        padding: Padding factor (0.2 = 20% padding)
        
    Returns:
        Cropped PIL Image
    """
    try:
        x, y, w, h = face_box
        
        # Add padding
        pad_x = int(w * padding)
        pad_y = int(h * padding)
        
        # Calculate crop box
        left = max(0, x - pad_x)
        top = max(0, y - pad_y)
        right = min(image.width, x + w + pad_x)
        bottom = min(image.height, y + h + pad_y)
        
        # Crop image
        cropped = image.crop((left, top, right, bottom))
        
        return cropped
        
    except Exception as e:
        logger.error(f"Face cropping failed: {str(e)}")
        return image


def enhance_image_quality(image: Image.Image) -> Image.Image:
    """
    Enhance image quality for better analysis.
    
    Args:
        image: PIL Image
        
    Returns:
        Enhanced PIL Image
    """
    try:
        # Sharpen
        image = image.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3))
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.2)
        
        # Enhance color
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(1.1)
        
        return image
        
    except Exception as e:
        logger.error(f"Image enhancement failed: {str(e)}")
        return image


def get_image_info(image_path: str) -> Dict[str, Any]:
    """
    Get comprehensive image information.
    
    Args:
        image_path: Path to image file
        
    Returns:
        Dictionary with image info
    """
    try:
        with Image.open(image_path) as image:
            file_size = Path(image_path).stat().st_size
            
            info = {
                "filename": Path(image_path).name,
                "format": image.format,
                "mode": image.mode,
                "size": image.size,
                "width": image.width,
                "height": image.height,
                "file_size": file_size,
                "has_transparency": image.mode in ("RGBA", "LA") or "transparency" in image.info
            }
            
            # Get EXIF data if available
            if hasattr(image, '_getexif') and image._getexif():
                info["exif"] = dict(image._getexif())
            
            return info
            
    except Exception as e:
        logger.error(f"Get image info failed: {str(e)}")
        return {}


def convert_image_format(
    image: Image.Image, 
    target_format: str = "JPEG", 
    quality: int = 85
) -> bytes:
    """
    Convert image to target format and return bytes.
    
    Args:
        image: PIL Image
        target_format: Target format (JPEG, PNG, etc.)
        quality: JPEG quality (1-100)
        
    Returns:
        Image bytes in target format
    """
    try:
        buffer = io.BytesIO()
        
        # Convert mode if needed
        if target_format.upper() == "JPEG" and image.mode in ("RGBA", "LA"):
            # Create white background for JPEG
            background = Image.new("RGB", image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[-1] if image.mode == "RGBA" else None)
            image = background
        
        # Save to buffer
        if target_format.upper() == "JPEG":
            image.save(buffer, format=target_format, quality=quality, optimize=True)
        else:
            image.save(buffer, format=target_format)
        
        buffer.seek(0)
        return buffer.read()
        
    except Exception as e:
        logger.error(f"Image format conversion failed: {str(e)}")
        raise 