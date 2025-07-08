from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello from Vercel!"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Simple test API is running"}
