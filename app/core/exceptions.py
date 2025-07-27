"""
Custom exceptions and error handlers for AI Agent Seller Backend.
"""

from typing import Any, Dict, Optional
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from loguru import logger


class BaseCustomException(Exception):
    """Base custom exception class."""
    
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ModelLoadError(BaseCustomException):
    """Exception raised when AI model loading fails."""
    
    def __init__(self, model_name: str, details: Optional[Dict[str, Any]] = None):
        message = f"Failed to load AI model: {model_name}"
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details,
        )


class AudioProcessingError(BaseCustomException):
    """Exception raised when audio processing fails."""
    
    def __init__(self, operation: str, details: Optional[Dict[str, Any]] = None):
        message = f"Audio processing failed during: {operation}"
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
        )


class ImageProcessingError(BaseCustomException):
    """Exception raised when image processing fails."""
    
    def __init__(self, operation: str, details: Optional[Dict[str, Any]] = None):
        message = f"Image processing failed during: {operation}"
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
        )


class VideoProcessingError(BaseCustomException):
    """Exception raised when video processing fails."""
    
    def __init__(self, operation: str, details: Optional[Dict[str, Any]] = None):
        message = f"Video processing failed during: {operation}"
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
        )


class DatabaseError(BaseCustomException):
    """Exception raised when database operations fail."""
    
    def __init__(self, operation: str, details: Optional[Dict[str, Any]] = None):
        message = f"Database operation failed: {operation}"
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )


class ExternalServiceError(BaseCustomException):
    """Exception raised when external service calls fail."""
    
    def __init__(self, service: str, details: Optional[Dict[str, Any]] = None):
        message = f"External service unavailable: {service}"
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details,
        )


class ValidationError(BaseCustomException):
    """Exception raised when input validation fails."""
    
    def __init__(self, field: str, value: Any, details: Optional[Dict[str, Any]] = None):
        message = f"Validation failed for field '{field}' with value: {value}"
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
        )


class InsufficientStorageError(BaseCustomException):
    """Exception raised when storage space is insufficient."""
    
    def __init__(self, required_space: str, details: Optional[Dict[str, Any]] = None):
        message = f"Insufficient storage space. Required: {required_space}"
        super().__init__(
            message=message,
            status_code=status.HTTP_507_INSUFFICIENT_STORAGE,
            details=details,
        )


# Exception handlers
async def custom_exception_handler(request: Request, exc: BaseCustomException) -> JSONResponse:
    """Handle custom exceptions."""
    logger.error(f"Custom exception occurred: {exc.message}", extra={"details": exc.details})
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.message,
            "details": exc.details,
            "type": exc.__class__.__name__,
        },
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions."""
    logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "type": "HTTPException",
        },
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general exceptions."""
    logger.error(f"Unexpected error occurred: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "message": "Internal server error occurred",
            "type": "InternalServerError",
        },
    ) 