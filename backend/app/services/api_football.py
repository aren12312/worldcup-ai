from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import httpx

API_KEY = os.getenv("API_FOOTBALL_KEY")
BASE_URL = "https://v3.football.api-sports.io"
WORLD_CUP_LEAGUE = 1
CURRENT_SEASON = 2026

HEADERS = {"x-apisports-key": API_KEY} if API_KEY else {}


def _api_enabled() -> bool:
    return bool(API_KEY)


async def _get(path: str, params: Optional[dict] = None) -> Optional[dict]:
    if not _api_enabled():
        return None

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(
            f"{BASE_URL}{path}",
            headers=HEADERS,
            params=params or {},
        )

    if response.status_code != 200:
        return None

    data = response.json()
    if data.get("errors"):
        return None

    return data


def _parse_team_stats(raw: dict, fallback: dict) -> dict:
    stats = raw.get("response", {})
    if not stats:
        return fallback

    goals = stats.get("goals", {})
    fixtures = stats.get("fixtures", {})
    played = fixtures.get("played", {}).get("total") or 0

    goals_for = goals.get("for", {}).get("total", {}).get("total") or 0
    goals_against = goals.get("against", {}).get("total", {}).get("total") or 0

    wins = fixtures.get("wins", {}).get("total") or 0
    form_score = wins / played if played else fallback.get("form", 0.7)

    attack = min(95, max(55, 60 + (goals_for / max(played, 1)) * 12))
    defense = min(95, max(55, 60 + (2.0 - goals_against / max(played, 1)) * 15))

    return {
        "name": fallback["name"],
        "attack": round(attack),
        "defense": round(defense),
        "form": round(min(0.95, max(0.45, form_score)), 2),
        "source": "api_football",
        "matches_played": played,
        "goals_for": goals_for,
        "goals_against": goals_against,
    }


async def search_team(name: str) -> Optional[dict]:
    data = await _get("/teams", params={"search": name})
    if not data:
        return None

    for item in data.get("response", []):
        team = item.get("team", {})
        if team.get("national"):
            team_id = team["id"]
            stats_raw = await get_team_statistics(team_id)
            base = {
                "name": team["name"],
                "attack": 75,
                "defense": 75,
                "form": 0.7,
            }
            return _parse_team_stats(stats_raw or {}, base)

    return None


async def enrich_team(name: str, local: dict) -> dict:
    if not _api_enabled():
        return local

    data = await _get("/teams", params={"search": local["name"]})
    if not data:
        return local

    for item in data.get("response", []):
        team = item.get("team", {})
        if team.get("name", "").lower() == local["name"].lower():
            stats_raw = await get_team_statistics(team["id"])
            return _parse_team_stats(stats_raw or {}, local)

    return local


async def get_team_statistics(team_id: int) -> Optional[dict]:
    for season in (CURRENT_SEASON, 2024, 2022):
        data = await _get(
            "/teams/statistics",
            params={
                "team": team_id,
                "league": WORLD_CUP_LEAGUE,
                "season": season,
            },
        )
        if data and data.get("response"):
            return data

    return await _get(
        "/teams/statistics",
        params={
            "team": team_id,
            "league": 10,
            "season": 2024,
        },
    )


async def get_live_matches() -> List[Dict[str, Any]]:
    data = await _get("/fixtures", params={"live": "all"})
    if not data:
        return []

    matches = []
    for item in data.get("response", []):
        fixture = item.get("fixture", {})
        teams = item.get("teams", {})
        goals = item.get("goals", {})
        matches.append(
            {
                "home": teams.get("home", {}).get("name"),
                "away": teams.get("away", {}).get("name"),
                "minute": fixture.get("status", {}).get("elapsed"),
                "score": f"{goals.get('home')}-{goals.get('away')}",
                "status": fixture.get("status", {}).get("long"),
            }
        )

    return matches


async def get_upcoming_fixtures(limit: int = 10) -> List[Dict[str, Any]]:
    data = await _get(
        "/fixtures",
        params={"league": WORLD_CUP_LEAGUE, "season": CURRENT_SEASON, "next": limit},
    )
    if not data:
        return []

    fixtures = []
    for item in data.get("response", []):
        teams = item.get("teams", {})
        fixture = item.get("fixture", {})
        fixtures.append(
            {
                "home": teams.get("home", {}).get("name"),
                "away": teams.get("away", {}).get("name"),
                "date": fixture.get("date"),
                "venue": fixture.get("venue", {}).get("name"),
            }
        )

    return fixtures
