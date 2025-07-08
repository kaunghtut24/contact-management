from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# Create a simple FastAPI app
app = FastAPI()

# CORS Configuration
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello from Vercel API!", "status": "working"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "API is running from /api folder"}

@app.get("/contacts")
def get_contacts():
    return {"message": "Contacts endpoint working", "contacts": []}
