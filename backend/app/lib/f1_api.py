"""F1 API utilities for fetching Jolpica/Ergast data."""
import os
import time
import asyncio
import httpx
import logging
from typing import TypeVar, Optional

logger = logging.getLogger(__name__)

JOLPICA_BASE = "https://api.jolpi.ca/ergast/f1"

T = TypeVar('T')
VERIFY_SSL = os.getenv("F1_API_VERIFY_SSL", "false").lower() == "true"
_CACHE: dict[str, tuple[float, dict]] = {}
_CACHE_TTL_SECONDS = 60


async def fetch_ergast(path: str, timeout: int = 15) -> dict:
    """
    Fetch data from Ergast F1 API
    
    Args:
        path: API endpoint path
        timeout: Request timeout in seconds
        
    Returns:
        JSON response data
    """
    url = f"{JOLPICA_BASE}{path}"
    cached = _CACHE.get(url)
    if cached and time.time() - cached[0] < _CACHE_TTL_SECONDS:
        return cached[1]

    last_error = None
    async with httpx.AsyncClient(verify=VERIFY_SSL) as client:
        for attempt in range(3):
            try:
                response = await client.get(
                    url,
                    headers={"Accept": "application/json"},
                    timeout=timeout
                )
                response.raise_for_status()
                data = response.json()
                _CACHE[url] = (time.time(), data)
                return data
            except httpx.HTTPError as error:
                last_error = error
                if attempt < 2:
                    await asyncio.sleep(0.35 * (attempt + 1))

    logger.error(f"Ergast API error for {url}: {last_error}")
    if cached:
        return cached[1]
    raise last_error


CONSTRUCTOR_COLORS = {
    "red_bull": "#3671C6",
    "ferrari": "#E8002D",
    "mercedes": "#27F4D2",
    "mclaren": "#FF8000",
    "aston_martin": "#229971",
    "alpine": "#FF87BC",
    "williams": "#64C4FF",
    "rb": "#6692FF",
    "kick_sauber": "#52E252",
    "haas": "#B6BABD",
    "sauber": "#52E252",
    "alphatauri": "#5E8FAA",
    "alfa": "#C92D4B",
    "force_india": "#F596C8",
    "racing_point": "#F596C8",
    "toro_rosso": "#5E8FAA",
    "virgin": "#FF65FF",
    "marussia": "#FF65FF",
    "caterham": "#2D826D",
    "minardi": "#D2B48C",
}


def get_constructor_color(constructor_id: Optional[str]) -> str:
    """
    Get constructor brand color
    
    Args:
        constructor_id: Constructor identifier
        
    Returns:
        Hex color code
    """
    if not constructor_id:
        return "#FFFFFF"
    return CONSTRUCTOR_COLORS.get(constructor_id.lower(), "#CCCCCC")
