"""Live telemetry endpoints powered by FastF1 current race data."""
import logging

from fastapi import APIRouter, Query

from app.lib.fastf1_provider import FastF1Unavailable, get_current_track_payload
from app.models import TelemetryResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/telemetry", response_model=list[TelemetryResponse])
async def get_telemetry(
    race_id: str = Query("latest"),
    driver_id: str = Query("latest"),
):
    """Return FastF1 telemetry packets for an active race only."""
    try:
        payload = await get_current_track_payload()
        if not payload.get("is_live"):
            return []
        cars = payload.get("cars", [])
        if driver_id != "latest":
            cars = [car for car in cars if str(car.get("driver_number")) == str(driver_id)]
        return [
                TelemetryResponse(
                    driver_id=str(car.get("driver_number")),
                    driver_name=car.get("name") or f"Driver {car.get('driver_number')}",
                    speed=float(car.get("speed", 0) or 0),
                    throttle=float(car.get("throttle", 0) or 0),
                    brake=float(car.get("brake", 0) or 0),
                    drs=bool(car.get("drs")),
                    gear=int(car.get("gear", 0) or 0),
                    lap=0,
                )
            for car in cars[:6]
        ]
    except FastF1Unavailable as exc:
        logger.warning("FastF1 unavailable for telemetry: %s", exc)
        return []
    except Exception as exc:
        logger.warning("FastF1 telemetry processing failed: %s", exc)
        return []
