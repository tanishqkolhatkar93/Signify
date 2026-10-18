import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Root directory: c:\Users\tanuu\Downloads\Signify
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = ROOT_DIR / "data"
SIGN_MANIFEST_PATH = DATA_DIR / "sign_manifest.json"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ROOT_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    ENVIRONMENT: str = "development"
    BACKEND_HOST: str = "127.0.0.1"
    BACKEND_PORT: int = 8000
    DATABASE_URL: str = f"sqlite:///{ROOT_DIR / 'backend' / 'signify.db'}"
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000"
    
    # Provider Settings
    PROVIDER_MODE: str = "mock"  # 'mock' or 'verbx'
    VERBX_API_KEY: str = ""
    VERBX_API_BASE_URL: str = "https://one.verbxeco.com/api/v1"
    
    # Vision & Uncertainty Thresholds
    CONFIDENCE_THRESHOLD: float = 0.72
    TEMPORAL_SMOOTHING_FRAMES: int = 5
    UNKNOWN_SIGN_STABILITY_FRAMES: int = 3
    
    # Safety and Privacy
    ALLOW_EVIDENCE_RECORDING: bool = False
    REQUIRE_EXPLICIT_CONSENT: bool = True
    
    # Model Metadata
    MODEL_NAME: str = "Signify-ISL-GeometricNormalizer-v1.0"
    SUPPORTED_SIGN_LANGUAGE: str = "Indian Sign Language (ISL)"
    SUPPORTED_LANGUAGES: list[str] = ["en", "hi"]

settings = Settings()

