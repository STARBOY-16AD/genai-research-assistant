# src/backend/core/config.py
"""
Configuration settings for the application
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Settings
    HOST: str = "localhost"
    PORT: int = 8000
    DEBUG: bool = True
    
    # OpenAI API
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4-1106-preview"
    
    # Anthropic API (Alternative)
    ANTHROPIC_API_KEY: Optional[str] = None
    
    # File Settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: list = ["pdf", "txt", "docx"]
    UPLOAD_DIR: str = "uploads"
    
    # Vector Database
    VECTOR_DB_PATH: str = "data/vector_db"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    # AI Settings
    MAX_TOKENS: int = 4000
    TEMPERATURE: float = 0.7
    SUMMARY_MAX_WORDS: int = 150
    
    # Challenge Mode
    NUM_CHALLENGE_QUESTIONS: int = 3
    
    class Config:
        env_file = ".env"
        case_sensitive = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create directories if they don't exist
        Path(self.UPLOAD_DIR).mkdir(exist_ok=True)
        Path(self.VECTOR_DB_PATH).mkdir(parents=True, exist_ok=True)

settings = Settings()