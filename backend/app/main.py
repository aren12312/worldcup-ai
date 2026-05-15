from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from app.routes.predictions import router as prediction_router

app = FastAPI(title="WorldCup AI")
app.include_router(prediction_router, prefix="/api/v1")

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html lang="he" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>WorldCup AI Predictor</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Assistant:wght@400;700&display=swap" rel="stylesheet">
        <style> body { font-family: 'Assistant', sans-serif; } </style>
    </head>
    <body class="bg-gray-900 text-white min-h-screen flex flex-col items-center justify-center p-4">
        <div class="max-w-md w-full bg-gray-800 rounded-xl shadow-2xl p-8 border border-gray-700">
            <h1 class="text-3-xl font-bold text-center mb-8 text-blue-400">⚽ WorldCup AI Predictor</h1>
            
            <div class="space-y-4">
                <input id="t1" type="text" placeholder="קבוצה ביתית (למשל: Arsenal)" class="w-full p-3 rounded bg-gray-700 border border-gray-600 focus:outline-none focus:border-blue-500 text-center">
                <div class="text-center font-bold text-gray-500">נגד</div>
                <input id="t2" type="text" placeholder="קבוצת חוץ (למשל: Liverpool)" class="w-full p-3 rounded bg-gray-700 border border-gray-600 focus:outline-none focus:border-blue-500 text-center">
                
                <button onclick="getPrediction()" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-lg transition duration-300 transform hover:scale-105">
                    קבל תחזית AI
                </button>
            </div>

            <div id="result" class="mt-8 hidden space-y-4 border-t border-gray-700 pt-6">
                <div class="flex justify-between text-lg font-bold">
                    <span id="res-t1"></span>
                    <span id="res-prob"></span>
                    <span id="res-t2"></span>
                </div>
                <p id="insight" class="text-sm text-gray-400 italic text-center"></p>
            </div>
        </div>

        <script>
            async function getPrediction() {
                const t1 = document.getElementById('t1').value;
                const t2 = document.getElementById('t2').value;
                if(!t1 || !t2) return alert('נא להזין שתי קבוצות');
                
                const res = await fetch(`/api/v1/predict?team1=${t1}&team2=${t2}`);
                const data = await res.json();
                
                document.getElementById('result').classList.remove('hidden');
                document.getElementById('res-t1').innerText = t1;
                document.getElementById('res-t2').innerText = t2;
                document.getElementById('res-prob').innerText = `${data.probabilities[t1]} - ${data.probabilities[t2]}`;
                document.getElementById('insight').innerText = data.ai_insight;
            }
        </script>
    </body>
    </html>
    """
