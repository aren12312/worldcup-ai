from fastapi import FastAPI
from app.routes.predictions import router as prediction_router

# הגדרת אפליקציית FastAPI
app = FastAPI(
    title="WorldCup AI Predictor",
    description="Football predictions API powered by real-time data",
    version="1.0.0"
)

# חיבור הנתיבים תחת הקידומת /api/v1
app.include_router(prediction_router, prefix="/api/v1", tags=["Predictions"])

@app.get("/")
def root():
    """
    נקודת בדיקה שהשרת באוויר
    """
    return {
        "status": "online",
        "message": "WorldCup AI Predictor API is operational",
        "docs": "/docs"
    }
