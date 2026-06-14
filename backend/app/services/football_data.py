from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import httpx

from backend.app.data.match_history import get_curated_h2h, get_curated_recent
from backend.app.services.config import get_football_data_key, has_football_data

BASE_URL = "https://api.football-data.org/v4"

COMPETITIONS = ("WC", "CL", "EC")

TEAM_IDS = {
    "brazil": 7598, "france": 7733, "argentina": 7625, "england": 7704,
    "spain": 7600, "germany": 7593, "portugal": 7653, "netherlands": 7687,
    "belgium": 7583, "italy": 7643, "croatia": 7645, "uruguay": 7580,
    "colombia": 7582, "mexico": 7659, "usa": 7588, "japan": 7628,
    "morocco": 7671, "senegal": 7638, "switzerland": 7605, "denmark": 7595,
    "poland": 7591, "australia": 7596, "south korea": 7668, "canada": 7790,
    "israel": 7646, "egypt": 7616, "nigeria": 7663, "turkey": 7607,
}


def _headers() -> dict:
    return {"X-Auth-Token": get_football_data_key()}


async def _get(path: str, params: Optional[dict] = None) -> Optional[dict]:
    if not has_football_data():
        return None
    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.get(f"{BASE_URL}{path}", headers=_headers(), params=params or {})
    if response.status_code != 200:
        return None
    return response.json()


def _resolve_team_id(name: str) -> Optional[int]:
    key = name.strip().lower()
    if key in TEAM_IDS:
        return TEAM_IDS[key]
    for tk, tid in TEAM_IDS.items():
        if tk in key or key in tk:
            return tid
    return None


def _parse_match(item: dict, perspective_id: Optional[int] = None) -> dict:
    home = item.get("homeTeam", {})
    away = item.get("awayTeam", {})
    score = item.get("score", {}).get("fullTime", {})
    hg, ag = score.get("home"), score.get("away")
    comp = item.get("competition", {})

    result = {
        "date": (item.get("utcDate") or "")[:10],
        "competition": comp.get("name", ""),
        "home_team": home.get("name"),
        "away_team": away.get("name"),
        "score": f"{hg}-{ag}",
        "home_goals": hg,
        "away_goals": ag,
        "status": item.get("status"),
    }

    if perspective_id and hg is not None and ag is not None:
        if home.get("id") == perspective_id:
            result.update(team_goals=hg, opponent_goals=ag, opponent=away.get("name"), venue="home")
        elif away.get("id") == perspective_id:
            result.update(team_goals=ag, opponent_goals=hg, opponent=home.get("name"), venue="away")
        if "team_goals" in result:
            tg, og = result["team_goals"], result["opponent_goals"]
            result["outcome"] = "W" if tg > og else "L" if tg < og else "D"

    return result


def _format_curated_recent(team_name: str) -> List[dict]:
    out = []
    for m in get_curated_recent(team_name):
        tg, og = (int(x) for x in m["score"].split("-"))
        out.append({
            **m,
            "team_goals": tg,
            "opponent_goals": og,
            "home_team": team_name,
            "away_team": m["opponent"],
        })
    return out


async def _fetch_matches_date_range(team_id: int, days: int = 500) -> List[dict]:
    date_to = datetime.utcnow().strftime("%Y-%m-%d")
    date_from = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
    data = await _get("/matches", params={
        "dateFrom": date_from, "dateTo": date_to, "status": "FINISHED", "limit": 100,
    })
    if not data:
        return []
    out = []
    for item in data.get("matches", []):
        home = item.get("homeTeam", {})
        away = item.get("awayTeam", {})
        if team_id in (home.get("id"), away.get("id")):
            parsed = _parse_match(item, team_id)
            if parsed.get("team_goals") is not None:
                out.append(parsed)
    out.sort(key=lambda x: x["date"], reverse=True)
    return out


async def _fetch_competition_matches(team_id: int) -> List[dict]:
    collected = []
    for comp in COMPETITIONS:
        data = await _get(f"/competitions/{comp}/matches", params={"status": "FINISHED"})
        if not data:
            continue
        for item in data.get("matches", []):
            home = item.get("homeTeam", {})
            away = item.get("awayTeam", {})
            if team_id in (home.get("id"), away.get("id")):
                parsed = _parse_match(item, team_id)
                if parsed.get("team_goals") is not None:
                    collected.append(parsed)
    collected.sort(key=lambda x: x["date"], reverse=True)
    return collected


async def get_recent_fixtures(team_id: int, team_name: str, last: int = 5) -> List[dict]:
    fixtures = await _fetch_matches_date_range(team_id)
    if not fixtures:
        fixtures = await _fetch_competition_matches(team_id)
    if not fixtures:
        fixtures = _format_curated_recent(team_name)
    return fixtures[:last]


