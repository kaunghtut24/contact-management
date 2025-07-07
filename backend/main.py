"""
Entry point for Vercel deployment
"""
from app.main import app

# This is the entry point that Vercel will use
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
