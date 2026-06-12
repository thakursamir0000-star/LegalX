"""
Configuration management for the LegalX Knowledge Centre backend.
Loads settings from environment variables with sensible defaults.
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load .env file from the backend directory
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # --- API Keys ---
    GEMINI_API_KEY: str = ""

    # --- Paths ---
    BASE_DIR: Path = BASE_DIR
    DATA_DIR: Path = BASE_DIR / "data"
    SOURCES_DIR: Path = BASE_DIR / "data" / "sources"
    CACHE_DIR: Path = BASE_DIR / "data" / "cache"
    AUDIO_DIR: Path = BASE_DIR / "data" / "audio"
    CHROMA_DIR: Path = BASE_DIR / "chroma_db"

    # --- Text Splitting ---
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200

    # --- Gemini ---
    GEMINI_MODEL: str = "gemini-2.5-flash-lite"
    GEMINI_EMBEDDING_MODEL: str = "models/gemini-embedding-001"

    # --- TTS ---
    TTS_VOICE: str = "en-US-AriaNeural"
    TTS_RATE: str = "+0%"

    # --- Server ---
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # --- Topic Configuration ---
    TOPIC_METADATA: dict = {
        "pocso_act": {
            "name": "POCSO Act",
            "icon": "Shield",
            "description": "Protection of Children from Sexual Offences Act, 2012",
        },
        "consumer_protection_act": {
            "name": "Consumer Protection Act",
            "icon": "ShoppingCart",
            "description": "Consumer Protection Act, 2019 – Rights and Remedies",
        },
        "cyber_crime_laws": {
            "name": "Cyber Crime Laws",
            "icon": "Monitor",
            "description": "Information Technology Act and Cyber Crime Provisions",
        },
        "rti_act": {
            "name": "RTI Act",
            "icon": "FileText",
            "description": "Right to Information Act, 2005 – Transparency in Governance",
        },
        "gst_registration": {
            "name": "GST Registration",
            "icon": "Receipt",
            "description": "Goods and Services Tax Registration Process and Rules",
        },
    }

    class Config:
        env_file = ".env"
        extra = "ignore"


# Singleton settings instance
settings = Settings()

# Ensure GOOGLE_API_KEY is set in the environment for the google-genai SDK
# (used internally by langchain-google-genai v4.x)
if settings.GEMINI_API_KEY and not os.environ.get("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = settings.GEMINI_API_KEY


def ensure_directories() -> None:
    """Create all required data directories if they don't exist."""
    for dir_path in [settings.CACHE_DIR, settings.AUDIO_DIR, settings.CHROMA_DIR]:
        dir_path.mkdir(parents=True, exist_ok=True)

