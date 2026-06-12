from fastapi import APIRouter, Query

from backend.app.services import api_football
from backend.app.services.team_resolver import list_teams

router = APIRouter()


@router.get("/live-matches")
async def live_matches():
    matches = await api_football.get_live_matches()
    return {
        "matches": matches,
        "source": "api" if matches else "empty",
        "api_configured": api_football.api_enabled(),
    }


@router.get("/upcoming-matches")
async def upcoming_matches():
    fixtures = await api_football.get_upcoming_fixtures()
    return {"fixtures": fixtures, "api_configured": api_football.api_enabled()}


@router.get("/teams")
async def teams(lang: str = Query(default="he", pattern="^(he|en)$")):
    return {"teams": await list_teams(lang)}
