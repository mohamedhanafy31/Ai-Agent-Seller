"""
File handling utilities.
"""

import os
import hashlib
import mimetypes
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Tuple, List
from datetime import datetime, timedelta

from loguru import logger


def get_file_hash(file_path: str, algorithm: str = "md5") -> str:
    """
    Calculate file hash.
    
    Args:
        file_path: Path to file
        algorithm: Hash algorithm (md5, sha1, sha256)
        
    Returns:
        Hex digest of file hash
    """
    try:
        hash_obj = hashlib.new(algorithm)
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)
        
        return hash_obj.hexdigest()
        
    except Exception as e:
        logger.error(f"File hash calculation failed: {str(e)}")
        raise


def get_file_mime_type(file_path: str) -> Optional[str]:
    """
    Get MIME type of file.
    
    Args:
        file_path: Path to file
        
    Returns:
        MIME type string or None
    """
    try:
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type
        
    except Exception as e:
        logger.error(f"MIME type detection failed: {str(e)}")
        return None


def safe_filename(filename: str) -> str:
    """
    Create safe filename by removing/replacing dangerous characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Safe filename
    """
    try:
        # Replace dangerous characters
        dangerous_chars = '<>:"/\\|?*'
        safe_name = filename
        
        for char in dangerous_chars:
            safe_name = safe_name.replace(char, '_')
        
        # Remove leading/trailing spaces and dots
        safe_name = safe_name.strip(' .')
        
        # Ensure not empty
        if not safe_name:
            safe_name = "unnamed_file"
        
        # Limit length
        if len(safe_name) > 255:
            name, ext = os.path.splitext(safe_name)
            max_name_len = 255 - len(ext)
            safe_name = name[:max_name_len] + ext
        
        return safe_name
        
    except Exception as e:
        logger.error(f"Safe filename creation failed: {str(e)}")
        return "safe_file"


def create_unique_filename(directory: str, filename: str) -> str:
    """
    Create unique filename if file already exists.
    
    Args:
        directory: Target directory
        filename: Original filename
        
    Returns:
        Unique filename
    """
    try:
        file_path = Path(directory) / filename
        
        if not file_path.exists():
            return filename
        
        name, ext = os.path.splitext(filename)
        counter = 1
        
        while file_path.exists():
            new_filename = f"{name}_{counter}{ext}"
            file_path = Path(directory) / new_filename
            counter += 1
        
        return file_path.name
        
    except Exception as e:
        logger.error(f"Unique filename creation failed: {str(e)}")
        return filename


def ensure_directory(directory: str) -> bool:
    """
    Ensure directory exists, create if necessary.
    
    Args:
        directory: Directory path
        
    Returns:
        True if directory exists or was created
    """
    try:
        Path(directory).mkdir(parents=True, exist_ok=True)
        return True
        
    except Exception as e:
        logger.error(f"Directory creation failed: {str(e)}")
        return False


def get_file_size_human_readable(file_path: str) -> str:
    """
    Get human-readable file size.
    
    Args:
        file_path: Path to file
        
    Returns:
        Human-readable size string
    """
    try:
        size = os.path.getsize(file_path)
        
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        
        return f"{size:.1f} PB"
        
    except Exception as e:
        logger.error(f"File size calculation failed: {str(e)}")
        return "Unknown"


def cleanup_old_files(directory: str, max_age_hours: int = 24) -> int:
    """
    Clean up old files in directory.
    
    Args:
        directory: Directory to clean
        max_age_hours: Maximum age in hours
        
    Returns:
        Number of files deleted
    """
    try:
        if not Path(directory).exists():
            return 0
        
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        deleted_count = 0
        
        for file_path in Path(directory).iterdir():
            if file_path.is_file():
                file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                
                if file_time < cutoff_time:
                    try:
                        file_path.unlink()
                        deleted_count += 1
                        logger.info(f"Deleted old file: {file_path}")
                    except Exception as e:
                        logger.warning(f"Failed to delete {file_path}: {str(e)}")
        
        return deleted_count
        
    except Exception as e:
        logger.error(f"Cleanup failed: {str(e)}")
        return 0


def copy_file_safe(source: str, destination: str) -> bool:
    """
    Safely copy file with error handling.
    
    Args:
        source: Source file path
        destination: Destination file path
        
    Returns:
        True if copy succeeded
    """
    try:
        # Ensure destination directory exists
        dest_dir = Path(destination).parent
        ensure_directory(str(dest_dir))
        
        # Copy file
        shutil.copy2(source, destination)
        
        # Verify copy
        if Path(destination).exists():
            source_size = os.path.getsize(source)
            dest_size = os.path.getsize(destination)
            
            if source_size == dest_size:
                return True
            else:
                logger.error(f"File copy size mismatch: {source_size} != {dest_size}")
                return False
        
        return False
        
    except Exception as e:
        logger.error(f"File copy failed: {str(e)}")
        return False


def move_file_safe(source: str, destination: str) -> bool:
    """
    Safely move file with error handling.
    
    Args:
        source: Source file path
        destination: Destination file path
        
    Returns:
        True if move succeeded
    """
    try:
        # First try copy then delete
        if copy_file_safe(source, destination):
            try:
                os.unlink(source)
                return True
            except Exception as e:
                logger.error(f"Failed to delete source after copy: {str(e)}")
                return False
        
        return False
        
    except Exception as e:
        logger.error(f"File move failed: {str(e)}")
        return False


def get_temp_file_path(suffix: str = "", prefix: str = "tmp") -> str:
    """
    Get temporary file path.
    
    Args:
        suffix: File suffix (e.g., '.wav')
        prefix: File prefix
        
    Returns:
        Temporary file path
    """
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, prefix=prefix) as temp_file:
            return temp_file.name
            
    except Exception as e:
        logger.error(f"Temp file creation failed: {str(e)}")
        raise


def validate_file_path(file_path: str, allowed_extensions: Optional[List[str]] = None) -> Tuple[bool, Optional[str]]:
    """
    Validate file path and extension.
    
    Args:
        file_path: Path to validate
        allowed_extensions: List of allowed extensions (e.g., ['.jpg', '.png'])
        
    Returns:
        (is_valid, error_message)
    """
    try:
        path = Path(file_path)
        
        # Check if file exists
        if not path.exists():
            return False, "File does not exist"
        
        # Check if it's a file (not directory)
        if not path.is_file():
            return False, "Path is not a file"
        
        # Check extension if specified
        if allowed_extensions:
            file_ext = path.suffix.lower()
            if file_ext not in [ext.lower() for ext in allowed_extensions]:
                return False, f"File extension {file_ext} not allowed. Allowed: {allowed_extensions}"
        
        # Check file size (reasonable limits)
        file_size = path.stat().st_size
        if file_size == 0:
            return False, "File is empty"
        
        if file_size > 100 * 1024 * 1024:  # 100 MB
            return False, "File too large (max 100MB)"
        
        return True, None
        
    except Exception as e:
        return False, f"Validation error: {str(e)}"


def get_directory_size(directory: str) -> int:
    """
    Get total size of directory in bytes.
    
    Args:
        directory: Directory path
        
    Returns:
        Total size in bytes
    """
    try:
        total_size = 0
        
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(file_path)
                except (OSError, FileNotFoundError):
                    pass
        
        return total_size
        
    except Exception as e:
        logger.error(f"Directory size calculation failed: {str(e)}")
        return 0 