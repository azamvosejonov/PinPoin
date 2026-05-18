from datetime import datetime
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from sqlalchemy.orm import selectinload
from app import models, schemas
import math


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
