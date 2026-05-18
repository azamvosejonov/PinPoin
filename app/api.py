from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from app import schemas, services
from app.database import get_db
from app.config import get_settings

app = FastAPI(title="PinPoInt Backend", version="1.0.0")
settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/predictive-pin", response_model=schemas.PredictivePinResponse)
async def predictive_pin(request: schemas.PredictivePinRequest):
    return services.heuristic_predictive_pin(request)


@app.post("/thermal-projection", response_model=schemas.ThermalProjectionResponse)
async def thermal_projection(request: schemas.ThermalProjectionRequest):
    return services.compute_thermal_projection(request)


@app.post("/buildings", response_model=schemas.Building)
async def upsert_building(payload: schemas.BuildingCreate, db: AsyncSession = Depends(get_db)):
    building = await services.save_building(db, payload)
    return services.building_to_schema(building)


@app.get("/buildings/{external_id}", response_model=schemas.Building)
async def get_building(external_id: str, db: AsyncSession = Depends(get_db)):
    building = await services.get_building_by_external_id(db, external_id)
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
    return services.building_to_schema(building)


@app.put("/buildings/{external_id}/indoor-map", response_model=schemas.IndoorMap)
async def put_indoor_map(
    external_id: str,
    indoor_map: schemas.IndoorMapCreate,
    db: AsyncSession = Depends(get_db),
):
    building = await services.get_building_by_external_id(db, external_id)
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
    await services.upsert_indoor_map(db, building.id, indoor_map)
    refreshed = await services.get_indoor_map(db, building.id)
    if not refreshed:
        raise HTTPException(status_code=500, detail="Indoor map not stored")
    return services.indoor_map_to_schema(refreshed)


@app.get("/buildings/{external_id}/indoor-map", response_model=schemas.IndoorMap)
async def get_indoor_map(external_id: str, db: AsyncSession = Depends(get_db)):
    building = await services.get_building_by_external_id(db, external_id)
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
    if not building.indoor_map:
        raise HTTPException(status_code=404, detail="Indoor map not defined")
    return services.indoor_map_to_schema(building.indoor_map)


@app.post("/buildings/{external_id}/indoor-map/paths", response_model=schemas.IndoorPathDetail)
async def record_indoor_path_endpoint(
    external_id: str,
    path: schemas.IndoorPathCreate,
    db: AsyncSession = Depends(get_db),
):
    building = await services.get_building_by_external_id(db, external_id)
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
    try:
        indoor_path = await services.record_indoor_path(db, building.id, path)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return services.indoor_path_to_detail(indoor_path)


@app.get("/indoor-paths/{path_id}", response_model=schemas.IndoorPathDetail)
async def get_indoor_path(path_id: int, db: AsyncSession = Depends(get_db)):
    indoor_path = await services.get_indoor_path(db, path_id)
    if not indoor_path:
        raise HTTPException(status_code=404, detail="Indoor path not found")
    return services.indoor_path_to_detail(indoor_path)


@app.post("/buildings/{external_id}/trajectories", response_model=schemas.SyncResponse)
async def submit_trajectory(
    external_id: str,
    trajectory: schemas.TrajectoryCreate,
    db: AsyncSession = Depends(get_db)
):
    building = await services.get_building_by_external_id(db, external_id)
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
    delivered_time = datetime.utcfromtimestamp(trajectory.delivered_at / 1000) if trajectory.delivered_at else None
    await services.record_trajectory(
        db,
        building,
        trajectory.courier_id,
        [p.model_dump() for p in trajectory.points],
        delivered_time,
    )
    return schemas.SyncResponse()


@app.post("/entrances/{entrance_id}/domofon", response_model=schemas.Entrance)
async def validate_domofon_code(
    entrance_id: int,
    validation: schemas.DomofonValidationRequest,
    db: AsyncSession = Depends(get_db)
):
    updated = await services.update_domofon_code(db, entrance_id, validation.code, validation.success)
    return schemas.Entrance.from_orm(updated)
