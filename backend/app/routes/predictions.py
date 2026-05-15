from fastapi import APIRouter, Query
from app.services.prediction_engine import generate_prediction

router = APIRouter()

@router.get('/predict')
def predict(
    team1: str = Query(..., description="Home team name"), 
    team2: str = Query(..., description="Away team name")
):
    """
    API Endpoint לקבלת תחזית למשחק.
    שימוש: /api/v1/predict?team1=Argentina&team2=France
    """
    return generate_prediction(team1, team2)
