import random

def generate_prediction(team1: str, team2: str):
    team1_win = random.randint(35, 60)
    draw = random.randint(10, 25)
    team2_win = 100 - team1_win - draw

    return {
        "team1": team1,
        "team2": team2,
        "probabilities": {
            "team1_win": team1_win,
            "draw": draw,
            "team2_win": team2_win
        },
        "analysis": [
            f"{team1} strong attacking momentum",
            f"{team2} vulnerable defensively",
            "Weather conditions favor high pressing"
        ],
        "upset_risk": "medium"
    }