import math

import numpy as np


def _poisson_pmf(k: int, lam: float) -> float:
    return (lam ** k) * math.exp(-lam) / math.factorial(k)


def simulate_match(team1_xg: float, team2_xg: float, simulations: int = 10000) -> dict:
    """Poisson-based Monte Carlo match simulation."""
    team1_scores = np.random.poisson(team1_xg, simulations)
    team2_scores = np.random.poisson(team2_xg, simulations)

    team1_wins = int(np.sum(team1_scores > team2_scores))
    team2_wins = int(np.sum(team2_scores > team1_scores))
    draws = simulations - team1_wins - team2_wins

    over_25 = int(np.sum((team1_scores + team2_scores) > 2.5))
    btts = int(np.sum((team1_scores > 0) & (team2_scores > 0)))

    return {
        "team1_win": round(team1_wins / simulations * 100, 1),
        "draw": round(draws / simulations * 100, 1),
        "team2_win": round(team2_wins / simulations * 100, 1),
        "over_2_5": round(over_25 / simulations * 100, 1),
        "btts_yes": round(btts / simulations * 100, 1),
    }


def top_scorelines(team1_xg: float, team2_xg: float, top_n: int = 6) -> list:
    lines = []
    for h in range(6):
        for a in range(6):
            prob = _poisson_pmf(h, team1_xg) * _poisson_pmf(a, team2_xg)
            lines.append({"score": f"{h}-{a}", "probability": round(prob * 100, 2)})

    lines.sort(key=lambda x: x["probability"], reverse=True)
    return lines[:top_n]


def confidence_score(probabilities: dict, has_live_data: bool) -> int:
    favorite = max(probabilities["team1_win"], probabilities["team2_win"])
    margin = abs(probabilities["team1_win"] - probabilities["team2_win"])
    base = min(95, int(favorite * 0.6 + margin * 1.2))
    if has_live_data:
        base = min(95, base + 10)
    return max(35, base)
