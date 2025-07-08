from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World", "message": "This is a minimal FastAPI test"}

@app.get("/health")
def health():
    return {"status": "ok"}
