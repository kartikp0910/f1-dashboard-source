"""Race endpoints"""
from typing import List
from fastapi import APIRouter, Query
from app.models import RaceResponse
from app.lib.f1_api import fetch_ergast
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/races", response_model=List[RaceResponse])
async def get_races(season: str = Query("current")):
    """Get races for a season"""
    try:
        data = await fetch_ergast(f"/{season}.json")
        races = data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
        
        result = []
        for race in races:
            circuit = race.get("Circuit", {})
            result.append(RaceResponse(
                race_id=race.get("raceId") or circuit.get("circuitId") or f"{race['season']}-{race['round']}",
                round=int(race["round"]),
                season=int(race["season"]),
                race_name=race["raceName"],
                circuit_id=circuit.get("circuitId"),
                circuit_name=circuit.get("circuitName"),
                date=race["date"],
                time=race.get("time")
            ))
        
        return result
    except Exception as e:
        logger.error(f"Error fetching races: {e}")
        raise
