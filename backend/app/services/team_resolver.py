from __future__ import annotations

from typing import List, Optional

from backend.app.data.teams import TEAMS
from backend.app.services import api_football


def _normalize(name: str) -> str:
    return name.strip().lower()


def resolve_from_database(name: str) -> Optional[dict]:
    key = _normalize(name)
    if key in TEAMS:
        return {**TEAMS[key], "source": "database"}
    for team_key, team in TEAMS.items():
        if team["name"].lower() == key or team_key == key:
            return {**team, "source": "database"}
    return None


async def resolve_team(name: str) -> dict:
    """Resolve a team name to ratings, preferring live API data when available."""
    local = resolve_from_database(name)
    if local:
        enriched = await api_football.enrich_team(name, local)
        return enriched

    api_team = await api_football.search_team(name)
    if api_team:
        return api_team

    raise ValueError(f"Unknown team: {name}. Try a major national team like Brazil or France.")


async def list_teams() -> List[str]:
    names = sorted({team["name"] for team in TEAMS.values()})
    return names
