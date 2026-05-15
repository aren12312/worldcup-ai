import os
import httpx

API_KEY = os.getenv("API_FOOTBALL_KEY")

BASE_URL = "https://v3.football.api-sports.io"

HEADERS = {
    "x-apisports-key": API_KEY
}

async def get_live_matches():

    async with httpx.AsyncClient() as client:

        response = await client.get(
            f"{BASE_URL}/fixtures",
            headers=HEADERS,
            params={"live": "all"}
        )

    return response.json()

async def get_team_statistics(team_id):

    async with httpx.AsyncClient() as client:

        response = await client.get(
            f"{BASE_URL}/teams/statistics",
            headers=HEADERS,
            params={
                "team": team_id,
                "league": 39,
                "season": 2025
            }
        )

    return response.json()