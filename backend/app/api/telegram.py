from __future__ import annotations

import logging
import os
from typing import Optional

import httpx
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from backend.app.services.config import get_telegram_token

logger = logging.getLogger(__name__)

TOKEN = get_telegram_token()
API_URL = os.getenv("PUBLIC_BASE_URL") or os.getenv("API_URL", "http://localhost:8080")
LANG = "he"

application: Optional[Application] = None


def _parse_match(text: str):
    lowered = text.lower().replace("נגד", "vs").replace(" מול ", " vs ")
    if " vs " in lowered:
        parts = lowered.split(" vs ", 1)
    elif "vs" in lowered:
        idx = lowered.index("vs")
        parts = [lowered[:idx], lowered[idx + 2 :]]
    else:
        return None

    team1 = parts[0].replace("/predict", "").replace("/analyze", "").strip()
    team2 = parts[1].strip()
    if not team1 or not team2:
        return None
    return team1, team2


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚽ WorldCup AI — אנליסט משחקים\n\n"
        "שלח משחק בעברית או באנגלית:\n"
        "🇧🇷 ברזיל נגד צרפת\n"
        "🇧🇷 Brazil vs France\n\n"
        "פקודות:\n"
        "/predict ברזיל נגד צרפת\n"
        "/teams — רשימת קבוצות\n"
        "/live — משחקים live (דורש API key)"
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
        await update.message.reply_text(f"❌ לא הצלחתי להגיע ל-API: {exc}")


async def live_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(f"{API_URL}/live-matches")
        response.raise_for_status()
        data = response.json()
        matches = data.get("matches", [])
        if not matches:
            msg = "אין משחקים live כרגע."
            if not data.get("api_configured"):
                msg += "\n\n⚠️ הוסף FOOTBALL_DATA_API_KEY ב-GitHub Secrets."
            await update.message.reply_text(msg)
            return
        lines = ["🔴 משחקים LIVE:\n"]
        for m in matches[:8]:
            lines.append(
                f"{m.get('home')} {m.get('score')} {m.get('away')} "
                f"({m.get('minute')}' — {m.get('competition', '')})"
            )
        await update.message.reply_text("\n".join(lines))
    except httpx.HTTPError:
        await update.message.reply_text("❌ שגיאה בשליפת משחקים live")


async def analyze_match(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    parsed = _parse_match(text)

    if not parsed:
        await update.message.reply_text(
            "שלח משחק בפורmat:\nברזיל נגד צרפת\nאו Brazil vs France"
        )
        return

    team1, team2 = parsed
    await update.message.reply_text(f"🔍 מנתח {team1} נגד {team2}... (30-60 שניות)")

    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.get(
                f"{API_URL}/predict",
                params={"team1": team1, "team2": team2, "lang": LANG},
            )
        response.raise_for_status()
        p = response.json()
    except httpx.HTTPStatusError as exc:
        detail = exc.response.json().get("detail", "שגיאה לא ידועה")
        await update.message.reply_text(f"❌ {detail}")
        return
    except httpx.HTTPError:
        await update.message.reply_text(
            f"❌ לא הצלחתי להגיע ל-API.\nURL: {API_URL}"
        )
        return

    labels = p.get("labels", {})
    t1 = labels.get("team1", team1)
    t2 = labels.get("team2", team2)
    probs = p["probabilities"]
    xg = p["expected_goals"]

    lines = [
        f"⚽ {p['match']}",
        "",
        "📊 הסתברויות",
        f"{t1}: {probs['team1_win']}%",
        f"תיקו: {probs['draw']}%",
        f"{t2}: {probs['team2_win']}%",
        "",
        "🎯 שערים צפויים (xG)",
        f"{t1}: {xg.get(t1, xg[list(xg.keys())[0]])} | "
        f"{t2}: {xg.get(t2, xg[list(xg.keys())[1]])}",
        "",
        f"📋 {p.get('summary', '')}",
        "",
        "🔍 ניתוח מפורט",
    ]

    for point in p.get("analysis", [])[:6]:
        lines.append(f"• {point}")

    if p.get("h2h_summary"):
        lines.extend(["", f"🔄 {p['h2h_summary']}"])

    lines.extend(
        [
            "",
            f"💡 המלצה: {p['recommendation']}",
            f"🚨 סיכון אפסט: {p['upset_risk']}",
            f"📡 איכות נתונים: {p.get('data_quality', 'לא ידוע')}",
        ]
    )

    await update.message.reply_text("\n".join(lines))


def build_application() -> Application:
    if not TOKEN:
        raise RuntimeError("TELEGRAM_TOKEN is not set")

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("teams", list_teams_command))
    app.add_handler(CommandHandler("live", live_command))
    app.add_handler(CommandHandler("predict", analyze_match))
    app.add_handler(CommandHandler("analyze", analyze_match))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, analyze_match))
    return app


async def setup_webhook(base_url: str) -> None:
    global application
    if not TOKEN:
        logger.warning("TELEGRAM_TOKEN missing — bot disabled")
        return

    application = build_application()
    await application.initialize()
    await application.start()

    webhook_url = f"{base_url.rstrip('/')}/telegram/webhook"
    await application.bot.set_webhook(
        url=webhook_url,
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
    )
    logger.info("Telegram webhook registered: %s", webhook_url)


async def process_update(update_data: dict) -> None:
    if not application:
        return
    update = Update.de_json(update_data, application.bot)
    await application.process_update(update)


async def shutdown_webhook() -> None:
    global application
    if not application:
        return
    await application.bot.delete_webhook(drop_pending_updates=True)
    await application.stop()
    await application.shutdown()
    application = None
