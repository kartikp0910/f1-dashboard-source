"""Standings endpoints"""
from typing import List
from fastapi import APIRouter, Query
from app.models import DriverStandingResponse
from app.lib.f1_api import fetch_ergast, get_constructor_color
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/standings", response_model=List[DriverStandingResponse])
async def get_standings(season: str = Query("current")):
    """Get current championship standings"""
    try:
        data = await fetch_ergast(f"/{season}/driverStandings.json?limit=25")
        standings = data.get("MRData", {}).get("StandingsTable", {}).get("StandingsLists", [{}])[0].get("DriverStandings", [])
        
        result = []
        for standing in standings:
            driver = standing["Driver"]
            constructor = standing.get("Constructors", [{}])[0]
            result.append(DriverStandingResponse(
                driver_id=driver["driverId"],
                code=driver.get("code", driver["driverId"][:3].upper()),
                given_name=driver["givenName"],
                family_name=driver["familyName"],
                nationality=driver["nationality"],
                date_of_birth=driver.get("dateOfBirth"),
                points=float(standing["points"]),
                position=int(standing["position"]),
                wins=int(standing["wins"]),
                constructor_id=constructor.get("constructorId"),
                constructor_name=constructor.get("name"),
                constructor_color=get_constructor_color(constructor.get("constructorId"))
            ))
        
        return result
    except Exception as e:
        logger.error(f"Error fetching standings: {e}")
        raise
