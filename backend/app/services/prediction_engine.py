from backend.app.data.hebrew_teams import display_team_name, normalize_team_input
from backend.app.services import api_football
from backend.app.services.i18n import t
from backend.app.services.monte_carlo import simulate_match
from backend.app.services.research import generate_analysis
from backend.app.services.stats_engine import (
    assess_data_quality,
    build_recommendation,
    compute_expected_goals,
    compute_upset_risk,
)
from backend.app.services.team_resolver import resolve_team


async def generate_prediction(team1: str, team2: str, lang: str = "he") -> dict:
    if lang not in ("he", "en"):
        lang = "he"

    team1_input = normalize_team_input(team1)
    team2_input = normalize_team_input(team2)

    team1_data = await resolve_team(team1_input)
    team2_data = await resolve_team(team2_input)

    display_team1 = display_team_name(team1_data["name"], lang)
    display_team2 = display_team_name(team2_data["name"], lang)

    context = await api_football.get_match_context(team1_data, team2_data)

    team1_xg = compute_expected_goals(team1_data, team2_data)
    team2_xg = compute_expected_goals(team2_data, team1_data)

    probabilities = simulate_match(team1_xg, team2_xg)

    expected_goals = {
        display_team1: team1_xg,
        display_team2: team2_xg,
    }

    upset_risk = compute_upset_risk(probabilities, lang)
    recommendation = build_recommendation(
        display_team1,
        display_team2,
        probabilities,
        expected_goals,
        lang,
    )

    analysis_payload = await generate_analysis(
        display_team1,
        display_team2,
        team1_data,
        team2_data,
        expected_goals,
        probabilities,
        recommendation,
        context,
        lang,
    )

    data_quality = assess_data_quality(team1_data, team2_data, context, lang)

    draw_label = t("draw_label", lang)

    return {
        "lang": lang,
        "match": f"{display_team1} vs {display_team2}",
        "probabilities": {
            "team1_win": probabilities["team1_win"],
            "draw": probabilities["draw"],
            "team2_win": probabilities["team2_win"],
        },
        "labels": {
            "team1": display_team1,
            "team2": display_team2,
            "draw": draw_label,
        },
        "expected_goals": expected_goals,
        "analysis": analysis_payload.get("analysis", []),
        "summary": analysis_payload.get("summary", ""),
        "detailed": analysis_payload.get("detailed", ""),
        "key_factors": analysis_payload.get("key_factors", []),
        "recent_form": analysis_payload.get("recent_form", {}),
        "head_to_head": analysis_payload.get("head_to_head", []),
        "h2h_summary": analysis_payload.get("h2h_summary", ""),
        "upset_risk": upset_risk,
        "recommendation": recommendation,
        "data_quality": data_quality,
        "data_sources": {
            display_team1: team1_data.get("source", "database"),
            display_team2: team2_data.get("source", "database"),
        },
        "has_live_data": context.get("has_live_data", False),
    }
