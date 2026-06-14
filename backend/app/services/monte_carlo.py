"""Match simulation engine.

Upgrades over a naive independent-Poisson model:
- Dixon-Coles low-score correlation correction (tau) for more realistic 0-0/1-0/0-1/1-1.
- Full bivariate scoreline probability matrix (exact, not only sampled).
- Monte Carlo bootstrap for uncertainty bands (confidence intervals on win probability).
"""

from __future__ import annotations

import math
from typing import Dict, List

import numpy as np

MAX_GOALS = 8
DEFAULT_RHO = -0.06


def _poisson_pmf(k: int, lam: float) -> float:
    return (lam ** k) * math.exp(-lam) / math.factorial(k)


def _dixon_coles_tau(h: int, a: int, lam: float, mu: float, rho: float) -> float:
    """Dixon-Coles dependence correction for low scores."""
    if h == 0 and a == 0:
        return 1.0 - lam * mu * rho
    if h == 0 and a == 1:
        return 1.0 + lam * rho
    if h == 1 and a == 0:
        return 1.0 + mu * rho
    if h == 1 and a == 1:
        return 1.0 - rho
    return 1.0


def score_matrix(team1_xg: float, team2_xg: float, rho: float = DEFAULT_RHO, max_goals: int = MAX_GOALS) -> np.ndarray:
    """Return a (max_goals+1) x (max_goals+1) matrix of scoreline probabilities."""
    home = np.array([_poisson_pmf(i, team1_xg) for i in range(max_goals + 1)])
    away = np.array([_poisson_pmf(j, team2_xg) for j in range(max_goals + 1)])
    matrix = np.outer(home, away)

    for h in range(min(2, max_goals + 1)):
        for a in range(min(2, max_goals + 1)):
            matrix[h, a] *= _dixon_coles_tau(h, a, team1_xg, team2_xg, rho)

    total = matrix.sum()
    if total > 0:
        matrix /= total
    return matrix


def probabilities_from_matrix(matrix: np.ndarray) -> Dict[str, float]:
    n = matrix.shape[0]
    idx = np.arange(n)
    home_grid, away_grid = np.meshgrid(idx, idx, indexing="ij")

    team1_win = float(matrix[home_grid > away_grid].sum())
    team2_win = float(matrix[home_grid < away_grid].sum())
    draw = float(matrix[home_grid == away_grid].sum())

    totals = home_grid + away_grid
    over_25 = float(matrix[totals > 2].sum())
    over_15 = float(matrix[totals > 1].sum())
    over_35 = float(matrix[totals > 3].sum())
    btts = float(matrix[(home_grid > 0) & (away_grid > 0)].sum())

    return {
        "team1_win": round(team1_win * 100, 1),
        "draw": round(draw * 100, 1),
        "team2_win": round(team2_win * 100, 1),
        "over_1_5": round(over_15 * 100, 1),
        "over_2_5": round(over_25 * 100, 1),
        "over_3_5": round(over_35 * 100, 1),
        "btts_yes": round(btts * 100, 1),
    }


def simulate_match(team1_xg: float, team2_xg: float, simulations: int = 10000, rho: float = DEFAULT_RHO) -> dict:
    """Exact probabilities from the Dixon-Coles matrix, plus MC uncertainty bands."""
    matrix = score_matrix(team1_xg, team2_xg, rho)
    probs = probabilities_from_matrix(matrix)

    bands = _bootstrap_bands(team1_xg, team2_xg, simulations)
    probs["bands"] = bands
    return probs


def _bootstrap_bands(team1_xg: float, team2_xg: float, simulations: int, batches: int = 40) -> dict:
    """Bootstrap win-probability confidence bands via batched Poisson sampling."""
    per_batch = max(200, simulations // batches)
    t1_rates, draw_rates, t2_rates = [], [], []
    for _ in range(batches):
        s1 = np.random.poisson(team1_xg, per_batch)
        s2 = np.random.poisson(team2_xg, per_batch)
        t1_rates.append(np.mean(s1 > s2) * 100)
        draw_rates.append(np.mean(s1 == s2) * 100)
        t2_rates.append(np.mean(s2 > s1) * 100)

    def band(values: list) -> dict:
        arr = np.array(values)
        return {
            "low": round(float(np.percentile(arr, 10)), 1),
            "mid": round(float(np.percentile(arr, 50)), 1),
            "high": round(float(np.percentile(arr, 90)), 1),
        }

    return {
        "team1_win": band(t1_rates),
        "draw": band(draw_rates),
        "team2_win": band(t2_rates),
    }


def top_scorelines(team1_xg: float, team2_xg: float, top_n: int = 6, rho: float = DEFAULT_RHO) -> list:
    matrix = score_matrix(team1_xg, team2_xg, rho)
    lines = []
    n = matrix.shape[0]
    for h in range(n):
        for a in range(n):
            lines.append({"score": f"{h}-{a}", "probability": round(float(matrix[h, a]) * 100, 2)})
    lines.sort(key=lambda x: x["probability"], reverse=True)
    return lines[:top_n]


def scoreline_grid(team1_xg: float, team2_xg: float, max_goals: int = 5, rho: float = DEFAULT_RHO) -> List[List[float]]:
    """Probability grid (percentages) for a heatmap, capped at max_goals each side."""
    matrix = score_matrix(team1_xg, team2_xg, rho, max_goals=max(max_goals, MAX_GOALS))
    grid = []
    for h in range(max_goals + 1):
        row = []
        for a in range(max_goals + 1):
            row.append(round(float(matrix[h, a]) * 100, 2))
        grid.append(row)
    return grid


def confidence_score(probabilities: dict, has_live_data: bool) -> int:
    favorite = max(probabilities["team1_win"], probabilities["team2_win"])
    margin = abs(probabilities["team1_win"] - probabilities["team2_win"])
    base = min(95, int(favorite * 0.6 + margin * 1.2))
    if has_live_data:
        base = min(95, base + 10)
    return max(35, base)
