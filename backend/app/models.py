"""Pydantic models for API requests and responses"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class HealthCheckResponse(BaseModel):
    """Health check response model"""
    status: str


class PredictRaceWinnerBody(BaseModel):
    """Request body for race winner prediction"""
    circuit_id: str
    season: int
    round: int
    weather_condition: str = "dry"
    safety_car_probability: float = 0.3


class DriverStandingResponse(BaseModel):
    """Driver standing response model"""
    driver_id: str
    code: str
    given_name: str
    family_name: str
    nationality: str
    date_of_birth: Optional[str]
    points: float
    position: int
    wins: int
    constructor_id: Optional[str]
    constructor_name: Optional[str]
    constructor_color: str


class RaceResponse(BaseModel):
    """Race response model"""
    race_id: str
    round: int
    season: int
    race_name: str
    circuit_id: str
    circuit_name: str
    date: str
    time: Optional[str]


class TelemetryResponse(BaseModel):
    """Telemetry response model"""
    driver_id: str
    driver_name: str
    speed: float
    throttle: float
    brake: float
    drs: bool
    gear: int
    lap: int


class PredictionFactor(BaseModel):
    """Prediction factors model"""
    recent_form: float
    circuit_history: float
    qualifying_pace: float
    tyre_management: float
    weather_adaptability: float
    car_performance: float


class PredictionResult(BaseModel):
    """Individual prediction result"""
    driver_id: str
    driver_code: str
    driver_name: str
    constructor_id: str
    constructor_name: str
    constructor_color: str
    win_probability: float
    podium_probability: float
    predicted_position: int
    factors: PredictionFactor


class RaceWinnerPredictionResponse(BaseModel):
    """Race winner prediction response"""
    model_config = {"protected_namespaces": ()}

    circuit_id: str
    race_name: str
    weather_condition: str
    predictions: List[PredictionResult]
    model_confidence: float
    key_insights: List[str]


class SeasonResponse(BaseModel):
    """Season response model"""
    season: int
    url: str
