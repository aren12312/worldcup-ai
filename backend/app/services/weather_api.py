from __future__ import annotations

from typing import Optional

import httpx

from backend.app.services.config import get_weather_key

# Default host cities for major nations (World Cup context)
TEAM_CITIES = {
    "Brazil": "Brasilia,BR",
    "France": "Paris,FR",
    "Argentina": "Buenos Aires,AR",
    "England": "London,GB",
    "Spain": "Madrid,ES",
    "Germany": "Berlin,DE",
    "Portugal": "Lisbon,PT",
    "Netherlands": "Amsterdam,NL",
    "Belgium": "Brussels,BE",
    "Italy": "Rome,IT",
    "Mexico": "Mexico City,MX",
    "USA": "New York,US",
    "Japan": "Tokyo,JP",
    "Morocco": "Rabat,MA",
    "Israel": "Tel Aviv,IL",
}


async def fetch_match_weather(team1: str, team2: str) -> Optional[dict]:
    key = get_weather_key()
    if not key:
        return None

    city = TEAM_CITIES.get(team1) or TEAM_CITIES.get(team2)
    if not city:
        return None

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={"q": city, "appid": key, "units": "metric", "lang": "he"},
        )

    if response.status_code != 200:
        return None

    data = response.json()
    weather = data.get("weather", [{}])[0]
    main = data.get("main", {})
    wind = data.get("wind", {})

    return {
        "city": city.split(",")[0],
        "description": weather.get("description"),
        "temp_c": main.get("temp"),
        "humidity": main.get("humidity"),
        "wind_kmh": round((wind.get("speed") or 0) * 3.6, 1),
        "impact_he": _weather_impact_he(weather.get("description", ""), wind.get("speed", 0)),
    }


def _weather_impact_he(description: str, wind_speed: float) -> str:
    desc = (description or "").lower()
    if "rain" in desc or "גשם" in desc:
        return "גשם צפוי — עלול להאט את קצב המשחק ולהפחית שערים"
    if wind_speed > 8:
        return "רוח חזקה — עלולה להשפיע על מסירות ארוכות ועל set pieces"
    if "clear" in desc or "בהיר" in desc:
        return "תנאי מזג אוויר טובים — לא צפוי השפעה משמעותית"
    return "תנאי מזג אוויר רגילים"
