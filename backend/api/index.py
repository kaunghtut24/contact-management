"""
Vercel entry point for FastAPI application
"""
from app.main import app

# This is the entry point that Vercel will use
handler = app
