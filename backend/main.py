import sys
import os

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(__file__))

from app.main import app

# Export the app for Vercel
# Vercel will use this FastAPI app directly
