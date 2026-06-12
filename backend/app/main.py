import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.matches import router as matches_router
from backend.app.api.predictions import router as prediction_router
from backend.app.api.telegram import process_update, setup_webhook, shutdown_webhook

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "")


@asynccontextmanager
async def lifespan(app: FastAPI):
    if PUBLIC_BASE_URL and os.getenv("TELEGRAM_TOKEN"):
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
        "telegram": bool(os.getenv("TELEGRAM_TOKEN")),
        "api_football": bool(os.getenv("API_FOOTBALL_KEY")),
        "openai": bool(os.getenv("OPENAI_API_KEY")),
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
