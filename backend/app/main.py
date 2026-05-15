import asyncio
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from app.routes.predictions import router as prediction_router
from app.services.telegram_bot import start_bot

app = FastAPI(title="WorldCup AI")

@app.on_event("startup")
async def startup_event():
    # הפעלת בוט הטלגרם ברקע
    asyncio.create_task(start_bot())

app.include_router(prediction_router, prefix="/api/v1")

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html lang="he" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>WorldCup AI - Dashboard</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style> body { background: #0f172a; color: white; font-family: sans-serif; } </style>
    </head>
    <body class="p-8">
        <div class="max-w-4xl mx-auto">
            <h1 class="text-4xl font-bold text-center text-blue-400 mb-10">WorldCup AI Predictor</h1>
            
            <div class="flex gap-4 mb-8">
                <input id="t1" type="text" placeholder="Arsenal" class="flex-1 p-4 rounded bg-slate-800 border border-slate-700">
                <input id="t2" type="text" placeholder="Real Madrid" class="flex-1 p-4 rounded bg-slate-800 border border-slate-700">
                <button onclick="analyze()" class="bg-blue-600 px-8 rounded font-bold hover:bg-blue-500">נתח</button>
            </div>

            <div id="results" class="hidden space-y-6">
                <div class="bg-slate-800 p-6 rounded-xl border border-blue-500/30">
                    <h2 class="text-xl mb-4 text-center">סיכויי ניצחון</h2>
                    <div class="flex h-8 rounded-full overflow-hidden">
                        <div id="b1" class="bg-blue-500 flex items-center justify-center text-xs"></div>
                        <div id="bd" class="bg-slate-600 flex items-center justify-center text-xs"></div>
                        <div id="b2" class="bg-emerald-500 flex items-center justify-center text-xs"></div>
                    </div>
                </div>
                <div class="grid grid-cols-2 gap-4">
                    <div class="bg-slate-800 p-4 rounded-xl">
                        <h3 class="text-emerald-400 font-bold mb-2">משחקי עבר</h3>
                        <ul id="h2h" class="text-sm space-y-1"></ul>
                    </div>
                    <div class="bg-slate-800 p-4 rounded-xl">
                        <h3 class="text-amber-400 font-bold mb-2">שחקני מפתח</h3>
                        <div id="players" class="text-sm"></div>
                    </div>
                </div>
            </div>
        </div>

        <script>
            async function analyze() {
                const t1 = document.getElementById('t1').value;
                const t2 = document.getElementById('t2').value;
                const res = await fetch(`/api/v1/predict?team1=${t1}&team2=${t2}`);
                const data = await res.json();

                document.getElementById('results').classList.remove('hidden');
                document.getElementById('b1').style.width = data.probabilities.home;
                document.getElementById('b1').innerText = data.probabilities.home;
                document.getElementById('bd').style.width = data.probabilities.draw;
                document.getElementById('b2').style.width = data.probabilities.away;
                document.getElementById('b2').innerText = data.probabilities.away;

                document.getElementById('h2h').innerHTML = data.h2h.map(m => `<li>${m}</li>`).join('');
                document.getElementById('players').innerText = data.expert_analysis;
            }
        </script>
    </body>
    </html>
    """
