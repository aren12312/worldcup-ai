import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from app.routes.predictions import router as prediction_router
from telegram import Update, Bot
from app.services.prediction_engine import generate_prediction

app = FastAPI()
app.include_router(prediction_router, prefix="/api/v1")

# אתחול בוט טלגרם (Webhook Mode)
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = Bot(token=TOKEN) if TOKEN else None

@app.post("/webhook/telegram")
async def telegram_webhook(request: Request):
    update = Update.de_json(await request.json(), bot)
    if update.message and update.message.text:
        text = update.message.text
        if " vs " in text.lower():
            t1, t2 = text.lower().split(" vs ")
            res = generate_prediction(t1.strip(), t2.strip())
            msg = f"⚽ *{res['match']}*\n📈 סיכויים: {res['probabilities']['home']} - {res['probabilities']['away']}\n\n💡 {res['analysis']}"
            await bot.send_message(chat_id=update.message.chat_id, text=msg, parse_mode="Markdown")
        else:
            await bot.send_message(chat_id=update.message.chat_id, text="שלח קבוצות בפורמט: Arsenal vs Real Madrid")
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
def home():
    # כאן הקוד של ה-HTML מהגרסה הקודמת (הוא תקין)
    return "<h1>WorldCup AI Live</h1>"
