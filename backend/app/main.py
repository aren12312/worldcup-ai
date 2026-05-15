from fastapi import FastAPI
from app.routes.predictions import router as prediction_router

app = FastAPI(title="WorldCup AI Predictor")
app.include_router(prediction_router)

@app.get("/")
def root():
    return {"status": "running", "service": "WorldCup AI Predictor"}
