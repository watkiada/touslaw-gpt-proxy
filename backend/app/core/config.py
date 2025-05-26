"""
Configuration settings for the application
"""
import os
import secrets
from typing import List, Optional, Union
from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API settings
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # CORS settings
    CORS_ORIGINS: List[Union[str, AnyHttpUrl]] = ["http://localhost", "http://localhost:3000", "http://localhost:8000"]
    
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Database settings
    DATABASE_URL: str = "sqlite:///./myaidrive.db"
    
    # Storage settings
    STORAGE_PATH: str = "./storage"
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100 MB
    
    # OCR settings
    OCR_USE_TESSERACT: bool = True
    OCR_USE_EASYOCR: bool = False
    OCR_LANGUAGES: List[str] = ["eng"]
    
    # AI settings
    OPENAI_API_KEY: Optional[str] = None
    DEFAULT_AI_PROVIDER: str = "openai"
    DEFAULT_AI_MODEL: str = "gpt-4"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    
    # Vector DB settings
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_ENVIRONMENT: Optional[str] = None
    PINECONE_INDEX_NAME: str = "myaidrive"
    
    # Document processing settings
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    MAX_CONTEXT_CHUNKS: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()
