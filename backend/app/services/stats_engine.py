from __future__ import annotations

from typing import List

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
