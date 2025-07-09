import os
from typing import List
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(env_path)
except ImportError:
    # python-dotenv not installed, skip loading .env file
    pass

class Settings:
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./contact_db.sqlite")

    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

    # CORS
    _origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,https://contact-management-six-alpha.vercel.app,https://contact-management-vi36.vercel.app").split(",")
    # Always add localhost:3000 and localhost:5173 for local dev if not present
    if "http://localhost:5173" not in _origins:
        _origins.append("http://localhost:5173")
    if "http://localhost:3000" not in _origins:
        _origins.append("http://localhost:3000")
    ALLOWED_ORIGINS: List[str] = [o.strip() for o in _origins if o.strip()]

    # File Upload
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads/")

    # OCR
    TESSERACT_PATH: str = os.getenv("TESSERACT_PATH", "/usr/bin/tesseract")

print(f"[DEBUG] ALLOWED_ORIGINS: {Settings.ALLOWED_ORIGINS}")

settings = Settings()