async def get_head_to_head(team1_id: int, team2_id: int, team1_name: str, team2_name: str, last: int = 5) -> List[dict]:
    all_t1 = await _fetch_matches_date_range(team1_id, days=8000)
    h2h = []
    t2_lower = team2_name.lower()
    for m in all_t1:
        opp = (m.get("opponent") or "").lower()
        if t2_lower in opp or opp in t2_lower:
            h2h.append({
                "date": m["date"],
                "home_team": m.get("home_team") or team1_name,
                "away_team": m.get("away_team") or team2_name,
                "score": m["score"],
                "competition": m.get("competition", ""),
            })

    if not h2h:
        h2h = get_curated_h2h(team1_name, team2_name)

    return h2h[:last]


def _form_from_fixtures(fixtures: List[dict]) -> str:
    return "-".join(f.get("outcome", "?") for f in fixtures)


def _ratings_from_fixtures(fixtures: List[dict], fallback: dict, source: str) -> dict:
    if not fixtures:
        return fallback

    scored = [f["team_goals"] for f in fixtures if f.get("team_goals") is not None]
    conceded = [f["opponent_goals"] for f in fixtures if f.get("opponent_goals") is not None]
    if not scored:
        return fallback

    wins = sum(1 for f in fixtures if f.get("outcome") == "W")
    avg_scored = sum(scored) / len(scored)
    avg_conceded = sum(conceded) / len(conceded)
    form = wins / len(fixtures)

    return {
        **fallback,
        "attack": round(min(95, max(50, 55 + avg_scored * 14))),
        "defense": round(min(95, max(50, 55 + (2.2 - avg_conceded) * 16))),
        "form": round(min(0.95, max(0.35, form)), 2),
        "avg_goals_scored": round(avg_scored, 2),
        "avg_goals_conceded": round(avg_conceded, 2),
        "form_string": _form_from_fixtures(fixtures),
        "recent_matches": fixtures,
        "source": source,
    }


async def find_team(name: str) -> Optional[dict]:
    team_id = _resolve_team_id(name)
    if team_id:
        return {"id": team_id, "name": name if name[0].isupper() else name.title()}
    data = await _get("/competitions/WC/teams")
    if data:
        target = name.strip().lower()
        for team in data.get("teams", []):
            tname = team.get("name", "").lower()
            if target in tname or tname in target:
                return {"id": team["id"], "name": team["name"]}
    return None


async def build_team_profile(name: str, fallback: dict) -> dict:
    canonical = fallback.get("name", name)
    team = await find_team(canonical)
    if not team:
        curated = _format_curated_recent(canonical)
        profile = _ratings_from_fixtures(curated, fallback, "curated_database")
        profile["name"] = canonical
        return profile

    fixtures = await get_recent_fixtures(team["id"], team["name"], last=5)
    source = "football_data_live" if fixtures and fixtures[0].get("date", "") > "2023" else "curated_database"
    if source == "curated_database" or not fixtures:
        fixtures = _format_curated_recent(team["name"]) or fixtures

    profile = _ratings_from_fixtures(fixtures, fallback, source)
    profile["team_id"] = team["id"]
    profile["name"] = team["name"]
    return profile


async def get_match_context(team1: dict, team2: dict) -> dict:
    t1_name, t2_name = team1.get("name", ""), team2.get("name", "")
    t1_id, t2_id = team1.get("team_id"), team2.get("team_id")

    h2h = []
    if t1_id and t2_id:
        h2h = await get_head_to_head(t1_id, t2_id, t1_name, t2_name, last=5)
    if not h2h:
        h2h = get_curated_h2h(t1_name, t2_name)[:5]

    has_recent = bool(team1.get("recent_matches") or team2.get("recent_matches"))
    return {"head_to_head": h2h, "has_live_data": bool(h2h or has_recent)}


async def get_live_matches() -> List[Dict[str, Any]]:
    for status in ("IN_PLAY", "LIVE", "PAUSED"):
        data = await _get("/matches", params={"status": status})
        if data and data.get("matches"):
            return [_match_live(m) for m in data["matches"]]
    return []


def _match_live(item: dict) -> dict:
    home = item.get("homeTeam", {})
    away = item.get("awayTeam", {})
    score = item.get("score", {}).get("fullTime", {})
    return {
        "home": home.get("name"), "away": away.get("name"),
        "minute": item.get("minute"), "score": f"{score.get('home')}-{score.get('away')}",
        "status": item.get("status"), "competition": item.get("competition", {}).get("name"),
    }


async def get_upcoming_fixtures(limit: int = 10) -> List[Dict[str, Any]]:
    data = await _get("/competitions/WC/matches", params={"status": "SCHEDULED"})
    if not data:
        return []
    fixtures = []
    for item in data.get("matches", [])[:limit]:
        home = item.get("homeTeam", {})
        away = item.get("awayTeam", {})
        fixtures.append({
            "home": home.get("name"), "away": away.get("name"),
            "date": item.get("utcDate"), "venue": item.get("venue"),
            "competition": item.get("competition", {}).get("name"),
        })
    return fixtures
