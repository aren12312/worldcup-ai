import os

import httpx
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
API_URL = os.getenv("API_URL", "http://localhost:8080")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚽ WorldCup AI Analyst\n\n"
        "Send a match:\n"
        "Brazil vs France\n\n"
        "Commands:\n"
        "/predict Brazil vs France\n"
        "/teams — list supported teams"
    )


async def list_teams_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(f"{API_URL}/teams")
        response.raise_for_status()
        teams = response.json()["teams"]
        preview = ", ".join(teams[:15])
        await update.message.reply_text(
            f"Supported teams ({len(teams)}):\n{preview}\n... and more"
        )
    except httpx.HTTPError:
        await update.message.reply_text("Could not reach the API. Is the backend running?")


def _parse_match(text: str):
    if " vs " in text.lower():
        parts = text.lower().split(" vs ", 1)
    elif "vs" in text.lower():
        idx = text.lower().index("vs")
        parts = [text[:idx], text[idx + 2 :]]
    else:
        return None

    team1 = parts[0].replace("/predict", "").strip()
    team2 = parts[1].strip()
    if not team1 or not team2:
        return None
    return team1, team2


async def analyze_match(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    parsed = _parse_match(text)

    if not parsed:
        await update.message.reply_text("Send a match like:\nBrazil vs France")
        return

    team1, team2 = parsed

    await update.message.reply_text(f"Analyzing {team1.title()} vs {team2.title()}...")

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(
                f"{API_URL}/predict",
                params={"team1": team1, "team2": team2},
            )
        response.raise_for_status()
        prediction = response.json()
    except httpx.HTTPStatusError as exc:
        detail = exc.response.json().get("detail", "Unknown error")
        await update.message.reply_text(f"❌ {detail}")
        return
    except httpx.HTTPError:
        await update.message.reply_text(
            f"Could not reach API at {API_URL}. Start the backend first."
        )
        return

    probs = prediction["probabilities"]
    match = prediction["match"]
    t1, t2 = match.split(" vs ")
    xg = prediction["expected_goals"]

    lines = [
        f"⚽ {match}",
        "",
        "📊 Win Probability",
        f"{t1}: {probs['team1_win']}%",
        f"Draw: {probs['draw']}%",
        f"{t2}: {probs['team2_win']}%",
        "",
        "⚽ Expected Goals",
        f"{t1}: {xg[t1]} | {t2}: {xg[t2]}",
        "",
        "🔍 Analysis",
    ]
    for point in prediction["analysis"]:
        lines.append(f"• {point}")

    lines.extend(
        [
            "",
            f"💡 Recommendation:\n{prediction['recommendation']}",
            "",
            f"🚨 Upset Risk: {prediction['upset_risk']}",
        ]
    )

    await update.message.reply_text("\n".join(lines))


def main():
    if not TOKEN:
        raise SystemExit("TELEGRAM_TOKEN is missing. Add it to .env")

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("teams", list_teams_command))
    app.add_handler(CommandHandler("predict", analyze_match))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, analyze_match))
    app.run_polling()


if __name__ == "__main__":
    main()
