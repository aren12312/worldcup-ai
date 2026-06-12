from fastapi import APIRouter, Query

from backend.app.services import match_data
from backend.app.services.config import has_live_data_api
from backend.app.services.team_resolver import list_teams

router = APIRouter()


@router.get("/live-matches")
async def live_matches():
    matches = await match_data.get_live_matches()
    return {
        "matches": matches,
        "source": "api" if matches else "empty",
        "api_configured": has_live_data_api(),
    }


@router.get("/upcoming-matches")
async def upcoming_matches():
    fixtures = await match_data.get_upcoming_fixtures()
    return {"fixtures": fixtures, "api_configured": has_live_data_api()}


@router.get("/teams")
async def teams(lang: str = Query(default="he", pattern="^(he|en)$")):
    return {"teams": await list_teams(lang)}
