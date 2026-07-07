"""Driver profile endpoints backed by current FastF1 standings."""
import logging
from typing import Any

from fastapi import APIRouter, Query

from app.lib.fastf1_provider import FastF1Unavailable, get_current_driver_standings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/drivers/profiles")
async def get_driver_profiles(season: str = Query("current")) -> list[dict[str, Any]]:
    """Return current driver profile cards from FastF1 standings."""
    try:
        year = None if season == "current" else int(season)
        standings = await get_current_driver_standings(year)
    except FastF1Unavailable as exc:
        logger.warning("FastF1 unavailable for driver profiles: %s", exc)
        return []
    except Exception as exc:
        logger.warning("FastF1 driver profile fetch failed: %s", exc)
        return []

    leader_points = max(float(standings[0].points or 1), 1) if standings else 1
    profiles: list[dict[str, Any]] = []
    for driver in standings:
        profiles.append(
            {
                "driver_id": driver.driver_id,
                "driver_number": None,
                "code": driver.code,
                "given_name": driver.given_name,
                "family_name": driver.family_name,
                "driver_name": f"{driver.given_name} {driver.family_name}",
                "nationality": driver.nationality,
                "date_of_birth": driver.date_of_birth,
                "constructor_id": driver.constructor_id,
                "constructor_name": driver.constructor_name,
                "constructor_color": driver.constructor_color,
                "headshot_url": None,
                "position": driver.position,
                "points": driver.points,
                "wins": driver.wins,
                "podium_probability_hint": min(0.96, round((driver.wins * 0.08) + (max(0, 22 - driver.position) / 30), 2)),
                "form_score": min(100, round((float(driver.points or 0) / leader_points) * 100)),
                "mode": "fastf1",
            }
        )
    return profiles
