from __future__ import annotations

from typing import Any, Dict, List, Optional

import httpx

from backend.app.services.config import get_football_data_key, has_football_data

BASE_URL = "https://api.football-data.org/v4"

# football-data.org national team IDs
TEAM_IDS = {
    "brazil": 7598,
    "france": 7733,
    "argentina": 7625,
    "england": 7704,
    "spain": 7600,
    "germany": 7593,
    "portugal": 7653,
    "netherlands": 7687,
    "belgium": 7583,
    "italy": 7643,
    "croatia": 7645,
    "uruguay": 7580,
    "colombia": 7582,
    "mexico": 7659,
    "usa": 7588,
    "japan": 7628,
    "morocco": 7671,
    "senegal": 7638,
    "switzerland": 7605,
    "denmark": 7595,
    "poland": 7591,
    "australia": 7596,
    "south korea": 7668,
    "canada": 7790,
    "israel": 7646,
    "egypt": 7616,
    "nigeria": 7663,
    "turkey": 7607,
    "austria": 7594,
    "serbia": 7633,
    "ukraine": 7606,
    "ecuador": 7639,
    "iran": 7637,
    "saudi arabia": 7669,
    "qatar": 7654,
    "costa rica": 7648,
    "wales": 7670,
    "scotland": 7632,
    "ghana": 7615,
    "cameroon": 7644,
    "tunisia": 7608,
    "chile": 7647,
    "peru": 7590,
    "paraguay": 7592,
    "venezuela": 7610,
    "ivory coast": 7631,
}


def _headers() -> dict:
    return {"X-Auth-Token": get_football_data_key()}


async def _get(path: str, params: Optional[dict] = None) -> Optional[dict]:
    if not has_football_data():
        return None

    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.get(
            f"{BASE_URL}{path}",
            headers=_headers(),
            params=params or {},
        )

    if response.status_code != 200:
        return None

    return response.json()


def _resolve_team_id(name: str) -> Optional[int]:
    key = name.strip().lower()
    if key in TEAM_IDS:
        return TEAM_IDS[key]
    for team_key, team_id in TEAM_IDS.items():
        if team_key in key or key in team_key:
            return team_id
    return None


def _parse_match(item: dict, perspective_id: Optional[int] = None) -> dict:
    home = item.get("homeTeam", {})
    away = item.get("awayTeam", {})
    score = item.get("score", {}).get("fullTime", {})
    home_goals = score.get("home")
    away_goals = score.get("away")
    competition = item.get("competition", {})

    result = {
        "date": (item.get("utcDate") or "")[:10],
        "competition": competition.get("name", ""),
        "home_team": home.get("name"),
        "away_team": away.get("name"),
        "score": f"{home_goals}-{away_goals}",
        "home_goals": home_goals,
        "away_goals": away_goals,
        "status": item.get("status"),
    }

    if perspective_id and home_goals is not None and away_goals is not None:
        if home.get("id") == perspective_id:
            result["team_goals"] = home_goals
            result["opponent_goals"] = away_goals
            result["opponent"] = away.get("name")
            result["venue"] = "home"
        elif away.get("id") == perspective_id:
            result["team_goals"] = away_goals
            result["opponent_goals"] = home_goals
            result["opponent"] = home.get("name")
            result["venue"] = "away"

        if "team_goals" in result:
            if result["team_goals"] > result["opponent_goals"]:
                result["outcome"] = "W"
            elif result["team_goals"] < result["opponent_goals"]:
                result["outcome"] = "L"
            else:
                result["outcome"] = "D"

    return result


async def find_team(name: str) -> Optional[dict]:
    team_id = _resolve_team_id(name)
    if not team_id:
        data = await _get("/competitions/WC/teams")
        if data:
            target = name.strip().lower()
            for team in data.get("teams", []):
                tname = team.get("name", "").lower()
                if target in tname or tname in target:
                    return {"id": team["id"], "name": team["name"]}
        return None

    data = await _get(f"/teams/{team_id}")
    if data:
        return {"id": data["id"], "name": data.get("name", name)}
    return {"id": team_id, "name": name}


async def get_recent_fixtures(team_id: int, last: int = 5) -> List[dict]:
    data = await _get(
        f"/teams/{team_id}/matches",
        params={"status": "FINISHED", "limit": last},
    )
    if not data:
        return []

    fixtures = []
    for item in data.get("matches", []):
        parsed = _parse_match(item, team_id)
        if parsed.get("team_goals") is None:
            continue
        fixtures.append(parsed)

    return fixtures[:last]


async def get_head_to_head(team1_id: int, team2_id: int, last: int = 5) -> List[dict]:
    data = await _get(
        f"/teams/{team1_id}/matches",
        params={"status": "FINISHED", "limit": 20},
    )
    if not data:
        return []

    h2h = []
    for item in data.get("matches", []):
        home = item.get("homeTeam", {})
        away = item.get("awayTeam", {})
        ids = {home.get("id"), away.get("id")}
        if team2_id in ids:
            h2h.append(_parse_match(item))

    return h2h[:last]


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
        "source": "football_data_live",
    }


async def build_team_profile(name: str, fallback: dict) -> dict:
    if not has_football_data():
        return {**fallback, "recent_matches": [], "form_string": ""}

    team = await find_team(fallback.get("name", name))
    if not team:
        return {**fallback, "recent_matches": [], "form_string": ""}

    fixtures = await get_recent_fixtures(team["id"], last=5)
    profile = _ratings_from_fixtures(fixtures, fallback)
    profile["team_id"] = team["id"]
    profile["name"] = team["name"]
    return profile


async def get_match_context(team1: dict, team2: dict) -> dict:
    if not has_football_data() or not team1.get("team_id") or not team2.get("team_id"):
        return {"head_to_head": [], "has_live_data": False}

    h2h = await get_head_to_head(team1["team_id"], team2["team_id"], last=5)
    return {
        "head_to_head": h2h,
        "has_live_data": bool(h2h or team1.get("recent_matches")),
    }


async def get_live_matches() -> List[Dict[str, Any]]:
    data = await _get("/matches", params={"status": "IN_PLAY"})
    if not data:
        data = await _get("/matches", params={"status": "LIVE"})
    if not data:
        return []

    matches = []
    for item in data.get("matches", []):
        home = item.get("homeTeam", {})
        away = item.get("awayTeam", {})
        score = item.get("score", {})
        minute = item.get("minute")
        comp = item.get("competition", {})
        matches.append(
            {
                "home": home.get("name"),
                "away": away.get("name"),
                "minute": minute,
                "score": f"{score.get('fullTime', {}).get('home')}-{score.get('fullTime', {}).get('away')}",
                "status": item.get("status"),
                "competition": comp.get("name"),
            }
        )

    return matches


async def get_upcoming_fixtures(limit: int = 10) -> List[Dict[str, Any]]:
    data = await _get("/competitions/WC/matches", params={"status": "SCHEDULED"})
    if not data:
        data = await _get("/competitions/WC/matches")
    if not data:
        return []

    fixtures = []
    for item in data.get("matches", [])[:limit]:
        home = item.get("homeTeam", {})
        away = item.get("awayTeam", {})
        fixtures.append(
            {
                "home": home.get("name"),
                "away": away.get("name"),
                "date": item.get("utcDate"),
                "venue": item.get("venue"),
                "competition": item.get("competition", {}).get("name"),
            }
        )

    return fixtures
