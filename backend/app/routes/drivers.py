"""Driver endpoints"""
from typing import List
from fastapi import APIRouter, Query
from app.models import DriverStandingResponse
from app.lib.fastf1_provider import FastF1Unavailable, get_current_driver_standings
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/drivers", response_model=List[DriverStandingResponse])
async def get_drivers(season: str = Query("current")):
    """Get list of drivers with current FastF1 standings."""
    try:
        year = None if season == "current" else int(season)
        return await get_current_driver_standings(year)
    except FastF1Unavailable as e:
        logger.warning("FastF1 unavailable for drivers: %s", e)
        return []
    except Exception as e:
        logger.warning("FastF1 driver fetch failed: %s", e)
        return []
