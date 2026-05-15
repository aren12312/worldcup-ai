from fastapi import FastAPI
from app.routes.predictions import router as prediction_router

# יצירת מופע האפליקציה
app = FastAPI(
    title="WorldCup AI Predictor",
    description="API for football match predictions using AI and real-time data",
    version="1.0.0"
)

# חיבור הראוטר של התחזיות תחת קידומת /api/v1
app.include_router(prediction_router, prefix="/api/v1", tags=["Predictions"])

@app.get("/")
def root():
    """
    נתיב בדיקת תקינות (Health Check)
    """
    return {
        "status": "online",
        "message": "Welcome to WorldCup AI Predictor API",
        "documentation": "/docs"
    }
