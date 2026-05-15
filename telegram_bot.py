import os

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    ContextTypes,
    filters,
    CommandHandler
)

from dotenv import load_dotenv

from backend.app.services.prediction_engine import generate_prediction

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "⚽ Football Analyst AI Ready\n\nSend:\nBrazil vs France"
    )

async def analyze_match(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

    if "vs" not in text.lower():

        await update.message.reply_text(
            "Send match like:\nBrazil vs France"
        )

        return

    parts = text.split("vs")

    team1 = parts[0].strip()
    team2 = parts[1].strip()

    prediction = generate_prediction(team1, team2)

    probs = prediction["probabilities"]

    response = f"""
⚽ {team1} vs {team2}

📊 Win Probability

{team1}: {probs['team1_win']}%
Draw: {probs['draw']}%
{team2}: {probs['team2_win']}%

🔥 Analysis
- {prediction['analysis'][0]}
- {prediction['analysis'][1]}
- {prediction['analysis'][2]}

🚨 Upset Risk:
{prediction['upset_risk']}
"""

    await update.message.reply_text(response)

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))

app.add_handler(
    MessageHandler(filters.TEXT, analyze_match)
)

app.run_polling()