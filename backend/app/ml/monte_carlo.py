import random

def simulate_match():
    simulations = 10000

    team1 = 0
    draw = 0
    team2 = 0

    for _ in range(simulations):
        result = random.random()

        if result < 0.55:
            team1 += 1
        elif result < 0.75:
            draw += 1
        else:
            team2 += 1

    return {
        "team1_win": round(team1/simulations*100, 2),
        "draw": round(draw/simulations*100, 2),
        "team2_win": round(team2/simulations*100, 2),
    }