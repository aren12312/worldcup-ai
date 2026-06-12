import numpy as np


def simulate_match(team1_xg: float, team2_xg: float, simulations: int = 10000) -> dict:
    """Poisson-based Monte Carlo match simulation."""
    team1_scores = np.random.poisson(team1_xg, simulations)
    team2_scores = np.random.poisson(team2_xg, simulations)

    team1_wins = int(np.sum(team1_scores > team2_scores))
    team2_wins = int(np.sum(team2_scores > team1_scores))
    draws = simulations - team1_wins - team2_wins

    return {
        "team1_win": round(team1_wins / simulations * 100, 1),
        "draw": round(draws / simulations * 100, 1),
        "team2_win": round(team2_wins / simulations * 100, 1),
    }
