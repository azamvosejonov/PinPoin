from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List


class Coordinate(BaseModel):
    latitude: float
    longitude: float


class Entrance(BaseModel):
    id: int
    label: str
    latitude: float
    longitude: float
    domofon_code: Optional[str]
    has_barrier: bool
    validated_count: int
    last_validated_at: Optional[datetime]

    class Config:
        from_attributes = True


class BuildingBase(BaseModel):
    external_id: str
    address: str
    coordinate: Coordinate
    building_type: str = "OTHER"
    difficulty_index: int = 1
    has_lift: bool = False
    requires_chip: bool = False
    entrance_hint: Optional[str] = None


class IndoorPoint(BaseModel):
    x: float
    y: float
    z: Optional[float] = None


class IndoorPOI(BaseModel):
    id: str
    label: str
    position: IndoorPoint
    icon: Optional[str] = None


class IndoorFloor(BaseModel):
    level: int
    name: Optional[str] = None
    height_m: float = 3.0
    outline: List[IndoorPoint] = Field(default_factory=list)
    walkable_mesh: Optional[List[List[IndoorPoint]]] = None
    pois: List[IndoorPOI] = Field(default_factory=list)


class IndoorMapBase(BaseModel):
    anchor: Optional[Coordinate] = None
    anchor_altitude: Optional[float] = None
    floors: List[IndoorFloor] = Field(default_factory=list)
    extras: Optional[dict] = None


class IndoorMapCreate(IndoorMapBase):
    pass


class IndoorPathPoint(BaseModel):
    floor: int
    position: IndoorPoint
    timestamp: int


class IndoorPathCreate(BaseModel):
    courier_id: str
    duration_ms: Optional[int] = None
    points: List[IndoorPathPoint]


class IndoorPathSummary(BaseModel):
    id: int
    courier_id: str
    recorded_at: datetime
    duration_ms: Optional[int]
    points_count: int

    class Config:
        from_attributes = True


class IndoorPathDetail(IndoorPathSummary):
    points: List[IndoorPathPoint]


class IndoorMap(IndoorMapBase):
    id: int
    created_at: datetime
    updated_at: datetime
    recent_paths: List[IndoorPathSummary] = Field(default_factory=list)

    class Config:
        from_attributes = True


class BuildingCreate(BuildingBase):
    entrances: List[Entrance] = Field(default_factory=list)
    indoor_map: Optional[IndoorMapCreate] = None


class Building(BuildingBase):
    id: int
    entrances: List[Entrance] = Field(default_factory=list)
    indoor_map: Optional[IndoorMap] = None
    updated_at: datetime

    class Config:
        from_attributes = True


class TrajectoryPoint(BaseModel):
    latitude: float
    longitude: float
    timestamp: int
    speed: Optional[float]
    bearing: Optional[float]


class TrajectoryCreate(BaseModel):
    courier_id: str
    delivered_at: Optional[int] = None
    points: List[TrajectoryPoint]


class DeliverySession(BaseModel):
    id: int
    order_id: str
    courier_id: str
    building_external_id: str
    start_time: datetime
    end_time: Optional[datetime]
    temperature_model: str
    start_temperature: float
    predicted_temperature: float
    predicted_eta_minutes: int
    transport_mode: Optional[str]

    class Config:
        from_attributes = True


class PredictivePinRequest(BaseModel):
    raw_coordinate: Coordinate
    address_embedding: list[float]
    historical_vector: list[float]


class PredictivePinResponse(BaseModel):
    adjusted_coordinate: Coordinate
    delta_lat: float
    delta_lon: float


class ThermalProjectionRequest(BaseModel):
    initial_temperature: float
    ambient_temperature: float
    insulation_factor: float
    total_minutes: int


class ThermalProjectionResponse(BaseModel):
    current_temperature: float
    predicted_temperature: float
    eta_minutes: int
    risk_level: str


class AlertResponse(BaseModel):
    alerts: list[str]


class SyncResponse(BaseModel):
    status: str = "stored"


class DomofonValidationRequest(BaseModel):
    code: str
    success: bool
