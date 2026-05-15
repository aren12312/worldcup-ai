from fastapi import APIRouter

router = APIRouter()

@router.get("/live-matches")

async def live_matches():

    return {
        "matches": [
            {
                "home": "Brazil",
                "away": "France",
                "minute": 67,
                "score": "2-1"
            }
        ]
    }