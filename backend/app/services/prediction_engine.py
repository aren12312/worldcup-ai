from backend.app.data.hebrew_teams import display_team_name, normalize_team_input
from backend.app.data.key_players import get_key_players
from backend.app.services import match_data
from backend.app.services.analytics_report import build_analytics_report, build_team_comparison
from backend.app.services.i18n import t
from backend.app.services.monte_carlo import confidence_score, simulate_match, top_scorelines
from backend.app.services.research import generate_analysis
from backend.app.services.stats_engine import (
    assess_data_quality,
    build_recommendation,
    compute_expected_goals,
    compute_upset_risk,
)
from backend.app.services.team_resolver import resolve_team
from backend.app.services.weather_api import fetch_match_weather


async def generate_prediction(team1: str, team2: str, lang: str = "he") -> dict:
    if lang not in ("he", "en"):
        lang = "he"

    team1_input = normalize_team_input(team1)
    team2_input = normalize_team_input(team2)

    team1_data = await resolve_team(team1_input)
    team2_data = await resolve_team(team2_input)

    display_team1 = display_team_name(team1_data["name"], lang)
    display_team2 = display_team_name(team2_data["name"], lang)

    context = await match_data.get_match_context(team1_data, team2_data)
    market_odds = await match_data.fetch_market_odds(team1_data["name"], team2_data["name"])
    weather = await fetch_match_weather(team1_data["name"], team2_data["name"])

    team1_xg = compute_expected_goals(team1_data, team2_data)
    team2_xg = compute_expected_goals(team2_data, team1_data)

    probabilities = simulate_match(team1_xg, team2_xg)
    scorelines = top_scorelines(team1_xg, team2_xg)
    confidence = confidence_score(probabilities, context.get("has_live_data", False))

    expected_goals = {display_team1: team1_xg, display_team2: team2_xg}
    upset_risk = compute_upset_risk(probabilities, lang)
    recommendation = build_recommendation(
        display_team1, display_team2, probabilities, expected_goals, lang,
    )

    key_players = {
        display_team1: get_key_players(team1_data["name"], lang),
        display_team2: get_key_players(team2_data["name"], lang),
    }

    comparison = build_team_comparison(
        display_team1, display_team2, team1_data, team2_data, lang,
    )

    analysis_payload = await generate_analysis(
        display_team1, display_team2, team1_data, team2_data,
        expected_goals, probabilities, recommendation, context, lang,
        market_odds=market_odds, weather=weather,
    )

    data_quality = assess_data_quality(team1_data, team2_data, context, lang)
    draw_label = t("draw_label", lang)

    report = build_analytics_report(
        match=f"{display_team1} vs {display_team2}",
        team1=display_team1, team2=display_team2,
        probabilities=probabilities, expected_goals=expected_goals,
        scorelines=scorelines, recommendation=recommendation,
        summary=analysis_payload.get("summary", ""),
        detailed=analysis_payload.get("detailed", ""),
        upset_risk=upset_risk, confidence=confidence,
        key_players=key_players, comparison=comparison, lang=lang,
    )

    return {
        "lang": lang,
        "match": f"{display_team1} vs {display_team2}",
        "confidence": confidence,
        "probabilities": {
            "team1_win": probabilities["team1_win"],
            "draw": probabilities["draw"],
            "team2_win": probabilities["team2_win"],
            "over_2_5": probabilities.get("over_2_5"),
            "btts_yes": probabilities.get("btts_yes"),
        },
        "labels": {"team1": display_team1, "team2": display_team2, "draw": draw_label},
        "expected_goals": expected_goals,
        "scorelines": scorelines,
        "analysis": analysis_payload.get("analysis", []),
        "summary": analysis_payload.get("summary", ""),
        "detailed": analysis_payload.get("detailed", ""),
        "key_factors": analysis_payload.get("key_factors", []),
        "recent_form": analysis_payload.get("recent_form", {}),
        "head_to_head": analysis_payload.get("head_to_head", []),
        "h2h_summary": analysis_payload.get("h2h_summary", ""),
        "key_players": key_players,
        "team_comparison": comparison,
        "report": report,
        "market_odds": market_odds,
        "weather": weather,
        "upset_risk": upset_risk,
        "recommendation": recommendation,
        "data_quality": data_quality,
        "data_sources": {
            display_team1: team1_data.get("source", "database"),
            display_team2: team2_data.get("source", "database"),
        },
        "has_live_data": context.get("has_live_data", False),
    }
