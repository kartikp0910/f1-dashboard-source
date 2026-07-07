"""Live race center endpoints powered by FastF1 current session state."""
import logging

from fastapi import APIRouter

from app.lib.fastf1_provider import FastF1Unavailable, get_current_track_payload

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/live/track")
async def get_live_track() -> dict:
    """Return FastF1 current race state and live packets when a race is active."""
    try:
        return await get_current_track_payload()
    except FastF1Unavailable as exc:
        logger.warning("FastF1 is unavailable: %s", exc)
        return {
            "mode": "provider-unavailable",
            "provider": "fastf1",
            "provider_warning": str(exc),
            "is_live": False,
            "session": {"session_name": "FastF1 unavailable", "session_type": "Unavailable"},
            "weather": None,
            "race_control": [],
            "cars": [],
            "refresh_ms": 30000,
        }
    except Exception as exc:
        logger.warning("FastF1 live track failed: %s", exc)
        return {
            "mode": "provider-error",
            "provider": "fastf1",
            "provider_warning": "FastF1 could not load current race data.",
            "is_live": False,
            "session": {"session_name": "FastF1 error", "session_type": "Unavailable"},
            "weather": None,
            "race_control": [],
            "cars": [],
            "refresh_ms": 30000,
        }
