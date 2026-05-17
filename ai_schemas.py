from pydantic import BaseModel, Field
from typing import List, Optional


class GeocodingRequest(BaseModel):
    address: str


class GeocodingResponse(BaseModel):
    lat: float
    lon: float
    display_name: str


class ThermalPredictionRequest(BaseModel):
    initial_temp: float
    external_temp: float
    insulation_coefficient: float = 0.7
    time_minutes: float


class ThermalPredictionResponse(BaseModel):
    predicted_temp: float
    is_critical: bool
    message: str
    priority: str


class DifficultyTimeRequest(BaseModel):
    floors: int
    has_elevator: bool
    elevator_type: Optional[str] = None


class DifficultyTimeResponse(BaseModel):
    additional_time_seconds: int


class TrajectoryAnalysisRequest(BaseModel):
    vehicle_stops: List[List[float]]
    pedestrian_points: List[List[float]]


class TrajectoryAnalysisResponse(BaseModel):
    entrance_lat: Optional[float]
    entrance_lon: Optional[float]
    confidence: Optional[float]
