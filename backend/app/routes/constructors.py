"""Constructor specs and car-development tracker endpoints."""
import logging
from typing import Any

from fastapi import APIRouter, Query

from app.lib.fastf1_provider import FastF1Unavailable, get_current_driver_standings

logger = logging.getLogger(__name__)
router = APIRouter()


TECH_PROFILES = {
    "red_bull": {
        "aero_focus": "high-efficiency floor and rear-end stability",
        "strength": "traction, high-speed balance, tyre life",
        "risk": "set-up sensitivity on kerbs",
    },
    "ferrari": {
        "aero_focus": "front-end response and straight-line efficiency",
        "strength": "qualifying pace and traction zones",
        "risk": "race stint thermal management",
    },
    "mercedes": {
        "aero_focus": "platform control and low-drag rear wing options",
        "strength": "race execution and tyre warm-up windows",
        "risk": "balance shift across wind conditions",
    },
    "mclaren": {
        "aero_focus": "efficient floor loading and medium-speed rotation",
        "strength": "race pace and tyre degradation control",
        "risk": "low-speed traction variance",
    },
    "aston_martin": {
        "aero_focus": "sidepod airflow conditioning and rear grip",
        "strength": "mixed-corner consistency",
        "risk": "straight-line drag trade-off",
    },
    "alpine": {
        "aero_focus": "cooling packaging and top-speed recovery",
        "strength": "technical-circuit agility",
        "risk": "race pace volatility",
    },
    "williams": {
        "aero_focus": "low-drag efficiency and brake stability",
        "strength": "straight-line speed",
        "risk": "high-downforce performance",
    },
    "rb": {
        "aero_focus": "stable platform and compact rear bodywork",
        "strength": "development flexibility",
        "risk": "balance consistency",
    },
    "kick_sauber": {
        "aero_focus": "floor sealing and cooling efficiency",
        "strength": "low-drag circuits",
        "risk": "overall load deficit",
    },
    "haas": {
        "aero_focus": "front wing balance and tyre usage",
        "strength": "qualifying windows",
        "risk": "long-run degradation",
    },
}

GENERIC_PROFILE = {
    "aero_focus": "balanced aerodynamic platform",
    "strength": "race-specific setup flexibility",
    "risk": "development correlation",
}

UPGRADE_LIBRARY = [
    {
        "race": "Launch spec",
        "area": "Front wing",
        "version": "Base",
        "impact": "Baseline balance map for low, medium, and high-speed corners.",
    },
    {
        "race": "Early season",
        "area": "Floor edge",
        "version": "Update 1",
        "impact": "Improves floor sealing and low-speed rear stability.",
    },
    {
        "race": "European swing",
        "area": "Sidepod bodywork",
        "version": "Update 2",
        "impact": "Refines cooling exits and airflow to the beam wing.",
    },
    {
        "race": "High-speed package",
        "area": "Rear wing",
        "version": "Update 3",
        "impact": "Reduces drag while preserving DRS delta on long straights.",
    },
    {
        "race": "Late season",
        "area": "Diffuser",
        "version": "Update 4",
        "impact": "Adds rear load consistency for tyre management.",
    },
]

@router.get("/constructors/specs")
async def get_constructor_specs(season: str = Query("current")) -> list[dict[str, Any]]:
    """Return constructor profile cards and car-development entries."""
    try:
        year = None if season == "current" else int(season)
        standings = await get_current_driver_standings(year)
    except FastF1Unavailable as exc:
        logger.warning("FastF1 unavailable for constructor specs: %s", exc)
        return []
    except Exception as exc:
        logger.warning("Could not fetch FastF1 constructor specs: %s", exc)
        return []

    constructors: dict[str, dict[str, Any]] = {}
    for driver in standings:
        constructor_id = driver.constructor_id
        if not constructor_id:
            continue
        entry = constructors.setdefault(
            constructor_id,
            {
                "constructor_id": constructor_id,
                "name": driver.constructor_name or constructor_id.replace("_", " ").title(),
                "color": driver.constructor_color,
                "drivers": [],
                "points": 0.0,
                "wins": 0,
                "mode": "fastf1",
            },
        )
        entry["drivers"].append(driver.code)
        entry["points"] += float(driver.points or 0)
        entry["wins"] += int(driver.wins or 0)

    response = []
    for constructor_id, constructor in constructors.items():
        profile = TECH_PROFILES.get(constructor_id, GENERIC_PROFILE)
        response.append(
            {
                **constructor,
                "power_unit": "Current Formula 1 hybrid turbo power-unit package",
                "chassis": "Carbon-fibre monocoque with ground-effect aerodynamic platform",
                "tyres": "Pirelli slick/intermediate/wet race compounds",
                "brakes": "Carbon-carbon discs with brake-by-wire rear control",
                "aero_focus": profile["aero_focus"],
                "strength": profile["strength"],
                "risk": profile["risk"],
                "upgrade_timeline": UPGRADE_LIBRARY,
            }
        )

    return sorted(response, key=lambda item: item["points"], reverse=True)
