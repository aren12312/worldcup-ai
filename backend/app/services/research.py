from __future__ import annotations

import json
import os
from typing import List, Optional

import httpx

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


async def generate_analysis(
    team1: str,
    team2: str,
    team1_data: dict,
    team2_data: dict,
    expected_goals: dict,
    probabilities: dict,
    recommendation: str,
) -> List[str]:
    if OPENAI_API_KEY:
        llm_analysis = await _llm_analysis(
            team1,
            team2,
            team1_data,
            team2_data,
            expected_goals,
            probabilities,
            recommendation,
        )
        if llm_analysis:
            return llm_analysis

    return _fallback_analysis(
        team1,
        team2,
        team1_data,
        team2_data,
        expected_goals,
        probabilities,
    )


async def _llm_analysis(
    team1: str,
    team2: str,
    team1_data: dict,
    team2_data: dict,
    expected_goals: dict,
    probabilities: dict,
    recommendation: str,
) -> Optional[List[str]]:
    prompt = f"""You are a professional football analyst for World Cup matches.
Analyze this match using ONLY the data provided. Respond in English with exactly 3 bullet points.

Match: {team1} vs {team2}

{team1} ratings — attack: {team1_data['attack']}, defense: {team1_data['defense']}, form: {team1_data['form']}
{team2} ratings — attack: {team2_data['attack']}, defense: {team2_data['defense']}, form: {team2_data['form']}

Expected goals: {team1} {expected_goals[team1]}, {team2} {expected_goals[team2]}
Win probabilities: {team1} {probabilities['team1_win']}%, Draw {probabilities['draw']}%, {team2} {probabilities['team2_win']}%
Recommendation: {recommendation}

Return JSON: {{"analysis": ["point1", "point2", "point3"]}}"""

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": OPENAI_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.4,
                    "response_format": {"type": "json_object"},
                },
            )

        if response.status_code != 200:
            return None

        content = response.json()["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        bullets = parsed.get("analysis", [])
        if len(bullets) >= 3:
            return bullets[:3]
    except (KeyError, json.JSONDecodeError, httpx.HTTPError):
        return None

    return None


def _fallback_analysis(
    team1: str,
    team2: str,
    team1_data: dict,
    team2_data: dict,
    expected_goals: dict,
    probabilities: dict,
) -> List[str]:
    stronger_attack = team1 if team1_data["attack"] >= team2_data["attack"] else team2
    stronger_defense = team1 if team1_data["defense"] >= team2_data["defense"] else team2
    favorite = team1 if probabilities["team1_win"] >= probabilities["team2_win"] else team2

    return [
        (
            f"{stronger_attack} carries the stronger attack profile "
            f"(xG {expected_goals[stronger_attack]:.1f} vs "
            f"{expected_goals[team2 if stronger_attack == team1 else team1]:.1f})"
        ),
        (
            f"{stronger_defense} looks more solid defensively "
            f"(rating {max(team1_data['defense'], team2_data['defense'])}/100)"
        ),
        (
            f"Model edge favors {favorite} at "
            f"{max(probabilities['team1_win'], probabilities['team2_win']):.0f}% win probability "
            f"with {probabilities['draw']:.0f}% draw chance"
        ),
    ]
