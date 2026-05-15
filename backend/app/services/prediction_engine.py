import os
import requests
import random

API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")
BASE_URL = "https://api.football-data.org/v4"
HEADERS = {'X-Auth-Token': API_KEY}

# מילון עזר לתרגום שמות נפוצים מעברית/קיצורים
TEAM_MAPPING = {
    "ריאל מדריד": "Real Madrid",
    "ארסנל": "Arsenal",
    "ברצלונה": "FC Barcelona",
    "מנצסטר סיטי": "Manchester City",
    "ליברפול": "Liverpool"
}

def get_team_info(name):
    name = TEAM_MAPPING.get(name, name)
    try:
        # חיפוש גלובלי של הקבוצה ב-API
        res = requests.get(f"{BASE_URL}/teams?name={name}", headers=HEADERS, timeout=5)
        data = res.json()
        if data.get('teams'):
            team = data['teams'][0]
            return team['id'], team['name'], team.get('runningCompetitions', [{}])[0].get('code', 'PL')
    except:
        pass
    return None, name, 'PL'

def get_standings_pos(team_id, league_code):
    try:
        res = requests.get(f"{BASE_URL}/competitions/{league_code}/standings", headers=HEADERS, timeout=5)
        table = res.json()['standings'][0]['table']
        for row in table:
            if row['team']['id'] == team_id:
                return row['position'], row['playedGames'], row['goalDifference']
    except:
        pass
    return 10, 20, 0 # ברירת מחדל

def generate_prediction(t1_name, t2_name):
    id1, name1, league1 = get_team_info(t1_name)
    id2, name2, league2 = get_team_info(t2_name)

    pos1, played1, gd1 = get_standings_pos(id1, league1) if id1 else (10, 20, 0)
    pos2, played2, gd2 = get_standings_pos(id2, league2) if id2 else (11, 20, 0)

    # לוגיקת חיזוי המבוססת על מיקום בטבלה והפרש שערים
    score1 = (20 - pos1) + (gd1 * 0.5)
    score2 = (20 - pos2) + (gd2 * 0.5)
    
    total = score1 + score2 + 10
    prob1 = min(max(int((score1 / total) * 100), 20), 75)
    prob2 = 100 - prob1 - 15

    return {
        "match": f"{name1} vs {name2}",
        "probabilities": {"home": f"{prob1}%", "draw": "15%", "away": f"{prob2}%"},
        "details": {
            "pos1": pos1, "pos2": pos2,
            "league": league1 if league1 == league2 else f"{league1}/{league2}"
        },
        "analysis": f"לפי הטבלה ב-{league1}, {name1} במקום ה-{pos1} ו-{name2} במקום ה-{pos2}. הפרש השערים של {name1} הוא {gd1}."
    }
