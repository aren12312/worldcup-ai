from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import httpx

API_KEY = os.getenv("API_FOOTBALL_KEY")
BASE_URL = "https://v3.football.api-sports.io"
HEADERS = {"x-apisports-key": API_KEY} if API_KEY else {}

INTERNATIONAL_LEAGUES = (1, 10, 29, 30)  # World Cup, friendlies, qualifiers


def api_enabled() -> bool:
    return bool(API_KEY)


async def _get(path: str, params: Optional[dict] = None) -> Optional[dict]:
    if not api_enabled():
        return None

    async with httpx.AsyncClient(timeout=20.0) as client:
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


def _parse_fixture(item: dict, perspective_team_id: Optional[int] = None) -> dict:
    fixture = item.get("fixture", {})
    teams = item.get("teams", {})
    goals = item.get("goals", {})
    league = item.get("league", {})

    home = teams.get("home", {})
    away = teams.get("away", {})
    home_goals = goals.get("home")
    away_goals = goals.get("away")

    result = {
        "date": fixture.get("date", "")[:10],
        "competition": league.get("name", ""),
        "home_team": home.get("name"),
        "away_team": away.get("name"),
        "score": f"{home_goals}-{away_goals}",
        "home_goals": home_goals,
        "away_goals": away_goals,
        "status": fixture.get("status", {}).get("short"),
    }

    if perspective_team_id:
        if home.get("id") == perspective_team_id:
            result["team_goals"] = home_goals
            result["opponent_goals"] = away_goals
            result["opponent"] = away.get("name")
            result["venue"] = "home"
        elif away.get("id") == perspective_team_id:
            result["team_goals"] = away_goals
            result["opponent_goals"] = home_goals
            result["opponent"] = home.get("name")
            result["venue"] = "away"

        if result.get("team_goals") is not None and result.get("opponent_goals") is not None:
            if result["team_goals"] > result["opponent_goals"]:
                result["outcome"] = "W"
            elif result["team_goals"] < result["opponent_goals"]:
                result["outcome"] = "L"
            else:
                result["outcome"] = "D"

    return result


async def find_national_team(name: str) -> Optional[dict]:
    data = await _get("/teams", params={"search": name})
    if not data:
        return None

    target = name.strip().lower()
    for item in data.get("response", []):
        team = item.get("team", {})
        if not team.get("national"):
            continue
        team_name = team.get("name", "").lower()
        if target in team_name or team_name in target:
            return {"id": team["id"], "name": team["name"], "country": team.get("country")}

    for item in data.get("response", []):
        team = item.get("team", {})
        if team.get("national"):
            return {"id": team["id"], "name": team["name"], "country": team.get("country")}

    return None


async def get_recent_fixtures(team_id: int, last: int = 5) -> List[dict]:
    data = await _get(
        "/fixtures",
        params={"team": team_id, "last": last, "status": "FT"},
    )
    if not data:
        return []

    fixtures = []
    for item in data.get("response", []):
        parsed = _parse_fixture(item, team_id)
        if parsed.get("team_goals") is None:
            continue
        fixtures.append(parsed)

    return fixtures[:last]


async def get_head_to_head(team1_id: int, team2_id: int, last: int = 5) -> List[dict]:
    data = await _get(
        "/fixtures/headtohead",
        params={"h2h": f"{team1_id}-{team2_id}", "last": last, "status": "FT"},
    )
    if not data:
        return []

    matches = []
    for item in data.get("response", []):
        matches.append(_parse_fixture(item))

    return matches[:last]


def _form_from_fixtures(fixtures: List[dict]) -> str:
    if not fixtures:
        return ""
    return "-".join(f.get("outcome", "?") for f in fixtures)


