import logging
import os
from contextlib import asynccontextmanager

from fastapi import BackgroundTasks, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.matches import router as matches_router
from backend.app.api.predictions import router as prediction_router
from backend.app.api.telegram import (
    get_webhook_status,
    process_update,
    setup_webhook,
    shutdown_webhook,
)
from backend.app.services.config import (
    get_bot_username,
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
    if get_telegram_token() and PUBLIC_BASE_URL:
        try:
            result = await setup_webhook(PUBLIC_BASE_URL)
            logger.info("Startup webhook setup: %s", result)
        except Exception:
            logger.exception("Failed to setup Telegram webhook on startup")
    yield
    await shutdown_webhook()


app = FastAPI(title="Football Analyst AI", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    webhook = await get_webhook_status()
    return {
        "service": "Football Analyst AI",
        "status": "running",
        "lang": "he",
        "bot": f"@{get_bot_username()}",
        "telegram": bool(get_telegram_token()),
        "telegram_webhook": webhook,
        "football_data": has_football_data(),
        "live_data": has_live_data_api(),
        "odds_api": bool(get_odds_key()),
        "weather_api": bool(get_weather_key()),
        "openai": bool(get_openai_key()),
    }


@app.get("/health")
async def health():
    return {"ok": True}


@app.get("/telegram/status")
async def telegram_status():
    return await get_webhook_status()


@app.post("/telegram/setup")
async def telegram_setup():
    """Force webhook registration — call after deploy."""
    url = PUBLIC_BASE_URL or os.getenv("PUBLIC_BASE_URL", "")
    if not url:
        return {"ok": False, "error": "PUBLIC_BASE_URL not set"}
    return await setup_webhook(url)


@app.post("/telegram/webhook")
async def telegram_webhook(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    background_tasks.add_task(process_update, data)
    return {"ok": True}


app.include_router(prediction_router)
app.include_router(matches_router)
