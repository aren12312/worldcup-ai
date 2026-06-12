from fastapi import APIRouter, HTTPException

from backend.app.services.prediction_engine import generate_prediction

router = APIRouter()


@router.get("/predict")
async def predict(team1: str, team2: str):
    try:
        return await generate_prediction(team1, team2)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
