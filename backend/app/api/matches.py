from fastapi import APIRouter

from backend.app.services import api_football
from backend.app.services.team_resolver import list_teams

router = APIRouter()


@router.get("/live-matches")
async def live_matches():
    matches = await api_football.get_live_matches()
    return {"matches": matches, "source": "api" if matches else "empty"}


@router.get("/upcoming-matches")
async def upcoming_matches():
    fixtures = await api_football.get_upcoming_fixtures()
    return {"fixtures": fixtures}


@router.get("/teams")
async def teams():
    return {"teams": await list_teams()}
