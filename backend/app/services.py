from collections import OrderedDict
from datetime import datetime, timedelta
from threading import Lock
from typing import Sequence, Callable
from math import radians, sin, cos, sqrt, atan2
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update, func
from sqlalchemy.orm import selectinload

from app import models, schemas
import math
from passlib.context import CryptContext
from jose import jwt
from jose.exceptions import JWTError
from fastapi import HTTPException, status
from app.config import get_settings
import secrets
import uuid


_TOKEN_BLACKLIST_CACHE: OrderedDict[str, datetime | None] = OrderedDict()
_TOKEN_BLACKLIST_LOCK = Lock()
_TOKEN_BLACKLIST_MAX_SIZE = 2048


ORDER_STATUS_TRANSITIONS = {
    schemas.OrderStatus.pending.value: {schemas.OrderStatus.ready_for_pickup.value, schemas.OrderStatus.canceled.value, schemas.OrderStatus.unassignable.value},
    schemas.OrderStatus.ready_for_pickup.value: {schemas.OrderStatus.accepted.value, schemas.OrderStatus.canceled.value, schemas.OrderStatus.unassignable.value},
    schemas.OrderStatus.accepted.value: {schemas.OrderStatus.picked_up.value, schemas.OrderStatus.canceled.value},
    schemas.OrderStatus.picked_up.value: {schemas.OrderStatus.delivered.value, schemas.OrderStatus.delivery_failed.value, schemas.OrderStatus.canceled.value},
    schemas.OrderStatus.delivery_failed.value: {schemas.OrderStatus.returned_to_restaurant.value},
    schemas.OrderStatus.returned_to_restaurant.value: set(),
    schemas.OrderStatus.delivered.value: set(),
    schemas.OrderStatus.canceled.value: set(),
    schemas.OrderStatus.unassignable.value: set(),
}


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _prune_blacklist_cache() -> None:
    now = datetime.utcnow()
    expired = [token for token, exp in _TOKEN_BLACKLIST_CACHE.items() if exp and exp < now]
    for token in expired:
        _TOKEN_BLACKLIST_CACHE.pop(token, None)
    while len(_TOKEN_BLACKLIST_CACHE) > _TOKEN_BLACKLIST_MAX_SIZE:
        _TOKEN_BLACKLIST_CACHE.popitem(last=False)


def _token_expiry_hint(token: str) -> datetime | None:
    try:
        claims = jwt.get_unverified_claims(token)
        exp = claims.get("exp")
        if exp:
            return datetime.utcfromtimestamp(exp)
    except Exception:  # pragma: no cover - best effort
        return datetime.utcnow() + timedelta(days=30)
    return None


def _cache_blacklisted_token(token: str, expires_at: datetime | None) -> None:
    with _TOKEN_BLACKLIST_LOCK:
        _prune_blacklist_cache()
        _TOKEN_BLACKLIST_CACHE[token] = expires_at


def _is_token_blacklisted_cached(token: str) -> bool:
    with _TOKEN_BLACKLIST_LOCK:
        _prune_blacklist_cache()
        return token in _TOKEN_BLACKLIST_CACHE


