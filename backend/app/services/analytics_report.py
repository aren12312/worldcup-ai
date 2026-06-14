from __future__ import annotations

from backend.app.data.key_players import get_key_players


def build_team_comparison(team1: str, team2: str, team1_data: dict, team2_data: dict, lang: str = "he") -> dict:
    metrics = [
        ("attack", "התקפה" if lang == "he" else "Attack"),
        ("defense", "הגנה" if lang == "he" else "Defense"),
        ("form", "טופס" if lang == "he" else "Form"),
    ]
    comparison = {}
    for key, label in metrics:
        v1 = team1_data.get(key, 0)
        v2 = team2_data.get(key, 0)
        if key == "form":
            v1, v2 = round(v1 * 100), round(v2 * 100)
        comparison[key] = {"label": label, "team1": v1, "team2": v2}

    return {
        "metrics": comparison,
        "team1": {
            "goals_scored_avg": team1_data.get("avg_goals_scored"),
            "goals_conceded_avg": team1_data.get("avg_goals_conceded"),
            "form_string": team1_data.get("form_string", ""),
        },
        "team2": {
            "goals_scored_avg": team2_data.get("avg_goals_scored"),
            "goals_conceded_avg": team2_data.get("avg_goals_conceded"),
            "form_string": team2_data.get("form_string", ""),
        },
    }


def build_analytics_report(
    match: str,
    team1: str,
    team2: str,
    probabilities: dict,
    expected_goals: dict,
    scorelines: list,
    recommendation: str,
    summary: str,
    detailed: str,
    upset_risk: str,
    confidence: int,
    key_players: dict,
    comparison: dict,
    lang: str = "he",
) -> dict:
    if lang == "he":
        sections = [
            {"title": "סיכום מנהלים", "content": summary},
            {"title": "המלצת המודל", "content": recommendation},
            {"title": "ניתוח מעמיק", "content": detailed},
            {
                "title": "הסתברויות",
                "content": (
                    f"{team1}: {probabilities['team1_win']}% | "
                    f"תיקו: {probabilities['draw']}% | "
                    f"{team2}: {probabilities['team2_win']}%"
                ),
            },
            {
                "title": "שוקי משנה",
                "content": (
                    f"Over 2.5: {probabilities.get('over_2_5', 'N/A')}% | "
                    f"BTTS: {probabilities.get('btts_yes', 'N/A')}% | "
                    f"סיכון אפסט: {upset_risk} | ביטחון: {confidence}/100"
                ),
            },
        ]
    else:
        sections = [
            {"title": "Executive Summary", "content": summary},
            {"title": "Recommendation", "content": recommendation},
            {"title": "Deep Analysis", "content": detailed},
        ]

    return {
        "match": match,
        "confidence": confidence,
        "sections": sections,
        "scorelines": scorelines,
        "key_players": key_players,
        "comparison": comparison,
    }
