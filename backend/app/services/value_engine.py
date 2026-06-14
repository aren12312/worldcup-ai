"""Value engine: compare model probabilities to bookmaker odds.

Computes de-vigged (overround-removed) market probabilities, the model's edge over
the market, fair odds, and a fractional-Kelly stake suggestion. This is the kind of
analysis pro bettors run but consumer prediction sites rarely expose.
"""

from __future__ import annotations

from typing import Dict, List, Optional

KELLY_FRACTION = 0.25


def _match_outcome_odds(odds: Dict[str, float], team1: str, team2: str) -> Optional[Dict[str, float]]:
    """Map bookmaker outcome names to team1 / draw / team2 decimal odds."""
    if not odds:
        return None

    t1 = team1.lower()
    t2 = team2.lower()
    mapped: Dict[str, float] = {}

    for name, price in odds.items():
        if not price:
            continue
        key = name.lower()
        if "draw" in key or "tie" in key or key in ("x", "תיקו"):
            mapped["draw"] = float(price)
        elif key in t1 or t1 in key:
            mapped["team1"] = float(price)
        elif key in t2 or t2 in key:
            mapped["team2"] = float(price)

    if {"team1", "team2"} <= mapped.keys():
        return mapped
    return None


def build_value_analysis(
    model_probabilities: Dict[str, float],
    market_odds: Optional[dict],
    team1: str,
    team2: str,
    lang: str = "he",
) -> Optional[dict]:
    if not market_odds:
        return None

    odds = _match_outcome_odds(market_odds.get("odds", {}), team1, team2)
    if not odds:
        return None

    implied_raw = {k: 1.0 / v for k, v in odds.items() if v}
    overround = sum(implied_raw.values())
    if overround <= 0:
        return None

    fair_market = {k: (v / overround) * 100 for k, v in implied_raw.items()}

    model = {
        "team1": model_probabilities.get("team1_win", 0.0),
        "draw": model_probabilities.get("draw", 0.0),
        "team2": model_probabilities.get("team2_win", 0.0),
    }

    outcomes: List[dict] = []
    labels = {
        "team1": team1,
        "draw": "תיקו" if lang == "he" else "Draw",
        "team2": team2,
    }

    best = None
    for key in ("team1", "draw", "team2"):
        if key not in odds:
            continue
        decimal = odds[key]
        model_p = model.get(key, 0.0) / 100.0
        market_p = fair_market.get(key, 0.0) / 100.0
        edge = (model_p * decimal - 1.0) * 100.0
        b = decimal - 1.0
        kelly = ((model_p * decimal - 1.0) / b) if b > 0 else 0.0
        stake = max(0.0, kelly) * KELLY_FRACTION * 100.0

        row = {
            "outcome": labels[key],
            "decimal_odds": round(decimal, 2),
            "model_prob": round(model.get(key, 0.0), 1),
            "market_prob": round(fair_market.get(key, 0.0), 1),
            "edge": round(edge, 1),
            "fair_odds": round(1.0 / model_p, 2) if model_p > 0 else None,
            "kelly_stake_pct": round(stake, 1),
        }
        outcomes.append(row)
        if edge > 0 and (best is None or edge > best["edge"]):
            best = row

    if lang == "he":
        if best:
            verdict = (
                f"💎 ערך מזוהה: {best['outcome']} ביחס {best['decimal_odds']} "
                f"(Edge {best['edge']}%, הימור Kelly {best['kelly_stake_pct']}% מהבנקרול)"
            )
        else:
            verdict = "אין ערך חיובי מול השוק — המודל מסכים עם המחיר."
    else:
        if best:
            verdict = (
                f"Value found: {best['outcome']} @ {best['decimal_odds']} "
                f"(Edge {best['edge']}%, Kelly {best['kelly_stake_pct']}%)"
            )
        else:
            verdict = "No positive edge vs market."

    return {
        "outcomes": outcomes,
        "overround_pct": round((overround - 1.0) * 100, 1),
        "best_value": best,
        "verdict": verdict,
        "source": market_odds.get("source", "market"),
    }
