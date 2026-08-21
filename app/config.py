"""
Application configuration.

All secrets and environment-specific values are loaded from a .env file
(see .env.example). Never commit a real .env file to source control.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings:
    # General
    APP_NAME: str = "AI Resume Analyzer"
    ENV: str = os.getenv("ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'data' / 'app.db'}"
    )

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    SESSION_COOKIE_NAME: str = os.getenv("SESSION_COOKIE_NAME", "session_id")
    SESSION_EXPIRE_MINUTES: int = int(os.getenv("SESSION_EXPIRE_MINUTES", "1440"))  # 24h
    SESSION_COOKIE_SECURE: bool = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"

    # External services (used by later members, kept here for convenience)
    AI_API_KEY: str = os.getenv("AI_API_KEY", "")
    AI_MODEL: str = os.getenv("AI_MODEL", "gemini-3.6-flash")

    # CORS
    ALLOWED_ORIGINS: list[str] = os.getenv(
        "ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173"
    ).split(",")

    # Uploads
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", str(BASE_DIR / "uploads"))


settings = Settings()

if not settings.SECRET_KEY and settings.ENV != "test":
    raise RuntimeError(
        "SECRET_KEY is not set. Copy .env.example to .env and set a real value."
    )
