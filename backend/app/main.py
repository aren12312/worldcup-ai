import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from app.routes.predictions import router as prediction_router
from telegram import Update, Bot
from app.services.prediction_engine import generate_prediction

app = FastAPI(title="WorldCup AI - Pro")

# חיבור ה-API Routes
app.include_router(prediction_router, prefix="/api/v1")

# אתחול בוט טלגרם
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = Bot(token=TOKEN) if TOKEN else None

@app.post("/webhook/telegram")
async def telegram_webhook(request: Request):
    """נתיב שהבוט משתמש בו כדי לקבל הודעות"""
    if not bot: return {"error": "no token"}
    try:
        data = await request.json()
        update = Update.de_json(data, bot)
        if update.message and update.message.text:
            text = update.message.text
            if " vs " in text.lower():
                t1, t2 = text.lower().split(" vs ")
                res = generate_prediction(t1.strip(), t2.strip())
                msg = f"⚽ *ניתוח: {res['match']}*\n\n📊 סיכויים:\n{t1.capitalize()}: {res['probabilities']['home']}\n{t2.capitalize()}: {res['probabilities']['away']}\n\n💡 {res['analysis']}"
                await bot.send_message(chat_id=update.message.chat_id, text=msg, parse_mode="Markdown")
            else:
                await bot.send_message(chat_id=update.message.chat_id, text="שלחו הודעה בפורמט: Arsenal vs Real Madrid")
    except Exception as e:
        print(f"Error: {e}")
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
def home():
    """החזרת ה-UI המקצועי המלא של האתר"""
    return """
    <!DOCTYPE html>
    <html lang="he" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>WorldCup AI - Professional Dashboard</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
            body { font-family: 'Inter', sans-serif; background: #0f172a; color: #f1f5f9; }
        </style>
    </head>
    <body class="p-6 md:p-12">
        <div class="max-w-4xl mx-auto text-center">
            <h1 class="text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-400 mb-4">WorldCup AI</h1>
            <p class="text-slate-400 mb-12 italic text-lg text-center">ניתוח נתונים בזמן אמת מבוסס ליגות אירופאיות</p>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
                <input id="t1" type="text" placeholder="קבוצה 1 (למשל: Arsenal)" class="bg-slate-800 border border-slate-700 p-4 rounded-2xl focus:ring-2 focus:ring-blue-500 outline-none shadow-xl">
                <input id="t2" type="text" placeholder="קבוצה 2 (למשל: Real Madrid)" class="bg-slate-800 border border-slate-700 p-4 rounded-2xl focus:ring-2 focus:ring-blue-500 outline-none shadow-xl">
            </div>
            
            <button onclick="analyze()" class="w-full bg-blue-600 hover:bg-blue-500 py-4 rounded-2xl font-bold text-xl transition-all shadow-lg hover:scale-[1.01]">נתח משחק עכשיו</button>

            <div id="loader" class="hidden mt-10 text-blue-400 animate-pulse">המערכת מעבדת נתוני ליגה...</div>

            <div id="dashboard" class="hidden mt-12 space-y-8 text-right">
                <div class="bg-slate-800 p-8 rounded-3xl border border-slate-700 shadow-2xl">
                    <h3 class="text-2xl font-bold mb-6 text-center text-blue-300" id="match-title"></h3>
                    <div class="flex items-center justify-between h-10 bg-slate-900 rounded-full overflow-hidden border border-slate-700 p-1">
                        <div id="bar-home" class="bg-gradient-to-r from-blue-600 to-blue-400 h-full flex items-center justify-center font-bold text-sm transition-all duration-1000" style="width: 0%"></div>
                        <div id="bar-draw" class="bg-slate-700 h-full flex items-center justify-center font-bold text-sm" style="width: 15%">תיקו</div>
                        <div id="bar-away" class="bg-gradient-to-r from-emerald-400 to-emerald-600 h-full flex items-center justify-center font-bold text-sm transition-all duration-1000" style="width: 0%"></div>
                    </div>
                    <p id="analysis-text" class="mt-8 text-slate-300 leading-relaxed bg-slate-900/50 p-4 rounded-xl border border-slate-700/50"></p>
                </div>
            </div>
        </div>

        <script>
            async function analyze() {
                const t1 = document.getElementById('t1').value;
                const t2 = document.getElementById('t2').value;
                if(!t1 || !t2) return;

                document.getElementById('loader').classList.remove('hidden');
                document.getElementById('dashboard').classList.add('hidden');

                try {
                    const res = await fetch(`/api/v1/predict?team1=${t1}&team2=${t2}`);
                    const data = await res.json();

                    document.getElementById('match-title').innerText = data.match;
                    document.getElementById('bar-home').style.width = data.probabilities.home;
                    document.getElementById('bar-home').innerText = data.probabilities.home;
                    document.getElementById('bar-away').style.width = data.probabilities.away;
                    document.getElementById('bar-away').innerText = data.probabilities.away;
                    document.getElementById('analysis-text').innerText = data.analysis;

                    document.getElementById('loader').classList.add('hidden');
                    document.getElementById('dashboard').classList.remove('hidden');
                } catch(e) {
                    alert("שגיאה במשיכת נתונים. וודא ששמות הקבוצות באנגלית.");
                    document.getElementById('loader').classList.add('hidden');
                }
            }
        </script>
    </body>
    </html>
    """
