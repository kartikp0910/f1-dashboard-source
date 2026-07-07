"""Race endpoints"""
from typing import List
from fastapi import APIRouter, Query
from app.models import RaceResponse
from app.lib.fastf1_provider import (
    FastF1Unavailable,
    get_current_schedule,
    get_previous_results_payload,
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/races", response_model=List[RaceResponse])
async def get_races(season: str = Query("current")):
    """Get the current FastF1 race schedule."""
    try:
        year = None if season == "current" else int(season)
        return await get_current_schedule(year)
    except FastF1Unavailable as e:
        logger.warning("FastF1 unavailable for schedule: %s", e)
        return []
    except Exception as e:
        logger.warning("FastF1 schedule fetch failed: %s", e)
        return []


@router.get("/races/previous-results")
async def get_previous_race_results(season: str = Query("current")):
    """Return FastF1 previous race results and next race countdown metadata."""
    try:
        year = None if season == "current" else int(season)
        return await get_previous_results_payload(year)
    except FastF1Unavailable as e:
        logger.warning("FastF1 unavailable for previous results: %s", e)
        return {
            "mode": "provider-unavailable",
            "provider": "fastf1",
            "is_live": False,
            "message": "FastF1 is unavailable.",
            "previous_race": None,
            "next_race": None,
            "results": [],
        }
    except Exception as e:
        logger.warning("FastF1 previous results fetch failed: %s", e)
        return {
            "mode": "provider-error",
            "provider": "fastf1",
            "is_live": False,
            "message": "FastF1 could not load current race state.",
            "previous_race": None,
            "next_race": None,
            "results": [],
        }
