from fastapi import APIRouter

from backend.app.services.prediction_engine import generate_prediction

router = APIRouter()

@router.get("/predict")

async def predict(team1: str, team2: str):

    prediction = generate_prediction(team1, team2)

    return prediction