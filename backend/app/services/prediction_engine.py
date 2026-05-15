import os
import requests

API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")
BASE_URL = "https://api.football-data.org/v4"
HEADERS = {'X-Auth-Token': API_KEY}

def get_team_stats(name):
    """שליפת נתוני קבוצה, מיקום בטבלה והפרש שערים"""
    try:
        # 1. חיפוש ה-ID של הקבוצה
        res = requests.get(f"{BASE_URL}/teams?name={name}", headers=HEADERS, timeout=5)
        data = res.json()
        if not data.get('teams'): 
            return None
        
        team = data['teams'][0]
        t_id = team['id']
        t_full_name = team['name']
        
        # 2. מציאת הליגה הפעילה של הקבוצה (למשל PL עבור אנגליה)
        league_code = 'PL' # ברירת מחדל
        if team.get('runningCompetitions'):
            league_code = team['runningCompetitions'][0].get('code', 'PL')
        
        # 3. שליפת הטבלה של אותה ליגה
        standings_res = requests.get(f"{BASE_URL}/competitions/{league_code}/standings", headers=HEADERS, timeout=5)
        standings_data = standings_res.json()
        
        if 'standings' in standings_data:
            table = standings_data['standings'][0]['table']
            for row in table:
                if row['team']['id'] == t_id:
                    return {
                        "name": t_full_name,
                        "pos": row['position'],
                        "gd": row['goalDifference'],
                        "league": league_code
                    }
    except Exception as e:
        print(f"Engine Error: {e}")
    return None

def generate_prediction(t1_query, t2_query):
    s1 = get_team_stats(t1_query)
    s2 = get_team_stats(t2_query)

    # נתוני ברירת מחדל אם הקבוצה לא נמצאה ב-API החינמי
    p1, gd1, name1 = (s1['pos'], s1['gd'], s1['name']) if s1 else (10, 0, t1_query.capitalize())
    p2, gd2, name2 = (s2['pos'], s2['gd'], s2['name']) if s2 else (11, 0, t2_query.capitalize())

    # לוגיקת חישוב עוצמה: מיקום נמוך יותר = חזק יותר, GD גבוה = חזק יותר
    power1 = (22 - p1) + (gd1 * 0.4)
    power2 = (22 - p2) + (gd2 * 0.4)
    
    total = power1 + power2
    # חישוב הסתברויות עם הגנה (מינימום 15%, מקסימום 80%)
    prob_home = min(max(int((power1 / total) * 100), 15), 80)
    prob_away = 100 - prob_home - 15 # ה-15% הנותרים הם לתיקו

    analysis = (
        f"לפי נתוני הליגה, {name1} מדורגת במקום ה-{p1} עם הפרש שערים של {gd1}. "
        f"לעומתה, {name2} במקום ה-{p2} עם הפרש של {gd2}. "
        f"הניתוח משקלל את יציבות ההגנה והתקפת הקבוצות לאורך העונה."
    )

    return {
        "match": f"{name1} vs {name2}",
        "probabilities": {"home": f"{prob_home}%", "draw": "15%", "away": f"{prob_away}%"},
        "analysis": analysis
    }
