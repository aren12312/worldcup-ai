import os
import requests
import random

API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")
BASE_URL = "https://api.football-data.org/v4"

def get_team_rank(team_name):
    """שולף את המיקום של הקבוצה בטבלה מה-API"""
    headers = {'X-Auth-Token': API_KEY}
    try:
        # שליפת טבלת הליגה האנגלית (PL) כברירת מחדל
        response = requests.get(f"{BASE_URL}/competitions/PL/standings", headers=headers, timeout=10)
        standings = response.json().get('standings', [])[0].get('table', [])
        
        for entry in standings:
            if team_name.lower() in entry['team']['name'].lower():
                return entry['position']
        return 10  # ברירת מחדל אם לא נמצאה
    except:
        return 10

def generate_prediction(team1: str, team2: str):
    if not API_KEY:
        return {"error": "Missing API Key"}

    # קבלת דירוג (מיקום נמוך יותר = קבוצה טובה יותר)
    rank1 = get_team_rank(team1)
    rank2 = get_team_rank(team2)

    # חישוב כוח בסיסי (הפוך מהדירוג)
    t1_power = (21 - rank1) + random.randint(1, 5)
    t2_power = (21 - rank2) + random.randint(1, 5)
    
    total = t1_power + t2_power
    p1 = round((t1_power / total) * 100)
    p2 = 100 - p1 - 15  # 15% לתיקו

    return {
        "match": f"{team1} vs {team2}",
        "probabilities": {
            team1: f"{p1}%",
            "Draw": "15%",
            team2: f"{p2}%"
        },
        "ai_insight": f"Based on league standings, {team1 if rank1 < rank2 else team2} is currently ranked higher.",
        "provider": "football-data.org (Live Data)"
    }
