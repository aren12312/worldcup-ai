from __future__ import annotations

from typing import List, Optional

from backend.app.data.hebrew_teams import normalize_team_input
from backend.app.data.teams import TEAMS
from backend.app.services import api_football
from backend.app.services.i18n import t


def _normalize(name: str) -> str:
    return normalize_team_input(name).strip().lower()


def resolve_from_database(name: str) -> Optional[dict]:
    key = _normalize(name)
    if key in TEAMS:
        return {**TEAMS[key], "source": "database"}
    for team_key, team in TEAMS.items():
        if team["name"].lower() == key or team_key == key:
            return {**team, "source": "database"}
    return None


async def resolve_team(name: str) -> dict:
    canonical = normalize_team_input(name)
    local = resolve_from_database(canonical)
    if local:
        return await api_football.build_team_profile(local["name"], local)

    api_team = await api_football.search_team(canonical)
    if api_team:
        return api_team

    raise ValueError(t("unknown_team", "he", name=name))


async def list_teams(lang: str = "he") -> List[str]:
    from backend.app.data.hebrew_teams import display_team_name

    names = sorted({team["name"] for team in TEAMS.values()})
    if lang == "he":
        return [display_team_name(name, "he") for name in names]
    return names
