from backend.app.services.monte_carlo import simulate_match
from backend.app.services.research import generate_analysis
from backend.app.services.stats_engine import (
    build_recommendation,
    compute_expected_goals,
    compute_upset_risk,
)
from backend.app.services.team_resolver import resolve_team


async def generate_prediction(team1: str, team2: str) -> dict:
    team1_data = await resolve_team(team1)
    team2_data = await resolve_team(team2)

    display_team1 = team1_data["name"]
    display_team2 = team2_data["name"]

    team1_xg = compute_expected_goals(team1_data, team2_data)
    team2_xg = compute_expected_goals(team2_data, team1_data)

    probabilities = simulate_match(team1_xg, team2_xg)

    expected_goals = {
        display_team1: team1_xg,
        display_team2: team2_xg,
    }

    upset_risk = compute_upset_risk(probabilities)
    recommendation = build_recommendation(
        display_team1,
        display_team2,
        probabilities,
        expected_goals,
    )

    analysis = await generate_analysis(
        display_team1,
        display_team2,
        team1_data,
        team2_data,
        expected_goals,
        probabilities,
        recommendation,
    )

    return {
        "match": f"{display_team1} vs {display_team2}",
        "probabilities": probabilities,
        "expected_goals": expected_goals,
        "analysis": analysis,
        "upset_risk": upset_risk,
        "recommendation": recommendation,
        "data_sources": {
            display_team1: team1_data.get("source", "database"),
            display_team2: team2_data.get("source", "database"),
        },
    }
