"""Driver endpoints"""
from typing import List, Optional
from fastapi import APIRouter, Query
from app.models import DriverStandingResponse
from app.lib.f1_api import fetch_ergast, get_constructor_color
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/drivers", response_model=List[DriverStandingResponse])
async def get_drivers(season: str = Query("current")):
    """Get list of drivers with current standings"""
    try:
        drivers_data, standings_data = await fetch_all_drivers_data(season)
        
        drivers = drivers_data.get("MRData", {}).get("DriverTable", {}).get("Drivers", [])
        standings = standings_data.get("MRData", {}).get("StandingsTable", {}).get("StandingsLists", [{}])[0].get("DriverStandings", [])
        
        standing_map = {s["Driver"]["driverId"]: s for s in standings}
        
        result = []
        for driver in drivers:
            standing = standing_map.get(driver["driverId"], {})
            result.append(DriverStandingResponse(
                driver_id=driver["driverId"],
                code=driver.get("code", driver["driverId"][:3].upper()),
                given_name=driver["givenName"],
                family_name=driver["familyName"],
                nationality=driver["nationality"],
                date_of_birth=driver.get("dateOfBirth"),
                points=float(standing.get("points", 0)),
                position=int(standing.get("position", 0)),
                wins=int(standing.get("wins", 0)),
                constructor_id=standing.get("Constructors", [{}])[0].get("constructorId"),
                constructor_name=standing.get("Constructors", [{}])[0].get("name"),
                constructor_color=get_constructor_color(standing.get("Constructors", [{}])[0].get("constructorId"))
            ))
        
        return result
    except Exception as e:
        logger.error(f"Error fetching drivers: {e}")
        raise


async def fetch_all_drivers_data(season: str):
    """Fetch drivers and standings data"""
    import asyncio
    drivers_task = fetch_ergast(f"/{season}/drivers.json?limit=30")
    standings_task = fetch_ergast(f"/{season}/driverStandings.json?limit=30")
    return await asyncio.gather(drivers_task, standings_task)
