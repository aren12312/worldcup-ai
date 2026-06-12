from __future__ import annotations

import os


def get_telegram_token() -> str:
    token = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("TELEGRAM_TOKEN") or ""
    if token and ":" not in token:
        bot_id = os.getenv("TELEGRAM_BOT_ID", "")
        if bot_id:
            return f"{bot_id}:{token}"
    return token


def get_bot_username() -> str:
    name = os.getenv("TELEGRAM_BOT_USERNAME", "WorldCupApi")
    return name.lstrip("@")


def get_telegram_chat_id() -> str:
    return os.getenv("TELEGRAM_CHAT_ID") or os.getenv("CHAT_ID") or ""


def get_football_data_key() -> str:
    return os.getenv("FOOTBALL_DATA_API_KEY") or ""


def get_api_football_key() -> str:
    return os.getenv("API_FOOTBALL_KEY") or ""


def get_openai_key() -> str:
    return os.getenv("OPENAI_API_KEY") or ""


def get_odds_key() -> str:
    return os.getenv("ODDS_API_KEY") or ""


def get_weather_key() -> str:
    return os.getenv("WEATHER_API_KEY") or ""


def has_football_data() -> bool:
    return bool(get_football_data_key())


def has_api_football() -> bool:
    return bool(get_api_football_key())


def has_live_data_api() -> bool:
    return has_football_data() or has_api_football()


def has_telegram() -> bool:
    return bool(get_telegram_token())
