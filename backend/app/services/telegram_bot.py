import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from app.services.prediction_engine import generate_prediction

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_text = update.message.text
    
    if " vs " not in user_text.lower():
        await update.message.reply_text("ברוכים הבאים ל-WorldCup AI! ⚽\nשלחו שמות קבוצות בפורמט: Arsenal vs Liverpool")
        return

    teams = user_text.lower().split(" vs ")
    team1, team2 = teams[0].strip(), teams[1].strip()
    
    await update.message.reply_text(f"🔍 מנתח נתונים עבור {team1} נגד {team2}...")

    data = generate_prediction(team1, team2)
    
    response = (
        f"⚽ *ניתוח משחק: {data['match']}*\n\n"
        f"📊 *סיכויי ניצחון:*\n"
        f"🏠 {team1.capitalize()}: {data['probabilities']['home']}\n"
        f"🤝 תיקו: {data['probabilities']['draw']}\n"
        f"🚀 {team2.capitalize()}: {data['probabilities']['away']}\n\n"
        f"🏆 *מפגשי עבר (H2H):*\n" + "\n".join([f"• {m}" for m in data['h2h']]) + "\n\n"
        f"💡 *ניתוח מומחה:*\n_{data['expert_analysis']}_"
    )
    
    await update.message.reply_markdown(response)

async def start_bot():
    if not TOKEN:
        print("Telegram Token missing! Bot will not start.")
        return
    
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    await application.initialize()
    await application.start()
    await application.updater.start_polling()