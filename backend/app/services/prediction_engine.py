import random

def generate_prediction(team1: str, team2: str):
    t1 = random.randint(60,90)
    t2 = random.randint(60,90)
    total = t1+t2
    return {
        'team1': team1,
        'team2': team2,
        'team1_win_probability': round((t1/total)*100),
        'draw_probability': 10,
        'team2_win_probability': round((t2/total)*100)-10,
        'analysis': [
            f'{team1} has stronger momentum',
            f'{team2} performs well in knockout stages'
        ]
    }
