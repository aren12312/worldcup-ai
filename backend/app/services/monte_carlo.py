import random

def simulate_match():

    simulations = 5000

    team1 = 0
    draw = 0
    team2 = 0

    for _ in range(simulations):

        team1_score = random.gauss(2.0, 1.0)
        team2_score = random.gauss(1.4, 1.0)

        if team1_score > team2_score:
            team1 += 1

        elif team2_score > team1_score:
            team2 += 1

        else:
            draw += 1

    return {

        "team1_win": round(team1/simulations*100, 2),

        "draw": round(draw/simulations*100, 2),

        "team2_win": round(team2/simulations*100, 2)
    }