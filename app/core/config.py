"""
Application configuration settings.
"""
import os
from typing import List, Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # API settings
    API_TITLE: str = "Motion Q&A API"
    API_VERSION: str = "1.0.0"
    
    # Application settings
    APP_NAME: str = "Motion Q&A"
    DEBUG: bool = True
    
    # Database settings
    DATABASE_URL: str = "sqlite:///motion_qna.db"
    
    # AI model settings
    USE_TRANSFORMERS: bool = os.environ.get("USE_TRANSFORMERS", "False").lower() in ("true", "1", "t")
    USE_AI_MODELS: bool = os.environ.get("USE_AI_MODELS", "False").lower() in ("true", "1", "t")
    DEFAULT_MODEL: str = "distilgpt2"
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Project info
    PROJECT_NAME: str = "Motion Q&A"
    PROJECT_DESCRIPTION: str = "Question Analysis and Solution Generation System"
    PROJECT_VERSION: str = "0.1.0"
    
    # API settings
    API_V1_STR: str = "/api/v1"
    
    # CORS settings
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Security settings
    SECRET_KEY: str = "dev_secret_key_change_in_production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    @field_validator("DATABASE_URL")
    def assemble_db_url(cls, v: str, info):
        if os.path.isabs(v):
            return v
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        return os.path.join(base_dir, v.replace("sqlite:///", ""))
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Create a global settings instance
settings = Settings() 