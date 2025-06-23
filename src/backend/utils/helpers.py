import os
from pathlib import Path
from loguru import logger
from typing import Optional
from src.backend.core.config import settings

def configure_logger():
    """Configure loguru logger with rotation and retention"""
    logger.add(
        "logs/app.log",
        rotation="10 MB",
        retention="7 days",
        level="DEBUG" if settings.DEBUG else "INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
    )
    return logger

def validate_file_path(file_path: str) -> bool:
    """Validate if file exists and is accessible"""
    path = Path(file_path)
    return path.exists() and path.is_file()

def ensure_directory(directory: str) -> None:
    """Ensure directory exists, create if it doesn't"""
    Path(directory).mkdir(parents=True, exist_ok=True)

def get_safe_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal"""
    return "".join(c for c in filename if c.isalnum() or c in ('.', '_', '-')).strip()

def log_api_request(endpoint: str, method: str, status_code: int, message: Optional[str] = None):
    """Log API request details"""
    logger = configure_logger()
    logger.info(
        f"API Request | Endpoint: {endpoint} | Method: {method} | "
        f"Status: {status_code} | Message: {message or 'No additional info'}"
    )