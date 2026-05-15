from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.predictions import router as prediction_router
from backend.app.api.matches import router as matches_router

app = FastAPI(
    title="Football Analyst AI"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():

    return {
        "service": "Football Analyst AI",
        "status": "running"
    }

@app.get("/health")
async def health():

    return {"ok": True}

app.include_router(prediction_router)
app.include_router(matches_router)