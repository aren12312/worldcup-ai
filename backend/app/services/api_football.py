import os
import httpx

API_KEY = os.getenv("API_FOOTBALL_KEY")

BASE_URL = "https://v3.football.api-sports.io"

async def get_team_statistics(team_id: int):
    headers = {"x-apisports-key": API_KEY}

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/teams/statistics",
            headers=headers,
            params={"team": team_id}
        )

    return response.json()