import os
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Project info
    PROJECT_NAME: str = "Motion Q&A"
    PROJECT_DESCRIPTION: str = "Question Analysis and Solution Generation System"
    PROJECT_VERSION: str = "0.1.0"
    
    # API settings
    API_V1_STR: str = "/api/v1"
    
    # CORS settings
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Database settings
    DATABASE_URL: str = "sqlite:///./motion_qna.db"
    
    # Model settings
    USE_TRANSFORMERS: bool = True
    USE_AI_MODELS: bool = os.environ.get("USE_AI_MODELS", "True").lower() == "true"
    DEFAULT_MODEL: str = "gpt2"  # Default model, will be overridden if USE_TRANSFORMERS is False
    
    # Security settings
    SECRET_KEY: str = "dev_secret_key_change_in_production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Environment settings
    DEBUG: bool = True
    
    @field_validator("DATABASE_URL")
    def assemble_db_url(cls, v: str, info):
        if os.path.isabs(v):
            return v
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        return os.path.join(base_dir, v.replace("sqlite:///", ""))
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings object
settings = Settings() 