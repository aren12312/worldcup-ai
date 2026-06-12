from __future__ import annotations

from typing import Any, Dict, List, Optional

import httpx

from backend.app.services.config import get_odds_key, has_football_data
from backend.app.services import api_football, football_data


def api_enabled() -> bool:
    return has_football_data() or api_football.api_enabled()


async def build_team_profile(name: str, fallback: dict) -> dict:
    if has_football_data():
        profile = await football_data.build_team_profile(name, fallback)
        if profile.get("recent_matches"):
            return profile

    if api_football.api_enabled():
        return await api_football.build_team_profile(name, fallback)

    return {**fallback, "recent_matches": [], "form_string": ""}


async def search_team(name: str) -> Optional[dict]:
    return await build_team_profile(name, {"name": name, "attack": 75, "defense": 75, "form": 0.7})


async def enrich_team(name: str, local: dict) -> dict:
    return await build_team_profile(name, local)


async def get_match_context(team1: dict, team2: dict) -> dict:
    if has_football_data() and team1.get("team_id") and team2.get("team_id"):
        ctx = await football_data.get_match_context(team1, team2)
        if ctx.get("has_live_data"):
            return ctx

    if api_football.api_enabled():
        return await api_football.get_match_context(team1, team2)

    return {"head_to_head": [], "has_live_data": False}


async def get_live_matches() -> List[Dict[str, Any]]:
    if has_football_data():
        matches = await football_data.get_live_matches()
        if matches:
            return matches
    return await api_football.get_live_matches()


async def get_upcoming_fixtures(limit: int = 10) -> List[Dict[str, Any]]:
    if has_football_data():
        fixtures = await football_data.get_upcoming_fixtures(limit)
        if fixtures:
            return fixtures
    return await api_football.get_upcoming_fixtures(limit)


async def fetch_market_odds(team1: str, team2: str) -> Optional[dict]:
    """Fetch betting market odds from The Odds API when configured."""
    key = get_odds_key()
    if not key:
        return None

    sports = (
        "soccer_fifa_world_cup",
        "soccer_fifa_world_cup_qualification",
        "soccer_international_friendlies",
    )

    async with httpx.AsyncClient(timeout=15.0) as client:
        for sport in sports:
            response = await client.get(
                f"https://api.the-odds-api.com/v4/sports/{sport}/odds",
                params={
                    "apiKey": key,
                    "regions": "eu,uk",
                    "markets": "h2h",
                    "oddsFormat": "decimal",
                },
            )
            if response.status_code != 200:
                continue

            t1 = team1.lower()
            t2 = team2.lower()
            for event in response.json():
                home = (event.get("home_team") or "").lower()
                away = (event.get("away_team") or "").lower()
                if (t1 in home or home in t1) and (t2 in away or away in t2):
                    bookmakers = event.get("bookmakers", [])
                    if not bookmakers:
                        continue
                    market = bookmakers[0].get("markets", [{}])[0]
                    outcomes = {
                        o["name"]: o.get("price")
                        for o in market.get("outcomes", [])
                    }
                    return {
                        "source": "odds_api",
                        "event": f"{event.get('home_team')} vs {event.get('away_team')}",
                        "commence_time": event.get("commence_time"),
                        "odds": outcomes,
                    }

    return None
