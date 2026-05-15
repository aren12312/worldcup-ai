from fastapi import FastAPI
from app.routes.predictions import router as prediction_router

app = FastAPI(title="WorldCup AI Predictor")

# חיבור הראוטר של התחזיות
app.include_router(prediction_router, prefix="/api/v1")

@app.get("/")
def root():
    return {
        "status": "online",
        "message": "Welcome to WorldCup AI Predictor",
        "docs": "/docs"
    }
