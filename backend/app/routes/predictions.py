from fastapi import APIRouter, Query
from app.services.prediction_engine import generate_prediction

router = APIRouter()

@router.get('/predict')
def predict(
    team1: str = Query(..., description="Name of the first team"), 
    team2: str = Query(..., description="Name of the second team")
):
    """
    מקבל שתי קבוצות ומחזיר ניתוח הסתברויות לניצחון.
    דוגמה: /api/v1/predict?team1=Brazil&team2=France
    """
    result = generate_prediction(team1, team2)
    return result
