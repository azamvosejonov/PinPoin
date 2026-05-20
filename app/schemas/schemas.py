from pydantic import BaseModel, EmailStr
from typing import Optional, List, Any
from app.models.user import UserRole
from app.models.order import OrderStatus

# ── Auth ──────────────────────────────────────────────
class UserRegister(BaseModel):
    full_name: str
    phone: str
    email: Optional[EmailStr] = None
    password: str
    role: UserRole

class UserLogin(BaseModel):
    phone: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserOut(BaseModel):
    id: int
    full_name: str
    phone: str
    role: UserRole
    is_active: bool
    model_config = {"from_attributes": True}

# ── Restaurant ────────────────────────────────────────
class RestaurantCreate(BaseModel):
    name: str
    address: str
    lat: float
    lon: float
    phone: Optional[str] = None
    open_time: str = "09:00"
    close_time: str = "23:00"
    delivery_fee: float = 0.0
    min_order_price: float = 0.0

class RestaurantOut(RestaurantCreate):
    id: int
    owner_id: int
    model_config = {"from_attributes": True}

class MenuItemCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    calories: Optional[float] = None
    temperature_sensitive: bool = False

class MenuItemOut(MenuItemCreate):
    id: int
    restaurant_id: int
    model_config = {"from_attributes": True}

# ── Order ─────────────────────────────────────────────
class OrderItemIn(BaseModel):
    menu_item_id: int
    quantity: int

class OrderCreate(BaseModel):
    restaurant_id: int
    delivery_address: str
    delivery_lat: float
    delivery_lon: float
    building_id: Optional[int] = None
    apartment_number: Optional[str] = None
    floor: Optional[int] = None
    items: List[OrderItemIn]

class OrderOut(BaseModel):
    id: int
    status: OrderStatus
    total_price: float
    ai_analysis: Optional[Any] = None
    delivery_address: str
    model_config = {"from_attributes": True}

# ── Building ──────────────────────────────────────────
class BuildingCreate(BaseModel):
    address: str
    lat: float
    lon: float
    total_floors: int
    has_elevator: bool = False
    entrance_code: Optional[str] = None
    floor_map: Optional[Any] = None

class BuildingOut(BuildingCreate):
    id: int
    model_config = {"from_attributes": True}

class ApartmentAccessCreate(BaseModel):
    building_id: int
    apartment_number: str
    floor: int
    door_code: Optional[str] = None
    position: Optional[Any] = None

class ApartmentAccessOut(ApartmentAccessCreate):
    id: int
    customer_id: int
    model_config = {"from_attributes": True}

# ── Courier ───────────────────────────────────────────
class CourierLocationUpdate(BaseModel):
    lat: float
    lon: float

class RouteResponse(BaseModel):
    route: List[dict]
    estimated_minutes: int
    distance_km: float
    navigation_steps: List[str]

# ── Staff (kuryer qo'shish) ───────────────────────────
class StaffCreate(BaseModel):
    full_name: str
    phone: str
    vehicle_type: Optional[str] = "motorcycle"

class StaffOut(BaseModel):
    id: int
    full_name: str
    phone: str
    role: UserRole
    vehicle_type: Optional[str]
    plain_password: str  # faqat yaratilganda bir marta qaytariladi

# ── Admin ─────────────────────────────────────────────
class AdminUserUpdate(BaseModel):
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None

class AdminRestaurantUpdate(BaseModel):
    is_active: Optional[bool] = None
    name: Optional[str] = None
    address: Optional[str] = None

class StatsResponse(BaseModel):
    total_users: int
    total_restaurants: int
    total_orders: int
    total_delivered: int
    total_revenue: float
    orders_by_status: dict
    top_restaurants: List[dict]
    total_tracking_visits: int = 0
    unique_visitors: int = 0
    today_visits: int = 0
