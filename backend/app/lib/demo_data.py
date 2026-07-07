"""Demo data used when upstream F1 providers are unavailable."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import List, Optional

from app.models import DriverStandingResponse, RaceResponse, SeasonResponse, TelemetryResponse


DEMO_STANDINGS = [
    ("verstappen", "VER", "Max", "Verstappen", "Dutch", 312, 1, 7, "red_bull", "Red Bull Racing", "#3671C6"),
    ("norris", "NOR", "Lando", "Norris", "British", 286, 2, 4, "mclaren", "McLaren", "#FF8000"),
    ("leclerc", "LEC", "Charles", "Leclerc", "Monegasque", 251, 3, 3, "ferrari", "Ferrari", "#E8002D"),
    ("hamilton", "HAM", "Lewis", "Hamilton", "British", 228, 4, 2, "ferrari", "Ferrari", "#E8002D"),
    ("russell", "RUS", "George", "Russell", "British", 204, 5, 1, "mercedes", "Mercedes", "#27F4D2"),
    ("piastri", "PIA", "Oscar", "Piastri", "Australian", 198, 6, 1, "mclaren", "McLaren", "#FF8000"),
    ("alonso", "ALO", "Fernando", "Alonso", "Spanish", 122, 7, 0, "aston_martin", "Aston Martin", "#229971"),
    ("sainz", "SAI", "Carlos", "Sainz", "Spanish", 96, 8, 0, "williams", "Williams", "#64C4FF"),
]


def demo_driver_standings() -> List[DriverStandingResponse]:
    """Return standings-shaped demo data."""
    return [
        DriverStandingResponse(
            driver_id=driver_id,
            code=code,
            given_name=given,
            family_name=family,
            nationality=nationality,
            date_of_birth=None,
            points=float(points),
            position=position,
            wins=wins,
            constructor_id=constructor_id,
            constructor_name=constructor_name,
            constructor_color=color,
        )
        for driver_id, code, given, family, nationality, points, position, wins, constructor_id, constructor_name, color in DEMO_STANDINGS
    ]


def demo_races() -> List[RaceResponse]:
    """Return race calendar demo data around the current date."""
    year = datetime.now(timezone.utc).year
    start = datetime.now(timezone.utc).date() - timedelta(days=21)
    races = [
        ("bahrain", "Bahrain Grand Prix", "bahrain", "Bahrain International Circuit", start),
        ("jeddah", "Saudi Arabian Grand Prix", "jeddah", "Jeddah Corniche Circuit", start + timedelta(days=14)),
        ("melbourne", "Australian Grand Prix", "albert_park", "Albert Park Grand Prix Circuit", start + timedelta(days=28)),
        ("suzuka", "Japanese Grand Prix", "suzuka", "Suzuka Circuit", start + timedelta(days=42)),
        ("monaco", "Monaco Grand Prix", "monaco", "Circuit de Monaco", start + timedelta(days=56)),
        ("silverstone", "British Grand Prix", "silverstone", "Silverstone Circuit", start + timedelta(days=70)),
    ]
    return [
        RaceResponse(
            race_id=race_id,
            round=index,
            season=year,
            race_name=name,
            circuit_id=circuit_id,
            circuit_name=circuit_name,
            date=date.isoformat(),
            time="13:00:00Z",
        )
        for index, (race_id, name, circuit_id, circuit_name, date) in enumerate(races, start=1)
    ]


def demo_seasons() -> List[SeasonResponse]:
    year = datetime.now(timezone.utc).year
    return [
        SeasonResponse(season=season, url=f"https://en.wikipedia.org/wiki/{season}_Formula_One_World_Championship")
        for season in range(year - 4, year + 1)
    ]


def demo_telemetry() -> list[TelemetryResponse]:
    drivers = demo_driver_standings()[:6]
    return [
        TelemetryResponse(
            driver_id=str(number),
            driver_name=f"{driver.given_name} {driver.family_name}",
            speed=268 + index * 9,
            throttle=min(0.96, 0.72 + index * 0.04),
            brake=0.28 if index % 3 == 0 else 0.0,
            drs=index in {1, 3, 5},
            gear=5 + (index % 3),
            lap=18 + index,
        )
        for index, (number, driver) in enumerate(zip([1, 4, 16, 44, 63, 81], drivers))
    ]


def race_start(race: RaceResponse) -> datetime:
    """Return a timezone-aware datetime for a race response."""
    time_part = race.time or "23:59:59Z"
    value = datetime.fromisoformat(f"{race.date}T{time_part.replace('Z', '+00:00')}")
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


def serialize_race(race: Optional[RaceResponse]) -> Optional[dict]:
    if not race:
        return None
    return {
        "race_id": race.race_id,
        "round": race.round,
        "season": race.season,
        "race_name": race.race_name,
        "circuit_id": race.circuit_id,
        "circuit_name": race.circuit_name,
        "date": race.date,
        "time": race.time,
        "starts_at": race_start(race).isoformat(),
    }


def demo_previous_race_summary() -> dict:
    """Return previous race results and next race countdown metadata."""
    races = sorted(demo_races(), key=race_start)
    now = datetime.now(timezone.utc)
    previous = next((race for race in reversed(races) if race_start(race) < now), races[0])
    next_race = next((race for race in races if race_start(race) > now), races[-1])
    standings = demo_driver_standings()
    intervals = ["1:32:18.742", "+4.381", "+8.902", "+13.457", "+19.224", "+25.810", "+38.611", "+44.205"]

    return {
        "mode": "demo",
        "is_live": False,
        "message": "No current race is happening.",
        "previous_race": serialize_race(previous),
        "next_race": serialize_race(next_race),
        "results": [
            {
                "position": driver.position,
                "driver_id": driver.driver_id,
                "driver_code": driver.code,
                "driver_name": f"{driver.given_name} {driver.family_name}",
                "constructor_id": driver.constructor_id,
                "constructor_name": driver.constructor_name,
                "constructor_color": driver.constructor_color,
                "points": max(0, 26 - (index * 3)),
                "status": "Finished",
                "time": intervals[index] if index < len(intervals) else f"+{index * 8.4:.3f}",
            }
            for index, driver in enumerate(standings)
        ],
    }
