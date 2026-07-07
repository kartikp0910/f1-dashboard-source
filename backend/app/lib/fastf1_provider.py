"""FastF1-backed current season and session data helpers."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import asyncio
import logging
import math
import os
import urllib3
from typing import Any, Optional

from app.models import RaceResponse
from app.models import DriverStandingResponse

logger = logging.getLogger(__name__)

CACHE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".fastf1-cache"))
SESSION_WINDOW_HOURS = 4
VERIFY_SSL = os.getenv("F1_API_VERIFY_SSL", "false").lower() == "true"


class FastF1Unavailable(RuntimeError):
    """Raised when FastF1 cannot provide current data."""


def _to_utc(value: Any) -> Optional[datetime]:
    if value is None:
        return None
    if hasattr(value, "to_pydatetime"):
        value = value.to_pydatetime()
    if isinstance(value, str):
        if not value:
            return None
        value = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if not isinstance(value, datetime):
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _finite_number(value: Any) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def _safe_value(row: Any, key: str, default: Any = None) -> Any:
    try:
        value = row.get(key, default)
    except AttributeError:
        value = getattr(row, key, default)
    if value is None:
        return default
    try:
        if value != value:
            return default
    except Exception:
        pass
    return value


def _fastf1():
    try:
        import fastf1
    except ImportError as exc:
        raise FastF1Unavailable("FastF1 is not installed. Run pip install -r backend/requirements.txt.") from exc

    os.makedirs(CACHE_DIR, exist_ok=True)
    try:
        fastf1.Cache.enable_cache(CACHE_DIR)
    except Exception as exc:
        logger.debug("FastF1 cache setup skipped: %s", exc)
    if not VERIFY_SSL:
        try:
            import fastf1.req as fastf1_req

            fastf1_req.Cache._requests_session.verify = False
            fastf1_req.Cache._requests_session_cached.verify = False
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        except Exception as exc:
            logger.debug("FastF1 SSL verification override skipped: %s", exc)
    return fastf1


def _ergast():
    _fastf1()
    try:
        from fastf1.ergast import Ergast
    except ImportError as exc:
        raise FastF1Unavailable("FastF1 Ergast interface is unavailable.") from exc
    return Ergast(result_type="pandas", limit=100)


def _race_datetime(row: Any) -> Optional[datetime]:
    for key in ("Session5DateUtc", "Session5Date", "EventDate"):
        value = _to_utc(_safe_value(row, key))
        if value:
            return value
    return None


def _event_to_race(row: Any, year: int) -> RaceResponse:
    round_number = int(_safe_value(row, "RoundNumber", 0) or 0)
    event_name = str(_safe_value(row, "EventName", f"Round {round_number}"))
    location = str(_safe_value(row, "Location", "unknown"))
    race_time = _race_datetime(row)
    date = race_time.date().isoformat() if race_time else datetime.now(timezone.utc).date().isoformat()
    time = race_time.time().replace(microsecond=0).isoformat() + "Z" if race_time else None
    circuit_id = location.lower().replace(" ", "_").replace("-", "_")
    return RaceResponse(
        race_id=f"{year}-{round_number}",
        round=round_number,
        season=year,
        race_name=event_name,
        circuit_id=circuit_id,
        circuit_name=location,
        date=date,
        time=time,
    )


def _serialize_race(race: Optional[RaceResponse]) -> Optional[dict[str, Any]]:
    if not race:
        return None
    starts_at = _to_utc(f"{race.date}T{(race.time or '23:59:59Z').replace('Z', '+00:00')}")
    return {
        "race_id": race.race_id,
        "round": race.round,
        "season": race.season,
        "race_name": race.race_name,
        "circuit_id": race.circuit_id,
        "circuit_name": race.circuit_name,
        "date": race.date,
        "time": race.time,
        "starts_at": starts_at.isoformat() if starts_at else None,
    }


def _race_start(race: RaceResponse) -> datetime:
    return _to_utc(f"{race.date}T{(race.time or '23:59:59Z').replace('Z', '+00:00')}") or datetime.now(timezone.utc)


def _get_schedule_sync(year: int) -> list[RaceResponse]:
    fastf1 = _fastf1()
    schedule = fastf1.get_event_schedule(year, include_testing=False, backend="fastf1")
    races = [_event_to_race(row, year) for _, row in schedule.iterrows()]
    return [race for race in races if race.round > 0]


async def get_current_schedule(year: Optional[int] = None) -> list[RaceResponse]:
    selected_year = year or datetime.now(timezone.utc).year
    return await asyncio.to_thread(_get_schedule_sync, selected_year)


def _list_value(value: Any, index: int = 0, default: Any = None) -> Any:
    if isinstance(value, (list, tuple)) and value:
        return value[index] if index < len(value) else default
    return value if value is not None else default


def _standings_sync(year: Optional[int]) -> list[DriverStandingResponse]:
    ergast = _ergast()
    season = year or "current"
    response = ergast.get_driver_standings(season=season)
    content = getattr(response, "content", [])
    if not content:
        return []
    standings = content[-1]
    result = []
    for _, row in standings.iterrows():
        constructor_id = _list_value(_safe_value(row, "constructorIds", []), 0, "")
        constructor_name = _list_value(_safe_value(row, "constructorNames", []), 0, "")
        result.append(
            DriverStandingResponse(
                driver_id=str(_safe_value(row, "driverId", "")),
                code=str(_safe_value(row, "driverCode", "")),
                given_name=str(_safe_value(row, "givenName", "")),
                family_name=str(_safe_value(row, "familyName", "")),
                nationality=str(_safe_value(row, "driverNationality", "")),
                date_of_birth=str(_safe_value(row, "dateOfBirth", "")) or None,
                points=float(_safe_value(row, "points", 0) or 0),
                position=int(_safe_value(row, "position", 0) or 0),
                wins=int(_safe_value(row, "wins", 0) or 0),
                constructor_id=str(constructor_id),
                constructor_name=str(constructor_name),
                constructor_color=_team_color(str(constructor_name)),
            )
        )
    return result


async def get_current_driver_standings(year: Optional[int] = None) -> list[DriverStandingResponse]:
    return await asyncio.to_thread(_standings_sync, year)


async def get_race_state(year: Optional[int] = None) -> dict[str, Any]:
    races = await get_current_schedule(year)
    now = datetime.now(timezone.utc)
    previous = next((race for race in reversed(races) if _race_start(race) <= now), None)
    next_race = next((race for race in races if _race_start(race) > now), None)
    active = next(
        (
            race for race in races
            if _race_start(race) <= now <= _race_start(race) + timedelta(hours=SESSION_WINDOW_HOURS)
        ),
        None,
    )

    return {
        "provider": "fastf1",
        "is_live": active is not None,
        "message": "Current race is live." if active else "No current race is happening.",
        "active_race": _serialize_race(active),
        "previous_race": _serialize_race(previous),
        "next_race": _serialize_race(next_race),
    }


def _load_session_sync(year: int, round_number: int, telemetry: bool = False, laps: bool = False, weather: bool = True, messages: bool = True):
    fastf1 = _fastf1()
    session = fastf1.get_session(year, round_number, "R", backend="fastf1")
    session.load(laps=laps, telemetry=telemetry, weather=weather, messages=messages)
    return session


def _normalize_positions(points: list[dict[str, Any]]) -> dict[str, tuple[float, float]]:
    numeric = [point for point in points if _finite_number(point.get("raw_x")) and _finite_number(point.get("raw_y"))]
    if not numeric:
        return {}

    xs = [float(point["raw_x"]) for point in numeric]
    ys = [float(point["raw_y"]) for point in numeric]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    width = max(max_x - min_x, 1)
    height = max(max_y - min_y, 1)
    result = {}
    for point in numeric:
        x = 6 + ((float(point["raw_x"]) - min_x) / width) * 88
        y = 8 + ((float(point["raw_y"]) - min_y) / height) * 84
        result[str(point["driver_number"])] = (round(x, 2), round(y, 2))
    return result


def _team_color(team_name: str) -> str:
    colors = {
        "red bull": "#3671C6",
        "ferrari": "#E8002D",
        "mercedes": "#27F4D2",
        "mclaren": "#FF8000",
        "aston martin": "#229971",
        "alpine": "#FF87BC",
        "williams": "#64C4FF",
        "haas": "#B6BABD",
        "sauber": "#52E252",
        "rb": "#6692FF",
    }
    lowered = team_name.lower()
    for key, color in colors.items():
        if key in lowered:
            return color
    return "#E10600"


def _current_track_sync(year: int, round_number: int) -> dict[str, Any]:
    session = _load_session_sync(year, round_number, telemetry=True, laps=True, weather=True, messages=True)
    results = getattr(session, "results", None)
    raw_points = []

    for number, pos_data in getattr(session, "pos_data", {}).items():
        if pos_data is None or pos_data.empty:
            continue
        latest = pos_data.iloc[-1]
        raw_points.append(
            {
                "driver_number": str(number),
                "raw_x": _safe_value(latest, "X"),
                "raw_y": _safe_value(latest, "Y"),
                "raw_z": _safe_value(latest, "Z"),
            }
        )

    normalized = _normalize_positions(raw_points)
    cars = []
    for index, point in enumerate(raw_points):
        number = str(point["driver_number"])
        result_row = None
        if results is not None and not results.empty:
            try:
                result_row = results[results["DriverNumber"].astype(str) == number].iloc[0]
            except Exception:
                result_row = None
        car_data = getattr(session, "car_data", {}).get(number)
        latest_car = car_data.iloc[-1] if car_data is not None and not car_data.empty else {}
        team_name = str(_safe_value(result_row, "TeamName", "Unknown team")) if result_row is not None else "Unknown team"
        code = str(_safe_value(result_row, "Abbreviation", number)) if result_row is not None else number
        first = str(_safe_value(result_row, "FirstName", "")) if result_row is not None else ""
        last = str(_safe_value(result_row, "LastName", "")) if result_row is not None else ""
        position = int(_safe_value(result_row, "Position", index + 1)) if result_row is not None else index + 1
        x, y = normalized.get(number, (50, 50))
        cars.append(
            {
                "driver_number": number,
                "code": code,
                "name": f"{first} {last}".strip() or code,
                "team_name": team_name,
                "team_color": _team_color(team_name),
                "headshot_url": None,
                "position": position,
                "gap_to_leader": None,
                "interval": None,
                "x": x,
                "y": y,
                "raw_x": point.get("raw_x"),
                "raw_y": point.get("raw_y"),
                "raw_z": point.get("raw_z"),
                "speed": float(_safe_value(latest_car, "Speed", 0) or 0),
                "throttle": float(_safe_value(latest_car, "Throttle", 0) or 0) / 100,
                "brake": float(_safe_value(latest_car, "Brake", 0) or 0),
                "gear": int(_safe_value(latest_car, "nGear", 0) or 0),
                "rpm": int(_safe_value(latest_car, "RPM", 0) or 0),
                "drs": bool(_safe_value(latest_car, "DRS", 0)),
                "last_update": datetime.now(timezone.utc).isoformat(),
            }
        )

    cars.sort(key=lambda item: item["position"])
    weather = None
    if getattr(session, "weather_data", None) is not None and not session.weather_data.empty:
        latest_weather = session.weather_data.iloc[-1]
        weather = {
            "air_temperature": _safe_value(latest_weather, "AirTemp"),
            "track_temperature": _safe_value(latest_weather, "TrackTemp"),
            "humidity": _safe_value(latest_weather, "Humidity"),
            "rainfall": _safe_value(latest_weather, "Rainfall"),
            "wind_speed": _safe_value(latest_weather, "WindSpeed"),
        }

    messages = []
    if getattr(session, "race_control_messages", None) is not None and not session.race_control_messages.empty:
        for _, row in session.race_control_messages.tail(8).iterrows():
            messages.append(
                {
                    "category": str(_safe_value(row, "Category", "INFO")),
                    "flag": _safe_value(row, "Flag", None),
                    "message": str(_safe_value(row, "Message", "Session update")),
                    "date": str(_safe_value(row, "Time", "")),
                }
            )

    return {
        "mode": "fastf1-live",
        "provider": "fastf1",
        "provider_warning": None if cars else "FastF1 session loaded, but no current position packets are available yet.",
        "is_live": True,
        "session": {
            "session_name": getattr(session, "name", "Race"),
            "session_type": "Race",
            "circuit_short_name": getattr(session.event, "get", lambda *_: None)("Location", None) if hasattr(session, "event") else None,
            "location": getattr(session.event, "get", lambda *_: None)("Location", None) if hasattr(session, "event") else None,
            "country_name": getattr(session.event, "get", lambda *_: None)("Country", None) if hasattr(session, "event") else None,
            "date_start": getattr(session, "date", None).isoformat() if getattr(session, "date", None) is not None else None,
            "date_end": None,
        },
        "weather": weather,
        "race_control": messages,
        "cars": cars,
        "refresh_ms": 15000,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


async def get_current_track_payload(year: Optional[int] = None) -> dict[str, Any]:
    state = await get_race_state(year)
    active = state.get("active_race")
    if not active:
        return {
            "mode": "no-live-race",
            "provider": "fastf1",
            "provider_warning": "FastF1 current schedule shows no active race session.",
            "is_live": False,
            "session": {
                "session_name": "No live race",
                "session_type": "Idle",
                "circuit_short_name": state.get("next_race", {}).get("circuit_name") if state.get("next_race") else None,
                "location": state.get("next_race", {}).get("circuit_name") if state.get("next_race") else None,
                "date_start": None,
                "date_end": None,
            },
            "weather": None,
            "race_control": [],
            "cars": [],
            "refresh_ms": 30000,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "race_state": state,
        }
    return await asyncio.to_thread(_current_track_sync, int(active["season"]), int(active["round"]))


def _previous_results_sync(year: int, round_number: int) -> list[dict[str, Any]]:
    session = _load_session_sync(year, round_number, telemetry=False, laps=False, weather=False, messages=False)
    results = getattr(session, "results", None)
    if results is None or results.empty:
        return []

    rows = []
    for _, result in results.iterrows():
        team_name = str(_safe_value(result, "TeamName", ""))
        position = _safe_value(result, "Position", None)
        if not _finite_number(position):
            continue
        rows.append(
            {
                "position": int(float(position)),
                "driver_id": str(_safe_value(result, "DriverId", _safe_value(result, "Abbreviation", ""))).lower(),
                "driver_code": str(_safe_value(result, "Abbreviation", "")),
                "driver_name": f"{_safe_value(result, 'FirstName', '')} {_safe_value(result, 'LastName', '')}".strip(),
                "constructor_id": team_name.lower().replace(" ", "_"),
                "constructor_name": team_name,
                "constructor_color": _team_color(team_name),
                "points": float(_safe_value(result, "Points", 0) or 0),
                "status": str(_safe_value(result, "Status", "Finished")),
                "time": str(_safe_value(result, "Time", _safe_value(result, "Status", ""))),
            }
        )
    return sorted(rows, key=lambda item: item["position"])


async def get_previous_results_payload(year: Optional[int] = None) -> dict[str, Any]:
    state = await get_race_state(year)
    previous = state.get("previous_race")
    results = []
    if previous:
        results = await asyncio.to_thread(_previous_results_sync, int(previous["season"]), int(previous["round"]))
    return {
        "mode": "fastf1",
        "provider": "fastf1",
        "is_live": False,
        "message": "No current race is happening.",
        "previous_race": previous,
        "next_race": state.get("next_race"),
        "results": results,
    }
