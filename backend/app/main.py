"""FastAPI main application"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import (
    constructors,
    drivers,
    health,
    live,
    news,
    predictions,
    profiles,
    races,
    season,
    standings,
    telemetry,
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="F1 Dashboard API",
    description="Formula 1 Dashboard API with predictions",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(drivers.router)
app.include_router(races.router)
app.include_router(standings.router)
app.include_router(predictions.router)
app.include_router(season.router)
app.include_router(telemetry.router)
app.include_router(live.router)
app.include_router(profiles.router)
app.include_router(constructors.router)
app.include_router(news.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "F1 Dashboard API", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
