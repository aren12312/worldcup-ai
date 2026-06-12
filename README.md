# WorldCup AI — Match Analyst MVP

AI-powered World Cup match predictions with a FastAPI backend, Telegram bot, and Next.js website.

## What it does

- **Poisson Monte Carlo** simulations based on team attack/defense ratings
- **50+ national teams** built-in (works without API keys)
- **API-Football enrichment** when `API_FOOTBALL_KEY` is set
- **OpenAI analysis** when `OPENAI_API_KEY` is set (stats-based fallback otherwise)
- **Telegram bot** and **web UI** share the same prediction API

## Quick start

### 1. Environment

```bash
cp .env.example .env
# Optional: add API_FOOTBALL_KEY, OPENAI_API_KEY, TELEGRAM_TOKEN
```

### 2. Backend

```bash
cd /home/user/worldcup-ai/worldcup-ai
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload --port 8080
```

API docs: http://localhost:8080/docs

Try: http://localhost:8080/predict?team1=Brazil&team2=France

### 3. Website

```bash
cd frontend
cp .env.local.example .env.local
npm install
npm run dev
```

Open: http://localhost:3000

### 4. Telegram bot

```bash
# From repo root, with backend running
pip install httpx python-dotenv python-telegram-bot
python telegram_bot.py
```

Send: `Brazil vs France` or `/predict Brazil vs France`

### Docker (backend + bot)

```bash
docker compose up --build
```

## API endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /predict?team1=&team2=` | Full match prediction |
| `GET /teams` | List supported teams |
| `GET /live-matches` | Live fixtures (requires API key) |
| `GET /upcoming-matches` | Upcoming World Cup fixtures |
| `GET /health` | Health check |

## Stack

- FastAPI + NumPy (Poisson simulation)
- API-Football (optional live data)
- OpenAI (optional narrative analysis)
- Next.js + Tailwind + Recharts
- python-telegram-bot

## Deploy to Cloud Run (worldcup-ai)

Push to `main` triggers GitHub Actions which deploys:

| Service | Cloud Run name | Role |
|---------|----------------|------|
| Backend API | `worldcup-ai` | predictions, teams, live matches |
| Website | `worldcup-ai-web` | Next.js UI |

### GitHub secrets (required)

In GitHub repo **Settings → Secrets → Actions**, set:

- `API_FOOTBALL_KEY` — optional, enriches live stats
- `OPENAI_API_KEY` — optional, AI narrative analysis

### Deploy

```bash
git add .
git commit -m "Deploy MVP to Cloud Run"
git push origin main
```

After deploy, find URLs:

```bash
gcloud run services describe worldcup-ai --region us-central1 --format='value(status.url)'
gcloud run services describe worldcup-ai-web --region us-central1 --format='value(status.url)'
```

### Telegram bot with Cloud Run

Run the bot locally or on a VM and point it at your backend:

```bash
export API_URL=https://YOUR-BACKEND-URL
export TELEGRAM_TOKEN=your-bot-token
python telegram_bot.py
```

