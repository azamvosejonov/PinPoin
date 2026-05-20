from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, EmailStr
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


class VerificationRequest(BaseModel):
    email: EmailStr


class VerificationConfirm(BaseModel):
    token: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LogoutRequest(BaseModel):
    token: str


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


class UserRole(str, Enum):
    admin = "admin"
    merchant_admin = "merchant_admin"
    restaurant_owner = "restaurant_owner"
    restaurant_operator = "restaurant_operator"
    fleet_manager = "fleet_manager"
    support_operator = "support_operator"
    courier = "courier"


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    phone: Optional[str] = None
    role: UserRole = UserRole.courier


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None


class UserRead(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class RestaurantCourierCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    phone: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: Optional[str] = None
    role: Optional[UserRole] = None


class RestaurantBase(BaseModel):
    name: str
    contact_phone: Optional[str] = None
    building_external_id: Optional[str] = None
    opening_time: Optional[str] = None
    closing_time: Optional[str] = None
    is_open: Optional[bool] = None
    delivery_radius_km: Optional[float] = None
    logo_url: Optional[str] = None


class RestaurantCreate(RestaurantBase):
    owner_id: Optional[int] = None


class RestaurantUpdate(BaseModel):
    name: Optional[str] = None
    contact_phone: Optional[str] = None
    building_external_id: Optional[str] = None
    opening_time: Optional[str] = None
    closing_time: Optional[str] = None
    is_open: Optional[bool] = None
    delivery_radius_km: Optional[float] = None
    logo_url: Optional[str] = None


class RestaurantRead(RestaurantBase):
    id: int
    owner_id: int
    building_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaymentMethod(str, Enum):
    cash = "CASH"
    card = "CARD"
    prepaid = "PREPAID"


class OrderStatus(str, Enum):
    pending = "PENDING"
    accepted = "ACCEPTED"
    picked_up = "PICKED_UP"
    delivered = "DELIVERED"
    canceled = "CANCELED"
    delivery_failed = "DELIVERY_FAILED"
    ready_for_pickup = "READY_FOR_PICKUP"
    unassignable = "UNASSIGNABLE"
    returned_to_restaurant = "RETURNED_TO_RESTAURANT"


class OrderItem(BaseModel):
    name: str
    quantity: int = 1
    price: Optional[float] = None


class OrderCreate(BaseModel):
    order_code: str
    restaurant_id: int
    dropoff_address: str
    dropoff_latitude: float
    dropoff_longitude: float
    building_external_id: Optional[str] = None
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    notes: Optional[str] = None
    items: Optional[List[OrderItem]] = None
    preparation_time_minutes: int = 15
    total_amount: Optional[float] = None
    payment_method: Optional[PaymentMethod] = PaymentMethod.cash
    initial_food_temp: Optional[float] = None
    packaging_type: Optional[PackagingType] = PackagingType.standard


class OrderTracking(BaseModel):
    status: OrderStatus
    courier_location: Optional["CourierLocationRead"] = None
    restaurant_name: Optional[str] = None
    delivery_distance_km: Optional[float] = None
    delivery_fee: Optional[float] = None


class OrderAssign(BaseModel):
    courier_id: int


class OrderBatchAssign(BaseModel):
    order_ids: list[int]
    courier_id: int


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class OrderCancel(BaseModel):
    reason: Optional[str] = None


class OrderDeliveryFailed(BaseModel):
    return_reason: str


class OrderDecline(BaseModel):
    reason: Optional[str] = None


class CourierDailySummary(BaseModel):
    date: str
    total_orders: int
    delivered_orders: int
    canceled_orders: int
    total_earnings: Optional[float] = None


class OrderUpdate(BaseModel):
    dropoff_address: Optional[str] = None
    dropoff_latitude: Optional[float] = None
    dropoff_longitude: Optional[float] = None
    building_external_id: Optional[str] = None
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    notes: Optional[str] = None
    items: Optional[List[OrderItem]] = None


class CourierLocationUpdate(BaseModel):
    latitude: float
    longitude: float
    bearing: Optional[float] = None
    speed: Optional[float] = None


class CourierLocationRead(BaseModel):
    courier_id: int
    latitude: float
    longitude: float
    bearing: Optional[float] = None
    speed: Optional[float] = None
    updated_at: datetime


class CourierStatusEnum(str, Enum):
    offline = "offline"
    online = "online"
    busy = "busy"
    on_break = "on_break"


class TransportMode(str, Enum):
    pedestrian = "pedestrian"
    bicycle = "bicycle"
    car = "car"


class PackagingType(str, Enum):
    standard = "standard"
    thermal_bag = "thermal_bag"
    insulated_box = "insulated_box"


class CourierStatusUpdate(BaseModel):
    status: CourierStatusEnum
    transport_mode: Optional[TransportMode] = None


class CourierCashCollect(BaseModel):
    amount: float


class CourierStatusRead(BaseModel):
    courier_id: int
    status: CourierStatusEnum
    transport_mode: Optional[str] = "pedestrian"
    updated_at: datetime
    last_online_at: Optional[datetime] = None
    cash_balance: float


class PaginatedOrders(BaseModel):
    items: List["OrderRead"]
    total: int
    page: int
    per_page: int


class OrderRead(BaseModel):
    id: int
    order_code: str
    tracking_hash: Optional[str]
    status: OrderStatus
    customer_name: Optional[str]
    customer_phone: Optional[str]
    notes: Optional[str]
    items: Optional[List[OrderItem]]
    dropoff_address: str
    dropoff_latitude: float
    dropoff_longitude: float
    restaurant_id: int
    building_id: Optional[int]
    courier_id: Optional[int]
    delivery_distance_km: Optional[float]
    delivery_fee: Optional[float]
    preparation_time_minutes: Optional[int]
    ready_for_pickup_at: Optional[datetime]
    is_urgent: bool
    total_amount: Optional[float]
    payment_method: Optional[PaymentMethod]
    declined_courier_ids: Optional[str]
    compensation_paid: bool
    max_retries: int
    retry_count: int
    initial_food_temp: Optional[float] = None
    packaging_type: Optional[str] = None
    predicted_arrival_temp: Optional[float] = None
    thermal_risk_level: Optional[str] = None
    corrected_latitude: Optional[float] = None
    corrected_longitude: Optional[float] = None
    pin_correction_reason: Optional[str] = None
    created_at: datetime
    accepted_at: Optional[datetime]
    picked_up_at: Optional[datetime]
    delivered_at: Optional[datetime]
    canceled_at: Optional[datetime]

    class Config:
        from_attributes = True


# ── Smart Dispatch ──

class SmartDispatchRequest(BaseModel):
    order_id: int
    max_radius_km: float = 5.0
    prefer_transport: Optional[TransportMode] = None


class SmartDispatchResponse(BaseModel):
    order_id: int
    assigned_courier_id: Optional[int] = None
    courier_name: Optional[str] = None
    transport_mode: Optional[str] = None
    estimated_pickup_minutes: Optional[int] = None
    estimated_delivery_minutes: Optional[int] = None
    predicted_food_temp: Optional[float] = None
    thermal_risk: Optional[str] = None
    message: str = "ok"


# ── Pin Auto-Correction ──

class PinCorrectionRequest(BaseModel):
    order_id: int
    text_address: str
    gps_latitude: float
    gps_longitude: float


class PinCorrectionResponse(BaseModel):
    original_latitude: float
    original_longitude: float
    corrected_latitude: float
    corrected_longitude: float
    correction_distance_meters: float
    source: str  # "geocoding", "historical_cluster", "unchanged"
    confidence: float


# ── Auto-Batching ──

class AutoBatchRequest(BaseModel):
    restaurant_id: int
    max_batch_size: int = 2
    max_detour_km: float = 1.5


class BatchedGroup(BaseModel):
    order_ids: list[int]
    total_distance_km: float
    estimated_time_minutes: int
    predicted_final_temp: Optional[float] = None


class AutoBatchResponse(BaseModel):
    batches: list[BatchedGroup]
    unbatched_order_ids: list[int]


# ── Dashboard Metrics ──

class DashboardMetrics(BaseModel):
    total_orders_today: int
    delivered_today: int
    avg_delivery_time_minutes: Optional[float] = None
    avg_indoor_delay_seconds: Optional[float] = None
    active_couriers: int
    total_revenue_today: Optional[float] = None


class CourierHeatmapPoint(BaseModel):
    courier_id: int
    courier_name: Optional[str] = None
    latitude: float
    longitude: float
    current_food_temp: Optional[float] = None
    status: str
    transport_mode: Optional[str] = None


class LiveHeatmapResponse(BaseModel):
    couriers: list[CourierHeatmapPoint]
    timestamp: datetime


class DeliveryMetricRead(BaseModel):
    id: int
    order_id: int
    courier_id: int
    restaurant_id: int
    total_delivery_seconds: Optional[int] = None
    indoor_delay_seconds: Optional[int] = None
    outdoor_travel_seconds: Optional[int] = None
    distance_km: Optional[float] = None
    final_food_temp: Optional[float] = None
    courier_rating: Optional[float] = None
    transport_mode: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ── WebSocket Events ──

class WSCourierLocationEvent(BaseModel):
    event: str = "courier_location"
    courier_id: int
    latitude: float
    longitude: float
    bearing: Optional[float] = None
    speed: Optional[float] = None
    current_food_temp: Optional[float] = None
    timestamp: datetime


class WSOrderStatusEvent(BaseModel):
    event: str = "order_status"
    order_id: int
    order_code: str
    old_status: str
    new_status: str
    timestamp: datetime
