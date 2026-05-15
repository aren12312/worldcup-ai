# WorldCup AI Predictor

AI-based football prediction platform deployed automatically from GitHub to Google Cloud Run.

## Features
- Match predictions
- Historical analysis
- Team momentum
- Player form
- Weather analysis
- Betting odds integration
- Tactical insights
- Live API integration

## Required APIs

### API-Football
https://www.api-football.com/

Used for:
- Fixtures
- Teams
- Players
- Injuries
- Lineups
- Live matches

Secret name:
API_FOOTBALL_KEY

### The Odds API
https://the-odds-api.com/

Used for:
- Betting odds
- Market movement

Secret name:
ODDS_API_KEY

### OpenWeatherMap API
https://openweathermap.org/api

Used for:
- Weather conditions
- Wind/rain impact

Secret name:
WEATHER_API_KEY

## GitHub Secrets

Add inside:
GitHub → Settings → Secrets and variables → Actions

- GCP_PROJECT_ID
- GCP_SA_KEY
- API_FOOTBALL_KEY
- ODDS_API_KEY
- WEATHER_API_KEY

## Deploy Flow

GitHub Push → GitHub Actions → Artifact Registry → Cloud Run
