from fastapi import APIRouter, Query
from app.services.prediction_engine import generate_prediction

router = APIRouter()

@router.get('/predict')
def predict(
    team1: str = Query(..., description="Home team"), 
    team2: str = Query(..., description="Away team")
):
    return generate_prediction(team1, team2)
