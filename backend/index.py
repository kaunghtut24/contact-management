import sys
import os
from pathlib import Path

# Add the current directory and app directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir / "app"))

try:
    from app.main import app
    print("Successfully imported app from app.main")
except ImportError as e:
    print(f"Import error: {e}")
    # Fallback to a simple app
    from fastapi import FastAPI
    
    app = FastAPI()
    
    @app.get("/")
    def read_root():
        return {"message": "Fallback API - Import failed", "error": str(e)}
    
    @app.get("/health")
    def health_check():
        return {"status": "fallback", "message": "Fallback API is running"}

# This is what Vercel will use
