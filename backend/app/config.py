import os
from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "SupportSwarm"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supportswarm-insecure-secret-key-for-dev-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Database configuration (PostgreSQL with fallback to SQLite for zero-dep local runs/tests)
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"sqlite+aiosqlite:///{BASE_DIR}/supportswarm.db"
    )
    SYNC_DATABASE_URL: str = os.getenv(
        "SYNC_DATABASE_URL",
        f"sqlite:///{BASE_DIR}/supportswarm.db"
    )
    
    # Redis configuration
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Storage configuration for voice recordings and attachments
    STORAGE_DIR: str = os.getenv("STORAGE_DIR", str(BASE_DIR / "storage"))
    
    # AI and Adapter configuration
    AI_MODEL_PROVIDER: str = os.getenv("AI_MODEL_PROVIDER", "mock_hermes")
    HERMES_API_URL: Optional[str] = os.getenv("HERMES_API_URL", None)
    PAPERCLIP_API_URL: Optional[str] = os.getenv("PAPERCLIP_API_URL", None)
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", None)
    
    # Thresholds and parameters
    CONFIDENCE_THRESHOLD_MIN: float = 0.70
    INCIDENT_WINDOW_MINUTES: int = 30
    INCIDENT_MIN_TICKETS: int = 5
    
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ]

    model_config = ConfigDict(case_sensitive=True, env_file=".env", extra="ignore")

settings = Settings()

# Ensure local storage directory exists
os.makedirs(settings.STORAGE_DIR, exist_ok=True)
os.makedirs(os.path.join(settings.STORAGE_DIR, "audio"), exist_ok=True)
os.makedirs(os.path.join(settings.STORAGE_DIR, "attachments"), exist_ok=True)
