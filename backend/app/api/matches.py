from fastapi import APIRouter
from app.services.api_football import get_live_matches

router = APIRouter()

@router.get("/live-matches")
async def live_matches():

    return await get_live_matches()