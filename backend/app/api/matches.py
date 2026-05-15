from fastapi import APIRouter

router = APIRouter(prefix="/matches", tags=["matches"])

@router.get("/upcoming")
async def upcoming_matches():
    return {
        "matches": [
            {"home": "Brazil", "away": "France"},
            {"home": "Argentina", "away": "Germany"}
        ]
    }