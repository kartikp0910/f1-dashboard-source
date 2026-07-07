"""Season endpoints"""
from typing import List
from fastapi import APIRouter
from app.models import SeasonResponse
from app.lib.demo_data import demo_seasons
from app.lib.f1_api import fetch_ergast
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/seasons", response_model=List[SeasonResponse])
async def get_seasons():
    """Get available F1 seasons"""
    try:
        data = await fetch_ergast("/seasons.json?limit=100")
        seasons = data.get("MRData", {}).get("SeasonTable", {}).get("Seasons", [])
        
        return [
            SeasonResponse(season=int(s["season"]), url=s["url"])
            for s in seasons
        ]
    except Exception as e:
        logger.warning("Error fetching seasons, returning demo data: %s", e)
        return demo_seasons()
