"""Race winner prediction endpoints"""
import asyncio
import logging
from typing import List

from fastapi import APIRouter, HTTPException

from app.lib.demo_data import demo_driver_standings, demo_races
from app.lib.f1_api import fetch_ergast, get_constructor_color
from app.models import (
    PredictRaceWinnerBody,
    PredictionFactor,
    PredictionResult,
    RaceWinnerPredictionResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter()

CIRCUIT_SPECIALIST_BOOST = {
    "monaco": {"leclerc": 0.15, "alonso": 0.1, "hamilton": 0.08},
    "monza": {"leclerc": 0.12, "sainz": 0.08, "norris": 0.06},
    "silverstone": {"hamilton": 0.15, "norris": 0.1, "russell": 0.08},
    "spa": {"verstappen": 0.12, "hamilton": 0.1},
    "suzuka": {"verstappen": 0.12, "alonso": 0.08},
    "interlagos": {"hamilton": 0.1, "alonso": 0.08},
}

WET_SPECIALISTS = {
    "hamilton": 0.15,
    "verstappen": 0.12,
    "alonso": 0.1,
    "sainz": 0.08,
    "norris": 0.08,
}


@router.post("/predictions/winner", response_model=RaceWinnerPredictionResponse)
async def predict_race_winner(body: PredictRaceWinnerBody):
    """Predict race winner from live standings plus latest race-session facts."""
    try:
        standings_data, schedule_data, qualifying_data, results_data = await fetch_race_data(body.season, body.round)
        standings = standings_data.get("MRData", {}).get("StandingsTable", {}).get("StandingsLists", [{}])[0].get("DriverStandings", [])
        if not standings:
            raise HTTPException(status_code=404, detail="No live standings available for this season")

        race = schedule_data.get("MRData", {}).get("RaceTable", {}).get("Races", [{}])[0]
        qualifying_order = build_session_position_map(qualifying_data, "QualifyingResults")
        race_result_order = build_session_position_map(results_data, "Results")
        total_points = sum(float(s["points"]) for s in standings) or 1
        field_size = max(len(standings), 1)
        circuit_boosts = CIRCUIT_SPECIALIST_BOOST.get(body.circuit_id, {})

        predictions = [
            calculate_prediction(
                standing=standing,
                field_size=field_size,
                total_points=total_points,
                circuit_boosts=circuit_boosts,
                weather=body.weather_condition,
                safety_car_prob=body.safety_car_probability,
                qualifying_order=qualifying_order,
                race_result_order=race_result_order,
            )
            for standing in standings[:20]
        ]

        predictions.sort(key=lambda x: x["_score"], reverse=True)
        total_score = sum(p["_score"] for p in predictions) or 1

        final_predictions = []
        for i, pred in enumerate(predictions):
            win_prob = round((pred["_score"] / total_score) * 100) / 100
            podium_prob = min(0.99, win_prob * 2.35 + max(0, (3 - i) * 0.045))
            final_predictions.append(
                PredictionResult(
                    driver_id=pred["driver_id"],
                    driver_code=pred["driver_code"],
                    driver_name=pred["driver_name"],
                    constructor_id=pred["constructor_id"],
                    constructor_name=pred["constructor_name"],
                    constructor_color=pred["constructor_color"],
                    win_probability=win_prob,
                    podium_probability=round(podium_prob * 100) / 100,
                    predicted_position=i + 1,
                    factors=pred["factors"],
                )
            )

        confidence = build_confidence(qualifying_order, race_result_order, body.weather_condition)

        return RaceWinnerPredictionResponse(
            circuit_id=body.circuit_id,
            race_name=race.get("raceName", f"Round {body.round}"),
            weather_condition=body.weather_condition,
            predictions=final_predictions,
            model_confidence=confidence,
            key_insights=build_insights(final_predictions, body.weather_condition, body.circuit_id, circuit_boosts, bool(qualifying_order)),
        )
    except HTTPException as exc:
        logger.warning("Live prediction data unavailable, returning demo prediction: %s", exc.detail)
        return build_demo_prediction(body)
    except Exception as exc:
        logger.warning("Error predicting race winner, returning demo prediction: %s", exc)
        return build_demo_prediction(body)


def build_session_position_map(data: dict, key: str) -> dict:
    races = data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
    if not races:
        return {}

    values = races[0].get(key, [])
    result = {}
    for item in values:
        driver_id = item.get("Driver", {}).get("driverId")
        position = item.get("position") or item.get("grid")
        if driver_id and str(position).lstrip("-").isdigit():
            result[driver_id] = max(1, int(position))
    return result


def normalized_position(position: int, field_size: int) -> float:
    return max(0, min(1, 1 - (position - 1) / max(field_size - 1, 1)))


def calculate_prediction(
    standing: dict,
    field_size: int,
    total_points: float,
    circuit_boosts: dict,
    weather: str,
    safety_car_prob: float,
    qualifying_order: dict,
    race_result_order: dict,
) -> dict:
    driver = standing["Driver"]
    constructor = standing.get("Constructors", [{}])[0]
    driver_id = driver["driverId"]
    championship_position = int(standing["position"])
    points = float(standing["points"])

    car_performance = normalized_position(championship_position, field_size)
    recent_form = min(1, (points / total_points) * field_size * 0.45)
    circuit_history = min(1, 0.35 + circuit_boosts.get(driver_id, 0))

    if driver_id in qualifying_order:
        qualifying_pace = normalized_position(qualifying_order[driver_id], field_size)
    else:
        qualifying_pace = max(0.2, car_performance * 0.85)

    if driver_id in race_result_order:
        race_execution = normalized_position(race_result_order[driver_id], field_size)
    else:
        race_execution = (car_performance * 0.65) + (recent_form * 0.35)

    tyre_management = min(1, 0.35 + race_execution * 0.45 + normalized_position(championship_position, field_size) * 0.2)
    weather_adaptability = min(1, 0.48 + WET_SPECIALISTS.get(driver_id, 0) + (0.15 if weather == "dry" else 0))

    base_score = (
        car_performance * 0.28
        + recent_form * 0.22
        + qualifying_pace * 0.18
        + race_execution * 0.14
        + circuit_history * 0.08
        + tyre_management * 0.06
        + weather_adaptability * 0.04
    )
    uncertainty_boost = 1 + min(max(safety_car_prob, 0), 1) * (0.08 if championship_position > 6 else -0.02)
    final_score = max(0.01, base_score * uncertainty_boost)

    return {
        "driver_id": driver_id,
        "driver_code": driver.get("code", driver_id[:3].upper()),
        "driver_name": f"{driver['givenName']} {driver['familyName']}",
        "constructor_id": constructor.get("constructorId", ""),
        "constructor_name": constructor.get("name", ""),
        "constructor_color": get_constructor_color(constructor.get("constructorId")),
        "_score": final_score,
        "factors": PredictionFactor(
            recent_form=round(recent_form * 100) / 100,
            circuit_history=round(circuit_history * 100) / 100,
            qualifying_pace=round(qualifying_pace * 100) / 100,
            tyre_management=round(tyre_management * 100) / 100,
            weather_adaptability=round(weather_adaptability * 100) / 100,
            car_performance=round(car_performance * 100) / 100,
        ),
    }


async def fetch_race_data(season: int, round_num: int):
    async def safe_fetch(path: str):
        try:
            return await fetch_ergast(path)
        except Exception:
            return {}

    return await asyncio.gather(
        fetch_ergast(f"/{season}/driverStandings.json?limit=25"),
        safe_fetch(f"/{season}/{round_num}.json"),
        safe_fetch(f"/{season}/{round_num}/qualifying.json"),
        safe_fetch(f"/{season}/{round_num}/results.json"),
    )


def build_confidence(qualifying_order: dict, race_result_order: dict, weather: str) -> float:
    confidence = 0.68
    if qualifying_order:
        confidence += 0.08
    if race_result_order:
        confidence += 0.06
    if weather in ["wet", "mixed"]:
        confidence -= 0.1
    return round(min(0.88, max(0.52, confidence)) * 100) / 100


def build_insights(
    predictions: List[PredictionResult],
    weather: str,
    circuit_id: str,
    circuit_boosts: dict,
    has_qualifying: bool,
) -> List[str]:
    if not predictions:
        return []

    leader = predictions[0]
    insights = [
        f"{leader.driver_code} leads the model at {round(leader.win_probability * 100)}% using current standings and live race data.",
    ]
    insights.append("Qualifying data is included in the model." if has_qualifying else "Qualifying is not published yet, so championship pace carries more weight.")

    if weather == "wet":
        insights.append("Wet conditions increase variance and lift known wet-weather specialists.")
    elif weather == "mixed":
        insights.append("Mixed conditions lower confidence because strategy timing becomes more decisive.")

    specialist = next((p for p in predictions if p.driver_id in circuit_boosts), None)
    if specialist:
        insights.append(f"{specialist.driver_code} receives a circuit-history boost for {circuit_id}.")

    if len(predictions) > 1 and leader.win_probability - predictions[1].win_probability < 0.05:
        insights.append(f"{leader.driver_code} and {predictions[1].driver_code} are separated by less than five percentage points.")

    return insights


def build_demo_prediction(body: PredictRaceWinnerBody) -> RaceWinnerPredictionResponse:
    standings = demo_driver_standings()
    races = demo_races()
    race = next((item for item in races if item.round == body.round), races[0])
    leader_points = max(float(standings[0].points or 1), 1)
    scores = []

    for index, driver in enumerate(standings[:20]):
        form = max(0.08, float(driver.points or 0) / leader_points)
        weather = 0.72 if body.weather_condition == "dry" else 0.62
        circuit = 0.54 + max(0, 8 - index) * 0.025
        tyre = 0.58 + max(0, 8 - index) * 0.02
        car = max(0.1, 1 - index / max(len(standings) - 1, 1))
        score = form * 0.38 + car * 0.22 + circuit * 0.14 + tyre * 0.12 + weather * 0.08
        scores.append((driver, score, form, circuit, tyre, weather, car))

    total = sum(item[1] for item in scores) or 1
    predictions = []
    for position, (driver, score, form, circuit, tyre, weather, car) in enumerate(scores, start=1):
        win_probability = round((score / total) * 100) / 100
        podium_probability = min(0.95, round((win_probability * 2.2 + max(0, 4 - position) * 0.06) * 100) / 100)
        predictions.append(
            PredictionResult(
                driver_id=driver.driver_id,
                driver_code=driver.code,
                driver_name=f"{driver.given_name} {driver.family_name}",
                constructor_id=driver.constructor_id or "",
                constructor_name=driver.constructor_name or "",
                constructor_color=driver.constructor_color,
                win_probability=win_probability,
                podium_probability=podium_probability,
                predicted_position=position,
                factors=PredictionFactor(
                    recent_form=round(form * 100) / 100,
                    circuit_history=round(circuit * 100) / 100,
                    qualifying_pace=round(car * 0.9 * 100) / 100,
                    tyre_management=round(tyre * 100) / 100,
                    weather_adaptability=round(weather * 100) / 100,
                    car_performance=round(car * 100) / 100,
                ),
            )
        )

    return RaceWinnerPredictionResponse(
        circuit_id=body.circuit_id,
        race_name=race.race_name,
        weather_condition=body.weather_condition,
        predictions=predictions,
        model_confidence=0.58,
        key_insights=[
            "Provider data is unavailable, so RaceIQ is showing a schema-valid demo prediction.",
            "Live mode will blend standings, qualifying, race results, weather, safety-car probability, and circuit history.",
            f"Safety-car probability is set to {round(body.safety_car_probability * 100)}%.",
        ],
    )
