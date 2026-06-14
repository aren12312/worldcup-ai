from __future__ import annotations

import asyncio
import logging
import os
from typing import Optional

import httpx
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from backend.app.services.config import get_bot_username, get_telegram_chat_id, get_telegram_token

logger = logging.getLogger(__name__)

API_URL = os.getenv("PUBLIC_BASE_URL") or os.getenv("API_URL", "http://localhost:8080")
LANG = "he"

application: Optional[Application] = None
_init_lock = asyncio.Lock()


def _get_token() -> str:
    return get_telegram_token()


def _parse_match(text: str):
    normalized = (
        text.replace("נגד", " vs ")
        .replace(" מול ", " vs ")
        .replace("VS", "vs")
    )
    lowered = normalized.lower()
    if " vs " in lowered:
        parts = lowered.split(" vs ", 1)
    elif "vs" in lowered:
        idx = lowered.index("vs")
        parts = [lowered[:idx], lowered[idx + 2 :]]
    else:
        return None

    team1 = parts[0].replace("/predict", "").replace("/analyze", "").replace("/start", "").strip()
    team2 = parts[1].strip()
    if not team1 or not team2:
        return None
    return team1, team2


async def _error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.exception("Telegram handler error: %s", context.error)
    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text(
            "❌ שגיאה בעיבוד הבקשה. נסה שוב או שלח /start"
        )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = get_bot_username()
    await update.message.reply_text(
        f"⚽ @{bot} — אנליסט משחקי מונדיאל\n\n"
        "שלח משחק בעברית:\n"
        "🇧🇷 ברזיל נגד צרפת\n\n"
        "פקודות:\n"
        "/predict ברזיל נגד צרפת\n"
        "/teams — רשימת קבוצות\n"
        "/live — משחקים live"
    )


async def list_teams_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(f"{API_URL}/teams", params={"lang": LANG})
        response.raise_for_status()
        teams = response.json()["teams"]
        preview = ", ".join(teams[:12])
        await update.message.reply_text(f"קבוצות נתמכות ({len(teams)}):\n{preview}\n...")
    except httpx.HTTPError as exc:
        logger.exception("teams command failed")
        await update.message.reply_text(f"❌ שגיאת API: {exc}")


async def live_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(f"{API_URL}/live-matches")
        response.raise_for_status()
        data = response.json()
        matches = data.get("matches", [])
        if not matches:
            await update.message.reply_text("אין משחקים live כרגע.")
            return
        lines = ["🔴 משחקים LIVE:\n"]
        for m in matches[:8]:
            lines.append(
                f"{m.get('home')} {m.get('score')} {m.get('away')} "
                f"({m.get('minute', '?')}' — {m.get('competition', '')})"
            )
        await update.message.reply_text("\n".join(lines))
    except httpx.HTTPError:
        await update.message.reply_text("❌ שגיאה בשליפת משחקים live")


