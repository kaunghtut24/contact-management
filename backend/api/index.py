import sys
import os

# Add the parent directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.main import app

# Export the app for Vercel
# This will handle all routes through the /api/* pattern