def _ratings_from_fixtures(fixtures: List[dict], fallback: dict) -> dict:
    if not fixtures:
        return fallback

    scored = [f["team_goals"] for f in fixtures if f.get("team_goals") is not None]
    conceded = [f["opponent_goals"] for f in fixtures if f.get("opponent_goals") is not None]
    wins = sum(1 for f in fixtures if f.get("outcome") == "W")

    avg_scored = sum(scored) / len(scored)
    avg_conceded = sum(conceded) / len(conceded)
    form = wins / len(fixtures)

    attack = min(95, max(50, 55 + avg_scored * 14))
    defense = min(95, max(50, 55 + (2.2 - avg_conceded) * 16))

    return {
        **fallback,
        "attack": round(attack),
        "defense": round(defense),
        "form": round(min(0.95, max(0.35, form)), 2),
        "avg_goals_scored": round(avg_scored, 2),
        "avg_goals_conceded": round(avg_conceded, 2),
        "form_string": _form_from_fixtures(fixtures),
        "recent_matches": fixtures,
        "source": "api_football_live",
    }


async def build_team_profile(name: str, fallback: dict) -> dict:
    if not api_enabled():
        return {**fallback, "recent_matches": [], "form_string": ""}

    team = await find_national_team(fallback.get("name", name))
    if not team:
        return {**fallback, "recent_matches": [], "form_string": ""}

    fixtures = await get_recent_fixtures(team["id"], last=5)
    profile = _ratings_from_fixtures(fixtures, fallback)
    profile["team_id"] = team["id"]
    profile["name"] = team["name"]
    return profile


async def get_match_context(team1: dict, team2: dict) -> dict:
    if not api_enabled() or not team1.get("team_id") or not team2.get("team_id"):
        return {"head_to_head": [], "has_live_data": False}

    h2h = await get_head_to_head(team1["team_id"], team2["team_id"], last=5)
    return {"head_to_head": h2h, "has_live_data": bool(h2h or team1.get("recent_matches"))}


async def get_live_matches() -> List[Dict[str, Any]]:
    data = await _get("/fixtures", params={"live": "all"})
    if not data:
        return []

    matches = []
    for item in data.get("response", []):
        fixture = item.get("fixture", {})
        teams = item.get("teams", {})
        goals = item.get("goals", {})
        league = item.get("league", {})
        matches.append(
            {
                "home": teams.get("home", {}).get("name"),
                "away": teams.get("away", {}).get("name"),
                "minute": fixture.get("status", {}).get("elapsed"),
                "score": f"{goals.get('home')}-{goals.get('away')}",
                "status": fixture.get("status", {}).get("long"),
                "competition": league.get("name"),
            }
        )

    return matches


async def get_upcoming_fixtures(limit: int = 10) -> List[Dict[str, Any]]:
    for league in INTERNATIONAL_LEAGUES:
        for season in (2026, 2025, 2024):
            data = await _get(
                "/fixtures",
                params={"league": league, "season": season, "next": limit},
            )
            if data and data.get("response"):
                fixtures = []
                for item in data.get("response", []):
                    teams = item.get("teams", {})
                    fixture = item.get("fixture", {})
                    league_info = item.get("league", {})
                    fixtures.append(
                        {
                            "home": teams.get("home", {}).get("name"),
                            "away": teams.get("away", {}).get("name"),
                            "date": fixture.get("date"),
                            "venue": fixture.get("venue", {}).get("name"),
                            "competition": league_info.get("name"),
                        }
                    )
                return fixtures[:limit]

    return []


# Backward-compatible helpers used by team_resolver
async def search_team(name: str) -> Optional[dict]:
    fallback = {"name": name, "attack": 75, "defense": 75, "form": 0.7}
    team = await find_national_team(name)
    if not team:
        return None
    fixtures = await get_recent_fixtures(team["id"], last=5)
    profile = _ratings_from_fixtures(fixtures, fallback)
    profile["team_id"] = team["id"]
    profile["name"] = team["name"]
    return profile


async def enrich_team(name: str, local: dict) -> dict:
    return await build_team_profile(name, local)