def _generate_tracking_hash() -> str:
    return str(uuid.uuid4())


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    d_lat = radians(lat2 - lat1)
    d_lon = radians(lon2 - lon1)
    a = sin(d_lat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(d_lon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def _calculate_delivery_fee(distance_km: float) -> float:
    base_fee = 5000.0
    per_km = 1500.0
    return round(base_fee + per_km * distance_km, 2)


_NOTIFICATION_SUBSCRIBERS: dict[str, list[Callable]] = {}
_NOTIFICATION_LOCK = Lock()


def subscribe_to_notifications(courier_id: int, callback: Callable) -> None:
    with _NOTIFICATION_LOCK:
        key = f"courier_{courier_id}"
        if key not in _NOTIFICATION_SUBSCRIBERS:
            _NOTIFICATION_SUBSCRIBERS[key] = []
        _NOTIFICATION_SUBSCRIBERS[key].append(callback)


def unsubscribe_from_notifications(courier_id: int, callback: Callable) -> None:
    with _NOTIFICATION_LOCK:
        key = f"courier_{courier_id}"
        if key in _NOTIFICATION_SUBSCRIBERS:
            if callback in _NOTIFICATION_SUBSCRIBERS[key]:
                _NOTIFICATION_SUBSCRIBERS[key].remove(callback)


async def notify_courier(courier_id: int, event_type: str, data: dict) -> None:
    key = f"courier_{courier_id}"
    with _NOTIFICATION_LOCK:
        callbacks = _NOTIFICATION_SUBSCRIBERS.get(key, []).copy()
    
    for callback in callbacks:
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(event_type, data)
            else:
                callback(event_type, data)
        except Exception:
            pass


async def log_order_status_change(
    db: AsyncSession,
    order_id: int,
    old_status: str | None,
    new_status: str,
    changed_by_user_id: int | None,
) -> None:
    log_entry = models.OrderStatusLog(
        order_id=order_id,
        old_status=old_status,
        new_status=new_status,
        changed_by_user_id=changed_by_user_id,
    )
    db.add(log_entry)
    await db.commit()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(subject: str, role: str) -> str:
    settings = get_settings()
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode = {"sub": subject, "role": role, "exp": expire}
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(subject: str, role: str) -> str:
    settings = get_settings()
    expire = datetime.utcnow() + timedelta(days=30)
    to_encode = {"sub": subject, "role": role, "exp": expire, "type": "refresh"}
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> schemas.TokenPayload:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        return schemas.TokenPayload(sub=payload.get("sub"), role=payload.get("role"))
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc


def decode_refresh_token(token: str) -> schemas.TokenPayload:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not a refresh token")
        return schemas.TokenPayload(sub=payload.get("sub"), role=payload.get("role"))
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token") from exc


async def is_token_blacklisted(db: AsyncSession, token: str) -> bool:
    if _is_token_blacklisted_cached(token):
        return True

    result = await db.execute(select(models.TokenBlacklist).where(models.TokenBlacklist.token == token))
    record = result.scalar_one_or_none()
    if record:
        _cache_blacklisted_token(token, _token_expiry_hint(token))
        return True
    return False


async def blacklist_token(db: AsyncSession, token: str) -> None:
    db.add(models.TokenBlacklist(token=token))
    await db.commit()
    _cache_blacklisted_token(token, _token_expiry_hint(token))


def generate_user_token(purpose: str, minutes: int) -> tuple[str, datetime]:
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(minutes=minutes)
    return token, expires_at


def compute_building_difficulty(building: models.Building) -> int:
    if building.building_type == "HRUSHCHEV":
        floors = 5
        score = min(5, max(1, floors * 15 // 60))
        return score
    if building.building_type == "NEW_TOWER":
        score = 2
        if building.requires_chip:
            score += 2
        if building.has_lift:
            score += 1
        else:
            score += 2
        return min(score, 5)
    return 2


def identify_entrance_point(trajectories: Sequence[models.Trajectory]) -> tuple[float, float] | None:
    points = [p for traj in trajectories for p in traj.points]
    if not points:
        return None
    precision = 0.0001
    buckets: dict[tuple[int, int], list[dict]] = {}
    for pt in points:
        key = (int(pt["latitude"] / precision), int(pt["longitude"] / precision))
        buckets.setdefault(key, []).append(pt)
    cluster = max(buckets.values(), key=len)
    avg_lat = sum(p["latitude"] for p in cluster) / len(cluster)
    avg_lon = sum(p["longitude"] for p in cluster) / len(cluster)
    return avg_lat, avg_lon


def heuristic_predictive_pin(request: schemas.PredictivePinRequest) -> schemas.PredictivePinResponse:
    values = request.address_embedding + request.historical_vector
    if not values:
        return schemas.PredictivePinResponse(
            adjusted_coordinate=request.raw_coordinate,
            delta_lat=0.0,
            delta_lon=0.0,
        )
    hash_sum = sum(values) + request.raw_coordinate.latitude + request.raw_coordinate.longitude
    angle = hash_sum % (2 * math.pi)
    magnitude = (len(values) / 64.0) * 0.0002
    delta_lat = magnitude * math.sin(angle)
    delta_lon = magnitude * math.cos(angle)
    return schemas.PredictivePinResponse(
        adjusted_coordinate=schemas.Coordinate(
            latitude=request.raw_coordinate.latitude + delta_lat,
            longitude=request.raw_coordinate.longitude + delta_lon,
        ),
        delta_lat=delta_lat,
        delta_lon=delta_lon,
    )


def compute_thermal_projection(request: schemas.ThermalProjectionRequest) -> schemas.ThermalProjectionResponse:
    decay_constant = max(0.1, min(0.9, 1 - request.insulation_factor))
    predicted_temperature = request.ambient_temperature + (
        request.initial_temperature - request.ambient_temperature
    ) * math.exp(-decay_constant * request.total_minutes / 10)
    if predicted_temperature >= 60:
        risk = "LOW"
    elif predicted_temperature >= 45:
        risk = "MEDIUM"
    else:
        risk = "HIGH"
    return schemas.ThermalProjectionResponse(
        current_temperature=request.initial_temperature,
        predicted_temperature=predicted_temperature,
        eta_minutes=request.total_minutes,
        risk_level=risk,
    )


async def get_building_by_external_id(db: AsyncSession, external_id: str) -> models.Building | None:
    result = await db.execute(
        select(models.Building)
        .options(
            selectinload(models.Building.entrances),
            selectinload(models.Building.indoor_map).selectinload(models.IndoorMap.paths),
        )
        .where(models.Building.external_id == external_id)
    )
    return result.scalar_one_or_none()


async def save_building(db: AsyncSession, payload: schemas.BuildingCreate) -> models.Building:
    existing = await db.execute(
        select(models.Building.id).where(models.Building.external_id == payload.external_id)
    )
    existing_id = existing.scalar_one_or_none()
    timestamp = datetime.utcnow()

    if existing_id is not None:
        await db.execute(
            update(models.Building)
            .where(models.Building.id == existing_id)
            .values(
                address=payload.address,
                latitude=payload.coordinate.latitude,
                longitude=payload.coordinate.longitude,
                building_type=payload.building_type,
                difficulty_index=payload.difficulty_index,
                has_lift=payload.has_lift,
                requires_chip=payload.requires_chip,
                entrance_hint=payload.entrance_hint,
                updated_at=timestamp,
            )
        )
        building_id = existing_id
        await db.execute(delete(models.Entrance).where(models.Entrance.building_id == building_id))
    else:
        building = models.Building(
            external_id=payload.external_id,
            address=payload.address,
            latitude=payload.coordinate.latitude,
            longitude=payload.coordinate.longitude,
            building_type=payload.building_type,
            difficulty_index=payload.difficulty_index,
            has_lift=payload.has_lift,
            requires_chip=payload.requires_chip,
            entrance_hint=payload.entrance_hint,
            updated_at=timestamp,
        )
        db.add(building)
        await db.flush()
        building_id = building.id

    for entrance in payload.entrances:
        db.add(
            models.Entrance(
                building_id=building_id,
                label=entrance.label,
                latitude=entrance.latitude,
                longitude=entrance.longitude,
                domofon_code=entrance.domofon_code,
                has_barrier=entrance.has_barrier,
                validated_count=entrance.validated_count,
                last_validated_at=entrance.last_validated_at,
            )
        )

    await db.commit()

    if payload.indoor_map:
        await upsert_indoor_map(db, building_id, payload.indoor_map)

    refreshed = await db.execute(
        select(models.Building)
        .options(
            selectinload(models.Building.entrances),
            selectinload(models.Building.indoor_map).selectinload(models.IndoorMap.paths),
        )
        .where(models.Building.id == building_id)
    )
    return refreshed.scalar_one()


def building_to_schema(building: models.Building) -> schemas.Building:
    indoor_map = None
    if building.indoor_map:
        indoor_map = indoor_map_to_schema(building.indoor_map)
    return schemas.Building(
        id=building.id,
        external_id=building.external_id,
        address=building.address,
        coordinate=schemas.Coordinate(latitude=building.latitude, longitude=building.longitude),
        building_type=building.building_type,
        difficulty_index=building.difficulty_index,
        has_lift=building.has_lift,
        requires_chip=building.requires_chip,
        entrance_hint=building.entrance_hint,
        entrances=[
            schemas.Entrance(
                id=entrance.id,
                label=entrance.label,
                latitude=entrance.latitude,
                longitude=entrance.longitude,
                domofon_code=entrance.domofon_code,
                has_barrier=entrance.has_barrier,
                validated_count=entrance.validated_count,
                last_validated_at=entrance.last_validated_at,
            )
            for entrance in building.entrances
        ],
        indoor_map=indoor_map,
        updated_at=building.updated_at,
    )


def indoor_map_to_schema(indoor_map: models.IndoorMap) -> schemas.IndoorMap:
    anchor = None
    if indoor_map.anchor_latitude is not None and indoor_map.anchor_longitude is not None:
        anchor = schemas.Coordinate(
            latitude=indoor_map.anchor_latitude,
            longitude=indoor_map.anchor_longitude,
        )
    floors = [schemas.IndoorFloor.model_validate(floor) for floor in indoor_map.floors]
    recent_paths = sorted(indoor_map.paths, key=lambda p: p.recorded_at, reverse=True)[:5]
    return schemas.IndoorMap(
        id=indoor_map.id,
        anchor=anchor,
        anchor_altitude=indoor_map.anchor_altitude,
        floors=floors,
        extras=indoor_map.extras,
        created_at=indoor_map.created_at,
        updated_at=indoor_map.updated_at,
        recent_paths=[indoor_path_to_summary(path) for path in recent_paths],
    )


def indoor_path_to_summary(path: models.IndoorPath) -> schemas.IndoorPathSummary:
    return schemas.IndoorPathSummary(
        id=path.id,
        courier_id=path.courier_id,
        recorded_at=path.recorded_at,
        duration_ms=path.duration_ms,
        points_count=len(path.path or []),
    )


def indoor_path_to_detail(path: models.IndoorPath) -> schemas.IndoorPathDetail:
    return schemas.IndoorPathDetail(
        id=path.id,
        courier_id=path.courier_id,
        recorded_at=path.recorded_at,
        duration_ms=path.duration_ms,
        points_count=len(path.path or []),
        points=[
            schemas.IndoorPathPoint(
                floor=point["floor"],
                position=schemas.IndoorPoint(**point["position"]),
                timestamp=point["timestamp"],
            )
            for point in (path.path or [])
        ],
    )


async def upsert_indoor_map(db: AsyncSession, building_id: int, payload: schemas.IndoorMapCreate) -> models.IndoorMap:
    result = await db.execute(select(models.IndoorMap).where(models.IndoorMap.building_id == building_id))
    indoor_map = result.scalar_one_or_none()

    anchor_lat = payload.anchor.latitude if payload.anchor else None
    anchor_lon = payload.anchor.longitude if payload.anchor else None
    floors_json = [floor.model_dump(mode="json") for floor in payload.floors]

    if indoor_map:
        indoor_map.anchor_latitude = anchor_lat
        indoor_map.anchor_longitude = anchor_lon
        indoor_map.anchor_altitude = payload.anchor_altitude
        indoor_map.floors = floors_json
        indoor_map.extras = payload.extras
    else:
        indoor_map = models.IndoorMap(
            building_id=building_id,
            anchor_latitude=anchor_lat,
            anchor_longitude=anchor_lon,
            anchor_altitude=payload.anchor_altitude,
            floors=floors_json,
            extras=payload.extras,
        )
        db.add(indoor_map)

    await db.commit()
    await db.refresh(indoor_map)
    return indoor_map


async def record_indoor_path(db: AsyncSession, building_id: int, payload: schemas.IndoorPathCreate) -> models.IndoorPath:
    result = await db.execute(select(models.IndoorMap).where(models.IndoorMap.building_id == building_id))
    indoor_map = result.scalar_one_or_none()
    if not indoor_map:
        raise ValueError("Indoor map not defined for building")

    path_json = [
        {
            "floor": point.floor,
            "position": point.position.model_dump(mode="json"),
            "timestamp": point.timestamp,
        }
        for point in payload.points
    ]

    indoor_path = models.IndoorPath(
        indoor_map_id=indoor_map.id,
        courier_id=payload.courier_id,
        duration_ms=payload.duration_ms,
        path=path_json,
    )
    db.add(indoor_path)
    await db.commit()
    await db.refresh(indoor_path)
    return indoor_path


async def get_indoor_map(db: AsyncSession, building_id: int) -> models.IndoorMap | None:
    result = await db.execute(
        select(models.IndoorMap)
        .options(selectinload(models.IndoorMap.paths))
        .where(models.IndoorMap.building_id == building_id)
    )
    return result.scalar_one_or_none()


async def get_indoor_path(db: AsyncSession, path_id: int) -> models.IndoorPath | None:
    result = await db.execute(select(models.IndoorPath).where(models.IndoorPath.id == path_id))
    return result.scalar_one_or_none()


async def record_trajectory(
    db: AsyncSession,
    building: models.Building,
    courier_id: str,
    points: list[dict],
    delivered_at: datetime | None = None,
) -> models.Trajectory:
    trajectory = models.Trajectory(
        building_id=building.id,
        courier_id=courier_id,
        points=points,
        delivered_at=delivered_at or datetime.utcnow()
    )
    db.add(trajectory)
    await db.commit()
    await db.refresh(trajectory)
    return trajectory


async def update_domofon_code(db: AsyncSession, entrance_id: int, code: str, is_success: bool) -> models.Entrance:
    result = await db.execute(select(models.Entrance).where(models.Entrance.id == entrance_id))
    entrance = result.scalar_one()
    if is_success:
        entrance.domofon_code = code
        entrance.validated_count += 1
        entrance.last_validated_at = datetime.utcnow()
    else:
        entrance.validated_count = max(0, entrance.validated_count - 1)
    await db.commit()
    await db.refresh(entrance)
    return entrance


async def create_user(db: AsyncSession, payload: schemas.UserCreate, *, auto_activate: bool = False) -> models.User:
    result = await db.execute(select(models.User).where(models.User.email == payload.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    if payload.role == schemas.UserRole.admin and not auto_activate:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role requires approval")

    is_active = auto_activate
    if payload.role == schemas.UserRole.admin:
        is_active = True

    user = models.User(
        email=payload.email.lower(),
        full_name=payload.full_name,
        phone=payload.phone,
        role=payload.role.value,
        password_hash=hash_password(payload.password),
        is_active=is_active,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> models.User:
    result = await db.execute(select(models.User).where(models.User.email == email.lower()))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User disabled")
    return user


async def list_pending_users(db: AsyncSession) -> list[models.User]:
    result = await db.execute(select(models.User).where(models.User.is_active.is_(False)))
    return result.scalars().all()


async def set_user_active(db: AsyncSession, user_id: int, is_active: bool) -> models.User:
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.is_active = is_active
    user.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user_id: int) -> None:
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    await db.delete(user)
    await db.commit()


async def get_user_by_id(db: AsyncSession, user_id: int) -> models.User | None:
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> models.User | None:
    result = await db.execute(select(models.User).where(models.User.email == email.lower()))
    return result.scalar_one_or_none()


async def create_user_token(db: AsyncSession, user: models.User, purpose: str, minutes: int) -> models.UserToken:
    token_str, expires_at = generate_user_token(purpose, minutes)
    user_token = models.UserToken(user_id=user.id, token=token_str, purpose=purpose, expires_at=expires_at)
    db.add(user_token)
    await db.commit()
    await db.refresh(user_token)
    return user_token


async def consume_user_token(db: AsyncSession, token: str, purpose: str) -> models.UserToken:
    result = await db.execute(select(models.UserToken).where(models.UserToken.token == token))
    user_token = result.scalar_one_or_none()
    if not user_token or user_token.purpose != purpose:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")
    if user_token.consumed_at or user_token.expires_at < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token expired")

    user_token.consumed_at = datetime.utcnow()
    await db.commit()
    await db.refresh(user_token)
    return user_token


async def create_restaurant(db: AsyncSession, payload: schemas.RestaurantCreate) -> models.Restaurant:
    building_id = None
    if payload.building_external_id:
        building = await get_building_by_external_id(db, payload.building_external_id)
        if building:
            building_id = building.id

    restaurant = models.Restaurant(
        name=payload.name,
        contact_phone=payload.contact_phone,
        owner_id=payload.owner_id,
        building_id=building_id,
        opening_time=payload.opening_time,
        closing_time=payload.closing_time,
        is_open=payload.is_open if payload.is_open is not None else True,
        delivery_radius_km=payload.delivery_radius_km if payload.delivery_radius_km is not None else 10.0,
        logo_url=payload.logo_url,
    )
    db.add(restaurant)
    await db.commit()
    await db.refresh(restaurant)
    return restaurant


async def list_restaurants(db: AsyncSession) -> list[models.Restaurant]:
    result = await db.execute(select(models.Restaurant))
    return result.scalars().all()


async def create_order(db: AsyncSession, payload: schemas.OrderCreate) -> models.Order:
    building_id = None
    if payload.building_external_id:
        building = await get_building_by_external_id(db, payload.building_external_id)
        if building:
            building_id = building.id

    restaurant = await get_restaurant_by_id(db, payload.restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")
    
    if not restaurant.is_open:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Restaurant is currently closed")

    distance_km = None
    fee = None
    if restaurant.building and restaurant.building.latitude and restaurant.building.longitude:
        distance_km = _haversine_km(
            restaurant.building.latitude,
            restaurant.building.longitude,
            payload.dropoff_latitude,
            payload.dropoff_longitude,
        )
        
        if restaurant.delivery_radius_km and distance_km > restaurant.delivery_radius_km:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Delivery location is outside restaurant's delivery radius ({restaurant.delivery_radius_km} km)",
            )
        
        fee = _calculate_delivery_fee(distance_km)

    order = models.Order(
        order_code=payload.order_code,
        restaurant_id=payload.restaurant_id,
        dropoff_address=payload.dropoff_address,
        dropoff_latitude=payload.dropoff_latitude,
        dropoff_longitude=payload.dropoff_longitude,
        building_id=building_id,
        customer_name=payload.customer_name,
        customer_phone=payload.customer_phone,
        notes=payload.notes,
        items=[item.model_dump() for item in payload.items] if payload.items else None,
        tracking_hash=_generate_tracking_hash(),
        delivery_distance_km=distance_km,
        delivery_fee=fee,
        preparation_time_minutes=payload.preparation_time_minutes,
        total_amount=payload.total_amount,
        payment_method=payload.payment_method.value if payload.payment_method else None,
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)
    return order


async def assign_order(db: AsyncSession, order_id: int, courier_id: int) -> models.Order:
    result = await db.execute(select(models.Order).where(models.Order.id == order_id).with_for_update())
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if order.status != schemas.OrderStatus.pending.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order is not pending")
    if order.courier_id is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Order already assigned")
    
    courier = await get_user_by_id(db, courier_id)
    if not courier or courier.role != schemas.UserRole.courier.value:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Courier not found")
    if not courier.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Courier is disabled")
    
    courier_status_result = await db.execute(
        select(models.CourierStatus).where(models.CourierStatus.courier_id == courier_id).with_for_update()
    )
    courier_status = courier_status_result.scalar_one_or_none()
    if not courier_status or courier_status.status != schemas.CourierStatusEnum.online.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Courier is not online")

    order.courier_id = courier_id
    order.status = schemas.OrderStatus.accepted.value
    order.accepted_at = datetime.utcnow()
    await db.commit()
    await db.refresh(order)
    
    await notify_courier(courier_id, "order_assigned", {"order_id": order.id, "order_code": order.order_code})
    
    await _update_courier_busy_status(db, courier_id)
    
    return order


async def _update_courier_busy_status(db: AsyncSession, courier_id: int) -> None:
    result = await db.execute(
        select(models.Order)
        .where(
            models.Order.courier_id == courier_id,
            models.Order.status.in_([
                schemas.OrderStatus.accepted.value,
                schemas.OrderStatus.ready_for_pickup.value,
                schemas.OrderStatus.picked_up.value,
            ])
        )
    )
    active_orders = result.scalars().all()
    
    has_active_orders = len(active_orders) > 0
    
    courier_status_result = await db.execute(
        select(models.CourierStatus).where(models.CourierStatus.courier_id == courier_id).with_for_update()
    )
    courier_status = courier_status_result.scalar_one_or_none()
    if courier_status:
        if has_active_orders and courier_status.status == schemas.CourierStatusEnum.online.value:
            courier_status.status = schemas.CourierStatusEnum.busy.value
        elif not has_active_orders and courier_status.status == schemas.CourierStatusEnum.busy.value:
            courier_status.status = schemas.CourierStatusEnum.online.value
        courier_status.updated_at = datetime.utcnow()
        await db.commit()
    
    return None


async def find_nearest_couriers(db: AsyncSession, restaurant_id: int, radius_km: float = 3.0, limit: int = 3, order_id: int | None = None) -> list[models.User]:
    restaurant = await get_restaurant_by_id(db, restaurant_id)
    if not restaurant or not restaurant.building:
        return []
    
    if not restaurant.building.latitude or not restaurant.building.longitude:
        return []
    
    result = await db.execute(
        select(models.User)
        .options(selectinload(models.User.courier_status))
        .where(
            models.User.role == schemas.UserRole.courier.value,
            models.User.is_active == True,
        )
    )
    couriers = result.scalars().all()
    
    declined_courier_ids = []
    if order_id:
        order_result = await db.execute(select(models.Order).where(models.Order.id == order_id))
        order = order_result.scalar_one_or_none()
        if order and order.declined_courier_ids:
            declined_courier_ids = [int(cid) for cid in order.declined_courier_ids.split(",") if cid]
    
    courier_distances = []
    now = datetime.utcnow()
    stale_threshold_minutes = 5
    
    for courier in couriers:
        if courier.id in declined_courier_ids:
            continue
        
        if not courier.courier_status or courier.courier_status.status not in (schemas.CourierStatusEnum.online.value, schemas.CourierStatusEnum.busy.value):
            continue
        
        courier_location = await get_courier_location(db, courier.id)
        if not courier_location:
            continue
        
        if (now - courier_location.updated_at).total_seconds() > stale_threshold_minutes * 60:
            continue
        
        distance = _haversine_km(
            restaurant.building.latitude,
            restaurant.building.longitude,
            courier_location.latitude,
            courier_location.longitude,
        )
        
        if distance <= radius_km:
            courier_distances.append((courier, distance))
    
    courier_distances.sort(key=lambda x: x[1])
    return [c[0] for c in courier_distances[:limit]]


async def auto_assign_order(db: AsyncSession, order_id: int) -> models.Order | None:
    result = await db.execute(select(models.Order).where(models.Order.id == order_id).with_for_update())
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if order.status != schemas.OrderStatus.ready_for_pickup.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order must be READY_FOR_PICKUP")
    if order.courier_id is not None:
        return order
    
    if order.retry_count >= order.max_retries:
        order.status = schemas.OrderStatus.unassignable.value
        await db.commit()
        await db.refresh(order)
        return order
    
    order.retry_count += 1
    
    nearest_couriers = await find_nearest_couriers(db, order.restaurant_id, order_id=order_id)
    if not nearest_couriers:
        order.status = schemas.OrderStatus.unassignable.value
        await db.commit()
        await db.refresh(order)
        return order
    
    for courier in nearest_couriers:
        try:
            order = await assign_order(db, order_id, courier.id)
            return order
        except HTTPException:
            continue
    
    order.status = schemas.OrderStatus.unassignable.value
    await db.commit()
    await db.refresh(order)
    return order


async def mark_order_ready_for_pickup(db: AsyncSession, order_id: int, changed_by_user_id: int | None = None) -> models.Order:
    result = await db.execute(select(models.Order).where(models.Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if order.status != schemas.OrderStatus.pending.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order must be PENDING")
    
    old_status = order.status
    order.status = schemas.OrderStatus.ready_for_pickup.value
    order.ready_for_pickup_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(order)
    
    await log_order_status_change(db, order_id, old_status, order.status, changed_by_user_id)
    
    return order


async def update_order_details(db: AsyncSession, order_id: int, payload: schemas.OrderUpdate) -> models.Order:
    result = await db.execute(select(models.Order).where(models.Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if order.status in (schemas.OrderStatus.delivered.value, schemas.OrderStatus.canceled.value):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Completed order cannot be modified")

    if payload.dropoff_latitude is not None and payload.dropoff_longitude is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Longitude required with latitude")
    if payload.dropoff_longitude is not None and payload.dropoff_latitude is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Latitude required with longitude")

    if payload.dropoff_address is not None:
        order.dropoff_address = payload.dropoff_address
    if payload.dropoff_latitude is not None and payload.dropoff_longitude is not None:
        order.dropoff_latitude = payload.dropoff_latitude
        order.dropoff_longitude = payload.dropoff_longitude
    if payload.building_external_id is not None:
        building = await get_building_by_external_id(db, payload.building_external_id)
        order.building_id = building.id if building else None
    if payload.customer_name is not None:
        order.customer_name = payload.customer_name
    if payload.customer_phone is not None:
        order.customer_phone = payload.customer_phone
    if payload.notes is not None:
        order.notes = payload.notes
    if payload.items is not None:
        order.items = [item.model_dump() for item in payload.items]

    await db.commit()
    await db.refresh(order)
    return order


async def update_order_status(db: AsyncSession, order_id: int, status_payload: schemas.OrderStatusUpdate, changed_by_user_id: int | None = None) -> models.Order:
    result = await db.execute(select(models.Order).where(models.Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    new_status = status_payload.status.value
    current_status = order.status
    if new_status == current_status:
        return order

    allowed = ORDER_STATUS_TRANSITIONS.get(current_status, set())
    if new_status not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot transition order from {current_status} to {new_status}",
        )

    order.status = new_status
    now = datetime.utcnow()
    courier_id = order.courier_id
    
    if new_status == schemas.OrderStatus.picked_up.value:
        order.picked_up_at = now
    elif new_status == schemas.OrderStatus.delivered.value:
        order.delivered_at = now
        order.compensation_paid = True
        if order.payment_method == schemas.PaymentMethod.cash.value and order.total_amount:
            courier_status_result = await db.execute(
                select(models.CourierStatus).where(models.CourierStatus.courier_id == courier_id).with_for_update()
            )
            courier_status = courier_status_result.scalar_one_or_none()
            if courier_status:
                courier_status.cash_balance += order.total_amount
    elif new_status == schemas.OrderStatus.canceled.value:
        order.canceled_at = now
        if courier_id and order.delivery_fee:
            order.compensation_paid = True
    elif new_status == schemas.OrderStatus.delivery_failed.value:
        order.delivery_failed_at = now

    await db.commit()
    await db.refresh(order)
    
    await log_order_status_change(db, order_id, current_status, new_status, changed_by_user_id)
    
    if courier_id:
        await _update_courier_busy_status(db, courier_id)
    
    return order


async def decline_order(db: AsyncSession, order_id: int, reason: str | None = None, changed_by_user_id: int | None = None) -> models.Order:
    result = await db.execute(select(models.Order).where(models.Order.id == order_id).with_for_update())
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if order.status not in (schemas.OrderStatus.accepted.value, schemas.OrderStatus.ready_for_pickup.value):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order must be ACCEPTED or READY_FOR_PICKUP to decline",
        )
    if order.courier_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order has no courier assigned")
    
    old_status = order.status
    courier_id = order.courier_id
    
    declined_ids = []
    if order.declined_courier_ids:
        declined_ids = order.declined_courier_ids.split(",")
    if str(courier_id) not in declined_ids:
        declined_ids.append(str(courier_id))
    order.declined_courier_ids = ",".join(declined_ids)
    
    order.courier_id = None
    order.status = schemas.OrderStatus.pending.value
    order.accepted_at = None
    
    await db.commit()
    await db.refresh(order)
    
    await log_order_status_change(db, order_id, old_status, order.status, changed_by_user_id)
    await notify_courier(courier_id, "order_declined", {"order_id": order.id, "order_code": order.order_code, "reason": reason})
    
    await _update_courier_busy_status(db, courier_id)
    
    return order


async def mark_delivery_failed(db: AsyncSession, order_id: int, payload: schemas.OrderDeliveryFailed, changed_by_user_id: int | None = None) -> models.Order:
    result = await db.execute(select(models.Order).where(models.Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if order.status != schemas.OrderStatus.picked_up.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order must be PICKED_UP to mark as delivery failed",
        )
    
    old_status = order.status
    order.status = schemas.OrderStatus.delivery_failed.value
    order.delivery_failed_at = datetime.utcnow()
    order.return_reason = payload.return_reason
    
    await db.commit()
    await db.refresh(order)
    
    await log_order_status_change(db, order_id, old_status, order.status, changed_by_user_id)
    
    return order


async def batch_assign_orders(db: AsyncSession, order_ids: list[int], courier_id: int, changed_by_user_id: int | None = None) -> list[models.Order]:
    courier = await get_user_by_id(db, courier_id)
    if not courier or courier.role != schemas.UserRole.courier.value:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Courier not found")
    if not courier.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Courier is disabled")
    
    courier_status_result = await db.execute(
        select(models.CourierStatus).where(models.CourierStatus.courier_id == courier_id).with_for_update()
    )
    courier_status = courier_status_result.scalar_one_or_none()
    if not courier_status or courier_status.status != schemas.CourierStatusEnum.online.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Courier is not online")
    
    assigned_orders = []
    for order_id in order_ids:
        result = await db.execute(select(models.Order).where(models.Order.id == order_id).with_for_update())
        order = result.scalar_one_or_none()
        if not order:
            continue
        if order.status != schemas.OrderStatus.pending.value:
            continue
        if order.courier_id is not None:
            continue
        
        old_status = order.status
        order.courier_id = courier_id
        order.status = schemas.OrderStatus.accepted.value
        order.accepted_at = datetime.utcnow()
        
        await log_order_status_change(db, order_id, old_status, order.status, changed_by_user_id)
        assigned_orders.append(order)
    
    await db.commit()
    
    for order in assigned_orders:
        await db.refresh(order)
        await notify_courier(courier_id, "order_assigned", {"order_id": order.id, "order_code": order.order_code})
    
    return assigned_orders


async def unassign_order(db: AsyncSession, order_id: int, changed_by_user_id: int | None = None) -> models.Order:
    result = await db.execute(select(models.Order).where(models.Order.id == order_id).with_for_update())
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if order.status not in (schemas.OrderStatus.accepted.value, schemas.OrderStatus.picked_up.value):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order must be ACCEPTED or PICKED_UP to unassign",
        )
    
    old_status = order.status
    old_courier_id = order.courier_id
    order.courier_id = None
    order.status = schemas.OrderStatus.pending.value
    order.accepted_at = None
    order.picked_up_at = None
    
    await db.commit()
    await db.refresh(order)
    
    await log_order_status_change(db, order_id, old_status, order.status, changed_by_user_id)
    
    if old_courier_id:
        await notify_courier(old_courier_id, "order_unassigned", {"order_id": order.id, "order_code": order.order_code})
    
    return order


async def reassign_order(db: AsyncSession, order_id: int, new_courier_id: int, changed_by_user_id: int | None = None) -> models.Order:
    result = await db.execute(select(models.Order).where(models.Order.id == order_id).with_for_update())
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if order.status not in (schemas.OrderStatus.accepted.value, schemas.OrderStatus.picked_up.value):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order must be ACCEPTED or PICKED_UP to reassign",
        )
    
    old_courier_id = order.courier_id
    courier = await get_user_by_id(db, new_courier_id)
    if not courier or courier.role != schemas.UserRole.courier.value:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Courier not found")
    if not courier.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Courier is disabled")
    
    courier_status = await get_courier_status(db, new_courier_id)
    if not courier_status or courier_status.status != schemas.CourierStatusEnum.online.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New courier is not online")
    
    old_status = order.status
    order.courier_id = new_courier_id
    order.status = schemas.OrderStatus.accepted.value
    order.accepted_at = datetime.utcnow()
    if old_status == schemas.OrderStatus.picked_up.value:
        order.picked_up_at = None
    
    await db.commit()
    await db.refresh(order)
    
    await log_order_status_change(db, order_id, old_status, order.status, changed_by_user_id)
    
    await notify_courier(new_courier_id, "order_assigned", {"order_id": order.id, "order_code": order.order_code})
    if old_courier_id and old_courier_id != new_courier_id:
        await notify_courier(old_courier_id, "order_reassigned", {"order_id": order.id, "order_code": order.order_code})
    
    return order


async def list_orders_for_restaurant(db: AsyncSession, restaurant_id: int) -> list[models.Order]:
    result = await db.execute(
        select(models.Order)
        .options(selectinload(models.Order.restaurant), selectinload(models.Order.dropoff_building))
        .where(models.Order.restaurant_id == restaurant_id)
    )
    return result.scalars().all()


async def list_orders_for_courier(db: AsyncSession, courier_id: int) -> list[models.Order]:
    result = await db.execute(
        select(models.Order)
        .options(selectinload(models.Order.restaurant), selectinload(models.Order.dropoff_building))
        .where(models.Order.courier_id == courier_id)
    )
    return result.scalars().all()


async def get_order_by_id(db: AsyncSession, order_id: int) -> models.Order | None:
    result = await db.execute(
        select(models.Order)
        .options(selectinload(models.Order.restaurant), selectinload(models.Order.dropoff_building))
        .where(models.Order.id == order_id)
    )
    return result.scalar_one_or_none()


async def cancel_order(db: AsyncSession, order_id: int, reason: str | None = None) -> models.Order:
    result = await db.execute(select(models.Order).where(models.Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if order.status in (schemas.OrderStatus.delivered.value, schemas.OrderStatus.canceled.value):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order cannot be canceled")
    order.status = schemas.OrderStatus.canceled.value
    order.canceled_at = datetime.utcnow()
    order.cancel_reason = reason
    await db.commit()
    await db.refresh(order)
    return order


async def update_user_profile(db: AsyncSession, user: models.User, payload: schemas.UserUpdate) -> models.User:
    if payload.full_name is not None:
        user.full_name = payload.full_name
    if payload.phone is not None:
        user.phone = payload.phone
    user.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(user)
    return user


async def get_restaurant_by_id(db: AsyncSession, restaurant_id: int) -> models.Restaurant | None:
    result = await db.execute(
        select(models.Restaurant)
        .options(selectinload(models.Restaurant.building))
        .where(models.Restaurant.id == restaurant_id)
    )
    return result.scalar_one_or_none()


async def get_courier_daily_summary(db: AsyncSession, courier_id: int, date: datetime | None = None) -> schemas.CourierDailySummary:
    if date is None:
        date = datetime.utcnow()
    
    start_of_day = datetime(date.year, date.month, date.day)
    end_of_day = datetime(date.year, date.month, date.day, 23, 59, 59)
    
    result = await db.execute(
        select(models.Order)
        .where(
            models.Order.courier_id == courier_id,
            models.Order.created_at >= start_of_day,
            models.Order.created_at <= end_of_day,
        )
    )
    orders = result.scalars().all()
    
    total_orders = len(orders)
    delivered_orders = len([o for o in orders if o.status == schemas.OrderStatus.delivered.value])
    canceled_orders = len([o for o in orders if o.status == schemas.OrderStatus.canceled.value])
    
    total_earnings = None
    if orders:
        total_earnings = sum([o.total_amount for o in orders if o.total_amount is not None])
    
    return schemas.CourierDailySummary(
        date=date.strftime("%Y-%m-%d"),
        total_orders=total_orders,
        delivered_orders=delivered_orders,
        canceled_orders=canceled_orders,
        total_earnings=total_earnings,
    )


async def update_restaurant(db: AsyncSession, restaurant_id: int, payload: schemas.RestaurantUpdate) -> models.Restaurant:
    result = await db.execute(select(models.Restaurant).where(models.Restaurant.id == restaurant_id))
    restaurant = result.scalar_one_or_none()
    if not restaurant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")
    if payload.name is not None:
        restaurant.name = payload.name
    if payload.contact_phone is not None:
        restaurant.contact_phone = payload.contact_phone
    if payload.building_external_id is not None:
        building = await get_building_by_external_id(db, payload.building_external_id)
        restaurant.building_id = building.id if building else None
    if payload.opening_time is not None:
        restaurant.opening_time = payload.opening_time
    if payload.closing_time is not None:
        restaurant.closing_time = payload.closing_time
    if payload.is_open is not None:
        restaurant.is_open = payload.is_open
    if payload.delivery_radius_km is not None:
        restaurant.delivery_radius_km = payload.delivery_radius_km
    if payload.logo_url is not None:
        restaurant.logo_url = payload.logo_url
    restaurant.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(restaurant)
    return restaurant


async def add_courier_to_restaurant(
    db: AsyncSession,
    restaurant: models.Restaurant,
    payload: schemas.RestaurantCourierCreate,
) -> models.User:
    existing_user = await get_user_by_email(db, payload.email)
    if existing_user:
        if existing_user.role != schemas.UserRole.courier.value:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is not a courier")
        assignment = await db.execute(
            select(models.RestaurantCourier).where(models.RestaurantCourier.courier_id == existing_user.id)
        )
        if assignment.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Courier is already assigned")
        existing_user.is_active = True
        db.add(
            models.RestaurantCourier(restaurant_id=restaurant.id, courier_id=existing_user.id)
        )
        await db.commit()
        await db.refresh(existing_user)
        return existing_user

    courier_payload = schemas.UserCreate(
        email=payload.email,
        password=payload.password,
        full_name=payload.full_name,
        phone=payload.phone,
        role=schemas.UserRole.courier,
    )
    courier = await create_user(db, courier_payload, auto_activate=True)
    link = models.RestaurantCourier(restaurant_id=restaurant.id, courier_id=courier.id)
    db.add(link)
    await db.commit()
    await db.refresh(courier)
    return courier


async def list_couriers_for_restaurant(db: AsyncSession, restaurant_id: int) -> list[models.User]:
    result = await db.execute(
        select(models.User)
        .join(models.RestaurantCourier, models.RestaurantCourier.courier_id == models.User.id)
        .where(models.RestaurantCourier.restaurant_id == restaurant_id)
    )
    return result.scalars().all()


async def remove_courier_from_restaurant(
    db: AsyncSession,
    restaurant_id: int,
    courier_id: int,
) -> None:
    result = await db.execute(
        select(models.RestaurantCourier)
        .where(models.RestaurantCourier.restaurant_id == restaurant_id)
        .where(models.RestaurantCourier.courier_id == courier_id)
    )
    link = result.scalar_one_or_none()
    if not link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Courier link not found")

    await db.delete(link)
    await db.flush()

    remaining_links = await db.execute(
        select(models.RestaurantCourier).where(models.RestaurantCourier.courier_id == courier_id)
    )
    if remaining_links.scalar_one_or_none() is None:
        courier = await get_user_by_id(db, courier_id)
        if courier and courier.role == schemas.UserRole.courier.value:
            courier.is_active = False
            courier.updated_at = datetime.utcnow()

    await db.commit()


async def update_courier_location(db: AsyncSession, courier_id: int, payload: schemas.CourierLocationUpdate) -> models.CourierLocation:
    result = await db.execute(select(models.CourierLocation).where(models.CourierLocation.courier_id == courier_id))
    loc = result.scalar_one_or_none()
    if loc:
        loc.latitude = payload.latitude
        loc.longitude = payload.longitude
        loc.bearing = payload.bearing
        loc.speed = payload.speed
        loc.updated_at = datetime.utcnow()
    else:
        loc = models.CourierLocation(
            courier_id=courier_id,
            latitude=payload.latitude,
            longitude=payload.longitude,
            bearing=payload.bearing,
            speed=payload.speed,
        )
        db.add(loc)
    await db.commit()
    await db.refresh(loc)
    return loc


async def get_courier_location(db: AsyncSession, courier_id: int) -> models.CourierLocation | None:
    result = await db.execute(select(models.CourierLocation).where(models.CourierLocation.courier_id == courier_id))
    return result.scalar_one_or_none()


async def list_orders_paginated(db: AsyncSession, page: int = 1, per_page: int = 20, status_filter: str | None = None, restaurant_id: int | None = None, courier_id: int | None = None) -> tuple[list[models.Order], int]:
    query = select(models.Order).options(selectinload(models.Order.restaurant), selectinload(models.Order.dropoff_building))
    count_query = select(func.count(models.Order.id))
    if status_filter:
        query = query.where(models.Order.status == status_filter)
        count_query = count_query.where(models.Order.status == status_filter)
    if restaurant_id:
        query = query.where(models.Order.restaurant_id == restaurant_id)
        count_query = count_query.where(models.Order.restaurant_id == restaurant_id)
    if courier_id:
        query = query.where(models.Order.courier_id == courier_id)
        count_query = count_query.where(models.Order.courier_id == courier_id)
    total = (await db.execute(count_query)).scalar() or 0
    query = query.order_by(models.Order.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    return result.scalars().all(), total


async def get_courier_status(db: AsyncSession, courier_id: int) -> models.CourierStatus | None:
    result = await db.execute(select(models.CourierStatus).where(models.CourierStatus.courier_id == courier_id))
    return result.scalar_one_or_none()


async def collect_cash_from_courier(db: AsyncSession, courier_id: int, amount: float) -> models.CourierStatus:
    courier_status_result = await db.execute(
        select(models.CourierStatus).where(models.CourierStatus.courier_id == courier_id).with_for_update()
    )
    courier_status = courier_status_result.scalar_one_or_none()
    if not courier_status:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Courier status not found")
    
    if amount > courier_status.cash_balance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Amount exceeds cash balance. Balance: {courier_status.cash_balance}"
        )
    
    courier_status.cash_balance -= amount
    await db.commit()
    await db.refresh(courier_status)
    
    return courier_status


async def update_courier_status(db: AsyncSession, courier_id: int, payload: schemas.CourierStatusUpdate) -> models.CourierStatus:
    if payload.status.value == schemas.CourierStatusEnum.offline.value:
        result = await db.execute(
            select(models.Order).where(
                models.Order.courier_id == courier_id,
                models.Order.status.in_([
                    schemas.OrderStatus.accepted.value,
                    schemas.OrderStatus.ready_for_pickup.value,
                    schemas.OrderStatus.picked_up.value,
                ])
            )
        )
        active_orders = result.scalars().all()
        if active_orders:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot go offline with active orders"
            )
    
    result = await db.execute(select(models.CourierStatus).where(models.CourierStatus.courier_id == courier_id))
    status = result.scalar_one_or_none()
    now = datetime.utcnow()
    if status:
        status.status = payload.status.value
        status.updated_at = now
        if payload.status.value == schemas.CourierStatusEnum.online.value:
            status.last_online_at = now
    else:
        status = models.CourierStatus(
            courier_id=courier_id,
            status=payload.status.value,
            updated_at=now,
            last_online_at=now if payload.status.value == schemas.CourierStatusEnum.online.value else None,
        )
        db.add(status)
    await db.commit()
    await db.refresh(status)
    return status


async def get_order_by_tracking_hash(db: AsyncSession, tracking_hash: str) -> models.Order | None:
    result = await db.execute(
        select(models.Order)
        .options(
            selectinload(models.Order.restaurant),
            selectinload(models.Order.courier),
        )
        .where(models.Order.tracking_hash == tracking_hash)
    )
    return result.scalar_one_or_none()


async def get_order_tracking_data(db: AsyncSession, tracking_hash: str) -> schemas.OrderTracking:
    order = await get_order_by_tracking_hash(db, tracking_hash)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    courier_location = None
    if order.courier_id:
        loc = await get_courier_location(db, order.courier_id)
        if loc:
            courier_location = schemas.CourierLocationRead(
                courier_id=loc.courier_id,
                latitude=loc.latitude,
                longitude=loc.longitude,
                bearing=loc.bearing,
                speed=loc.speed,
                updated_at=loc.updated_at,
            )
    
    return schemas.OrderTracking(
        status=schemas.OrderStatus(order.status),
        courier_location=courier_location,
        restaurant_name=order.restaurant.name if order.restaurant else None,
        delivery_distance_km=order.delivery_distance_km,
        delivery_fee=order.delivery_fee,
    )
