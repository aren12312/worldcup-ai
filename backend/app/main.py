from fastapi import FastAPI
from app.api.predictions import router as prediction_router
from app.api.matches import router as matches_router

app = FastAPI(title="WorldCup AI Professional")

@app.get("/")
def root():
    return {
        "service": "WorldCup AI",
        "status": "running"
    }

@app.get("/health")
def health():
    return {"ok": True}

app.include_router(prediction_router)
app.include_router(matches_router)