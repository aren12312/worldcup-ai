from app.services.monte_carlo import simulate_match

def generate_prediction(team1, team2):

    simulation = simulate_match()

    return {
        "match": f"{team1} vs {team2}",

        "probabilities": simulation,

        "expected_goals": {
            team1: 2.1,
            team2: 1.3
        },

        "analysis": [
            f"{team1} stronger attacking form",
            f"{team2} defensive instability",
            "High tempo expected"
        ],

        "upset_risk": "medium"
    }