async def analyze_match(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    text = update.message.text or ""
    parsed = _parse_match(text)

    if not parsed:
        await update.message.reply_text("שלח משחק:\nברזיל נגד צרפת")
        return

    team1, team2 = parsed
    await update.message.reply_text(f"🔍 מנתח {team1} נגד {team2}...")

    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.get(
                f"{API_URL}/predict",
                params={"team1": team1, "team2": team2, "lang": LANG},
            )
        response.raise_for_status()
        p = response.json()
    except httpx.HTTPStatusError as exc:
        detail = "שגיאה לא ידועה"
        try:
            detail = exc.response.json().get("detail", detail)
        except Exception:
            pass
        await update.message.reply_text(f"❌ {detail}")
        return
    except httpx.HTTPError:
        await update.message.reply_text(f"❌ לא הצלחתי להגיע ל-API ({API_URL})")
        return

    labels = p.get("labels", {})
    t1 = labels.get("team1", team1)
    t2 = labels.get("team2", team2)
    probs = p["probabilities"]
    xg = p["expected_goals"]
    xg_vals = list(xg.values())
    xg_keys = list(xg.keys())

    lines = [
        f"⚽ {p['match']}",
        f"🎯 ביטחון: {p.get('confidence', '?')}/100",
        "",
        "📊 הסתברויות",
        f"{t1}: {probs['team1_win']}%",
        f"תיקו: {probs['draw']}%",
        f"{t2}: {probs['team2_win']}%",
        "",
        "⚽ xG",
        f"{t1}: {xg.get(t1, xg_vals[0])} | {t2}: {xg.get(t2, xg_vals[1] if len(xg_vals) > 1 else xg_vals[0])}",
        "",
        f"📋 {p.get('summary', '')}",
        "",
        "🔍 ניתוח",
    ]
    for point in p.get("analysis", [])[:5]:
        lines.append(f"• {point}")

    lines.extend([
        "",
        f"💡 {p.get('recommendation', '')}",
        f"🚨 אפסט: {p.get('upset_risk', '')}",
    ])

    await update.message.reply_text("\n".join(lines))


def _build_application() -> Application:
    token = _get_token()
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")

    if ":" not in token:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN invalid — must be full token from @BotFather (123456789:ABC...)"
        )

    app = Application.builder().token(token).build()
    app.add_error_handler(_error_handler)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("teams", list_teams_command))
    app.add_handler(CommandHandler("live", live_command))
    app.add_handler(CommandHandler("predict", analyze_match))
    app.add_handler(CommandHandler("analyze", analyze_match))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, analyze_match))
    return app


async def setup_webhook(base_url: Optional[str] = None) -> dict:
    """Initialize bot application and register Telegram webhook."""
    global application

    url = (base_url or os.getenv("PUBLIC_BASE_URL") or "").rstrip("/")
    token = _get_token()

    if not token:
        return {"ok": False, "error": "TELEGRAM_BOT_TOKEN missing"}

    if not url:
        return {"ok": False, "error": "PUBLIC_BASE_URL missing"}

    async with _init_lock:
        if application is None:
            application = _build_application()
            await application.initialize()
            await application.start()
            logger.info("Telegram application started")

        webhook_url = f"{url}/telegram/webhook"
        result = await application.bot.set_webhook(
            url=webhook_url,
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
        )
        info = await application.bot.get_webhook_info()

        logger.info("Webhook set to %s — result=%s", webhook_url, result)

        chat_id = get_telegram_chat_id()
        if chat_id:
            try:
                await application.bot.send_message(
                    chat_id=chat_id,
                    text="✅ @WorldCupApi מחובר ופעיל!\nשלח: ברזיל נגד צרפת",
                )
            except Exception:
                logger.exception("Could not notify TELEGRAM_CHAT_ID")

        return {
            "ok": True,
            "webhook_url": webhook_url,
            "telegram_result": result,
            "webhook_info": {
                "url": info.url,
                "pending_update_count": info.pending_update_count,
                "last_error_message": info.last_error_message,
                "last_error_date": str(info.last_error_date) if info.last_error_date else None,
            },
        }


async def get_webhook_status() -> dict:
    token = _get_token()
    if not token:
        return {"configured": False, "error": "no token"}

    if application:
        info = await application.bot.get_webhook_info()
        return {
            "configured": True,
            "application_running": True,
            "webhook_url": info.url,
            "pending_updates": info.pending_update_count,
            "last_error": info.last_error_message,
        }

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f"https://api.telegram.org/bot{token}/getWebhookInfo")
    if response.status_code != 200:
        return {"configured": False, "error": "invalid token or telegram API error"}

    data = response.json().get("result", {})
    return {
        "configured": True,
        "application_running": False,
        "webhook_url": data.get("url"),
        "pending_updates": data.get("pending_update_count"),
        "last_error": data.get("last_error_message"),
    }


async def ensure_ready() -> bool:
    if application is not None:
        return True
    result = await setup_webhook()
    return result.get("ok", False)


async def process_update(update_data: dict) -> None:
    if not await ensure_ready():
        logger.error("Bot not ready — cannot process update")
        return

    update = Update.de_json(update_data, application.bot)
    await application.process_update(update)


async def shutdown_webhook() -> None:
    global application
    if not application:
        return
    try:
        await application.bot.delete_webhook(drop_pending_updates=True)
        await application.stop()
        await application.shutdown()
    finally:
        application = None
