"""Standings endpoints"""
from typing import List
from fastapi import APIRouter, Query
from app.models import DriverStandingResponse
from app.lib.fastf1_provider import FastF1Unavailable, get_current_driver_standings
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/standings", response_model=List[DriverStandingResponse])
async def get_standings(season: str = Query("current")):
    """Get current championship standings from FastF1."""
    try:
        year = None if season == "current" else int(season)
        return await get_current_driver_standings(year)
    except FastF1Unavailable as e:
        logger.warning("FastF1 unavailable for standings: %s", e)
        return []
    except Exception as e:
        logger.warning("FastF1 standings fetch failed: %s", e)
        return []
