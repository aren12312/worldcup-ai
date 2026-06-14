from __future__ import annotations

from typing import Dict, List

from backend.app.services.i18n import t


def compute_expected_goals(
    team: dict,
    opponent: dict,
    *,
    home_advantage: float = 1.0,
) -> float:
    """Expected goals from ratings + real recent scoring averages when available."""
    if team.get("avg_goals_scored") is not None and opponent.get("avg_goals_conceded") is not None:
        base = (team["avg_goals_scored"] + opponent["avg_goals_conceded"]) / 2
        form = 0.6 + team.get("form", 0.7) * 0.4
        xg = base * form * home_advantage
        return round(max(0.45, min(3.5, xg)), 2)

    attack = team["attack"] / 100.0
    defense_factor = 1.15 - (opponent["defense"] / 250.0)
    form = 0.55 + team.get("form", 0.7) * 0.45
    xg = attack * defense_factor * form * 2.8 * home_advantage
    return round(max(0.55, min(3.2, xg)), 2)


def expected_goals_breakdown(
    team: dict,
    opponent: dict,
    *,
    home_advantage: float = 1.0,
    lang: str = "he",
) -> Dict:
    """Decompose the final xG into additive factor contributions for explainability.

    Returns the total xG plus a list of {label, value} contributions that sum to it.
    """
    xg = compute_expected_goals(team, opponent, home_advantage=home_advantage)

    attack_strength = team.get("attack", 75) / 100.0
    opp_defense = opponent.get("defense", 75) / 100.0
    form = team.get("form", 0.7)

    he = lang == "he"
    baseline = 1.30

    attack_contrib = (attack_strength - 0.75) * 1.6
    defense_contrib = (0.75 - opp_defense) * 1.4
    form_contrib = (form - 0.7) * 1.2
    home_contrib = (home_advantage - 1.0) * baseline

    raw = baseline + attack_contrib + defense_contrib + form_contrib + home_contrib
    scale = xg / raw if raw > 0 else 1.0

    factors = [
        {"label": "בסיס" if he else "Baseline", "value": round(baseline * scale, 2)},
        {"label": "כושר התקפה" if he else "Attack", "value": round(attack_contrib * scale, 2)},
        {"label": "הגנת היריב" if he else "Opp. defense", "value": round(defense_contrib * scale, 2)},
        {"label": "טופס" if he else "Form", "value": round(form_contrib * scale, 2)},
    ]
    if abs(home_contrib) > 0.001:
        factors.append({"label": "יתרון מיקום" if he else "Venue", "value": round(home_contrib * scale, 2)})

    return {"xg": xg, "factors": factors}


def compute_upset_risk(probabilities: dict, lang: str = "he") -> str:
    favorite = max(probabilities["team1_win"], probabilities["team2_win"])
    if favorite >= 55:
        return t("upset_low", lang)
    if favorite >= 38:
        return t("upset_medium", lang)
    return t("upset_high", lang)


def build_recommendation(
    team1: str,
    team2: str,
    probabilities: dict,
    expected_goals: dict,
    lang: str = "he",
) -> str:
    t1_win = probabilities["team1_win"]
    t2_win = probabilities["team2_win"]
    draw = probabilities["draw"]

    if abs(t1_win - t2_win) < 8 and draw >= 22:
        return t("rec_draw", lang, draw=draw)

    if t1_win > t2_win:
        favorite = team1
        margin = t1_win - t2_win
        xg_diff = expected_goals[team1] - expected_goals[team2]
    else:
        favorite = team2
        margin = t2_win - t1_win
        xg_diff = expected_goals[team2] - expected_goals[team1]

    if margin >= 20:
        confidence = t("confidence_high", lang)
    elif margin >= 10:
        confidence = t("confidence_medium", lang)
    else:
        confidence = t("confidence_low", lang)

    return t(
        "rec_win",
        lang,
        favorite=favorite,
        confidence=confidence,
        xg_diff=abs(xg_diff),
    )


def assess_data_quality(team1: dict, team2: dict, context: dict, lang: str = "he") -> str:
    from backend.app.services.config import has_live_data_api

    live_sources = sum(
        1
        for team in (team1, team2)
        if team.get("source") in ("api_football_live", "football_data_live", "curated_database") and team.get("recent_matches")
    )
    if live_sources == 2 and context.get("head_to_head"):
        return t("data_quality_high", lang)
    if live_sources >= 1:
        return t("data_quality_medium", lang)
    if has_live_data_api():
        return t("data_quality_api_no_matches", lang)
    return t("data_quality_low", lang)
