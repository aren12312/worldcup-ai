from fastapi import APIRouter
from app.engines.prediction_engine import generate_prediction

router = APIRouter(prefix="/predictions", tags=["predictions"])

@router.get("/")
async def predict(team1: str, team2: str):
    return generate_prediction(team1, team2)