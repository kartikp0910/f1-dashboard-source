"""Live telemetry endpoints powered by OpenF1."""
from datetime import datetime, timedelta, timezone
import logging
import os

import httpx
from fastapi import APIRouter, HTTPException, Query

from app.models import TelemetryResponse

logger = logging.getLogger(__name__)
router = APIRouter()
OPENF1_BASE = "https://api.openf1.org/v1"
VERIFY_SSL = os.getenv("F1_API_VERIFY_SSL", "false").lower() == "true"


async def fetch_openf1(path: str, params: dict) -> list:
    async with httpx.AsyncClient(timeout=20, verify=VERIFY_SSL) as client:
        response = await client.get(f"{OPENF1_BASE}/{path}", params=params)
        response.raise_for_status()
        return response.json()


@router.get("/telemetry", response_model=list[TelemetryResponse])
async def get_telemetry(
    race_id: str = Query("latest"),
    driver_id: str = Query("latest"),
):
    """Return the latest available car-data packets from the newest F1 session."""
    try:
        sessions = await fetch_openf1("sessions", {"session_key": "latest"})
        if not sessions:
            raise HTTPException(status_code=404, detail="No OpenF1 session is currently available")

        session = sessions[-1]
        session_key = session["session_key"]
        drivers = await fetch_openf1("drivers", {"session_key": session_key})
        if not drivers:
            raise HTTPException(status_code=404, detail="No drivers found for the latest session")

        by_number = {}
        for driver in drivers:
            by_number[str(driver.get("driver_number"))] = driver

        if driver_id != "latest":
            selected_numbers = [driver_id]
        else:
            selected_numbers = list(by_number.keys())[:6]

        session_end = session.get("date_end")
        try:
            end_time = datetime.fromisoformat(session_end.replace("Z", "+00:00")) if session_end else datetime.now(timezone.utc)
        except ValueError:
            end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(minutes=3)

        results = []
        for number in selected_numbers:
            packets = await fetch_openf1(
                "car_data",
                {
                    "session_key": session_key,
                    "driver_number": number,
                    "date>": start_time.isoformat(),
                },
            )
            if not packets:
                continue

            packet = packets[-1]
            driver = by_number.get(str(number), {})
            brake_value = packet.get("brake", 0)
            throttle_value = packet.get("throttle", 0)
            drs_value = int(packet.get("drs", 0) or 0)
            results.append(
                TelemetryResponse(
                    driver_id=str(number),
                    driver_name=driver.get("full_name") or driver.get("broadcast_name") or f"Driver {number}",
                    speed=float(packet.get("speed", 0) or 0),
                    throttle=float(throttle_value or 0) / 100,
                    brake=float(brake_value or 0) / 100 if float(brake_value or 0) > 1 else float(brake_value or 0),
                    drs=drs_value >= 10,
                    gear=int(packet.get("n_gear", 0) or 0),
                    lap=0,
                )
            )

        if not results:
            raise HTTPException(status_code=404, detail="No recent telemetry packets are available for this session")
        return results
    except HTTPException:
        raise
    except httpx.HTTPError as exc:
        logger.error("OpenF1 request failed: %s", exc)
        raise HTTPException(status_code=503, detail="Live telemetry provider is unavailable")
    except Exception as exc:
        logger.error("Telemetry processing failed: %s", exc)
        raise HTTPException(status_code=500, detail="Could not process live telemetry")
