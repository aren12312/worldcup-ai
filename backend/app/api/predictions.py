from fastapi import APIRouter, HTTPException, Query

from backend.app.services.prediction_engine import generate_prediction

router = APIRouter()


@router.get("/predict")
async def predict(
    team1: str,
    team2: str,
    lang: str = Query(default="he", pattern="^(he|en)$"),
):
    try:
        return await generate_prediction(team1, team2, lang=lang)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
