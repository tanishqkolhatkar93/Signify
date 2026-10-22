import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Robust root & data directory discovery
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
candidates = [
    ROOT_DIR,
    Path.cwd(),
    Path(__file__).resolve().parent.parent.parent,
    Path(__file__).resolve().parent.parent.parent.parent,
]
DATA_DIR = ROOT_DIR / "data"
for c in candidates:
    if (c / "data" / "sign_manifest.json").exists():
        ROOT_DIR = c
        DATA_DIR = c / "data"
        break

SIGN_MANIFEST_PATH = DATA_DIR / "sign_manifest.json"

# Ensure database directory exists
DB_DIR = ROOT_DIR / "backend"
DB_DIR.mkdir(parents=True, exist_ok=True)

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ROOT_DIR / ".env") if (ROOT_DIR / ".env").exists() else None,
        env_file_encoding="utf-8",
        extra="ignore"
    )

    ENVIRONMENT: str = "production"
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = int(os.environ.get("PORT", 8000))
    DATABASE_URL: str = f"sqlite:///{DB_DIR / 'signify.db'}"
    CORS_ORIGINS: str = "*"
    
    # Provider Settings
    PROVIDER_MODE: str = "verbx"  # 'mock' or 'verbx'
    VERBX_API_KEY: str = ""
    VERBX_API_BASE_URL: str = "https://api.verbxeco.com"
    
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

    # Authentication & Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    JWT_SECRET: str = "signify-secret-key-2026-hackathon-token"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRES_MINUTES: int = 60 * 24 * 7

settings = Settings()
