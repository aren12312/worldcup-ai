import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.matches import router as matches_router
from backend.app.api.predictions import router as prediction_router
from backend.app.api.telegram import process_update, setup_webhook, shutdown_webhook
from backend.app.services.config import (
    get_openai_key,
    get_odds_key,
    get_telegram_token,
    get_weather_key,
    has_football_data,
    has_live_data_api,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "")


@asynccontextmanager
async def lifespan(app: FastAPI):
    if PUBLIC_BASE_URL and get_telegram_token():
        try:
            await setup_webhook(PUBLIC_BASE_URL)
        except Exception:
            logger.exception("Failed to setup Telegram webhook")
    yield
    await shutdown_webhook()


app = FastAPI(
    title="Football Analyst AI",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "service": "Football Analyst AI",
        "status": "running",
        "lang": "he",
        "telegram": bool(get_telegram_token()),
        "football_data": has_football_data(),
        "live_data": has_live_data_api(),
        "odds_api": bool(get_odds_key()),
        "weather_api": bool(get_weather_key()),
        "openai": bool(get_openai_key()),
    }


@app.get("/health")
async def health():
    return {"ok": True}


@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    await process_update(data)
    return {"ok": True}


app.include_router(prediction_router)
app.include_router(matches_router)
