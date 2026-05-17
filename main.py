from fastapi import FastAPI, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid

from database import get_db, engine, Base
from models import Delivery, Building, BuildingEntrance, DomofonCode, Location, LocationPoint
from schemas import (
    DeliveryCreate, DeliveryUpdate, Delivery as DeliverySchema,
    BuildingCreate, Building as BuildingSchema,
    BuildingEntranceCreate, BuildingEntrance as BuildingEntranceSchema,
    DomofonCodeCreate, DomofonCode as DomofonCodeSchema,
    LocationCreate, Location as LocationSchema,
    LocationPointCreate, LocationPoint as LocationPointSchema
)
from config import settings
from geocoding_service import GeocodingService
from weather_service import WeatherService
from ml_service import TrajectoryClusteringService
from thermal_service import ThermalCalculationService
from ai_schemas import (
    GeocodingRequest, GeocodingResponse,
    ThermalPredictionRequest, ThermalPredictionResponse,
    DifficultyTimeRequest, DifficultyTimeResponse,
    TrajectoryAnalysisRequest, TrajectoryAnalysisResponse
)
from websocket_manager import manager
from redis_service import redis_service
from auth_service import auth_service

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="PinPoint Delivery API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Helper function to generate UUID
def generate_id() -> str:
    return str(uuid.uuid4())


# Health check
@app.get("/")
def health_check():
    return {"status": "healthy", "message": "PinPoint API is running"}


# ============ DELIVERIES ENDPOINTS ============

@app.get(f"{settings.API_V1_PREFIX}/deliveries", response_model=List[DeliverySchema])
def get_active_deliveries(
    courier_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Delivery)
    if courier_id:
        query = query.filter(
            Delivery.courier_id == courier_id,
            Delivery.status.notin_(['DELIVERED', 'CANCELLED'])
        )
    else:
        # If no courier_id, return all non-cancelled deliveries
        query = query.filter(Delivery.status != 'CANCELLED')
    return query.all()


@app.get(f"{settings.API_V1_PREFIX}/deliveries/{{delivery_id}}", response_model=DeliverySchema)
def get_delivery_by_id(delivery_id: str, db: Session = Depends(get_db)):
    delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    return delivery


@app.get(f"{settings.API_V1_PREFIX}/deliveries/courier/{{courier_id}}/today", response_model=List[DeliverySchema])
def get_today_deliveries(courier_id: str, db: Session = Depends(get_db)):
    from datetime import datetime, timedelta
    today_start = int((datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)).timestamp() * 1000)
    today_end = int((datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)).timestamp() * 1000)
    
    deliveries = db.query(Delivery).filter(
        Delivery.courier_id == courier_id,
        Delivery.created_at >= today_start,
        Delivery.created_at <= today_end
    ).all()
    return deliveries


@app.post(f"{settings.API_V1_PREFIX}/deliveries", response_model=DeliverySchema, status_code=201)
def create_delivery(delivery: DeliveryCreate, db: Session = Depends(get_db)):
    delivery_id = generate_id()
    created_at = int(datetime.now().timestamp() * 1000)
    
    db_delivery = Delivery(
        id=delivery_id,
        customer_id=delivery.customer_id,
        courier_id=delivery.courier_id,
        address=delivery.address,
        latitude=delivery.latitude,
        longitude=delivery.longitude,
        status="PENDING",
        items=delivery.items,
        estimated_time=delivery.estimated_time,
        created_at=created_at
    )
    db.add(db_delivery)
    db.commit()
    db.refresh(db_delivery)
    return db_delivery


@app.put(f"{settings.API_V1_PREFIX}/deliveries/{{delivery_id}}", response_model=DeliverySchema)
def update_delivery(delivery_id: str, delivery_update: DeliveryUpdate, db: Session = Depends(get_db)):
    db_delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not db_delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    
    for field, value in delivery_update.dict(exclude_unset=True).items():
        setattr(db_delivery, field, value)
    
    db.commit()
    db.refresh(db_delivery)
    return db_delivery


@app.patch(f"{settings.API_V1_PREFIX}/deliveries/{{delivery_id}}/status")
def update_delivery_status(
    delivery_id: str,
    status_update: dict,
    db: Session = Depends(get_db)
):
    db_delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not db_delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    
    db_delivery.status = status_update.get("status", db_delivery.status)
    if status_update.get("status") == "DELIVERED":
        db_delivery.delivered_at = int(datetime.now().timestamp() * 1000)
    elif status_update.get("status") == "PICKED_UP":
        db_delivery.picked_up_at = int(datetime.now().timestamp() * 1000)
    
    db.commit()
    return {"message": "Status updated successfully"}


@app.delete(f"{settings.API_V1_PREFIX}/deliveries/{{delivery_id}}")
def delete_delivery(delivery_id: str, db: Session = Depends(get_db)):
    db_delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not db_delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    
    db.delete(db_delivery)
    db.commit()
    return {"message": "Delivery deleted successfully"}


# ============ BUILDINGS ENDPOINTS ============

@app.get(f"{settings.API_V1_PREFIX}/buildings/all", response_model=List[BuildingSchema])
def get_all_buildings(db: Session = Depends(get_db)):
    buildings = db.query(Building).all()
    return buildings


@app.get(f"{settings.API_V1_PREFIX}/buildings/search", response_model=List[BuildingSchema])
def search_buildings(address: str = Query(...), db: Session = Depends(get_db)):
    # Search buildings by address (case-insensitive)
    from sqlalchemy import func
    buildings = db.query(Building).filter(
        func.lower(Building.address).like(f"%{address.lower()}%")
    ).all()
    return buildings


@app.get(f"{settings.API_V1_PREFIX}/buildings/{{building_id}}", response_model=BuildingSchema)
def get_building_by_id(building_id: str, db: Session = Depends(get_db)):
    building = db.query(Building).filter(Building.id == building_id).first()
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
    return building


@app.get(f"{settings.API_V1_PREFIX}/buildings/nearby", response_model=List[BuildingSchema])
def get_nearby_buildings(
    min_lat: float = Query(...),
    max_lat: float = Query(...),
    min_lng: float = Query(...),
    max_lng: float = Query(...),
    db: Session = Depends(get_db)
):
    buildings = db.query(Building).filter(
        Building.latitude >= min_lat,
        Building.latitude <= max_lat,
        Building.longitude >= min_lng,
        Building.longitude <= max_lng
    ).all()
    return buildings


@app.get(f"{settings.API_V1_PREFIX}/buildings/all", response_model=List[BuildingSchema])
def get_all_buildings(db: Session = Depends(get_db)):
    buildings = db.query(Building).all()
    return buildings


@app.post(f"{settings.API_V1_PREFIX}/buildings", response_model=BuildingSchema, status_code=201)
def create_building(building: BuildingCreate, db: Session = Depends(get_db)):
    building_id = generate_id()
    
    db_building = Building(
        id=building_id,
        address=building.address,
        latitude=building.latitude,
        longitude=building.longitude,
        building_type=building.building_type,
        floors=building.floors,
        has_elevator=building.has_elevator,
        elevator_type=building.elevator_type,
        difficulty_score=building.difficulty_score,
        access_notes=building.access_notes
    )
    db.add(db_building)
    db.commit()
    db.refresh(db_building)
    return db_building


@app.put(f"{settings.API_V1_PREFIX}/buildings/{{building_id}}", response_model=BuildingSchema)
def update_building(building_id: str, building_update: BuildingCreate, db: Session = Depends(get_db)):
    db_building = db.query(Building).filter(Building.id == building_id).first()
    if not db_building:
        raise HTTPException(status_code=404, detail="Building not found")
    
    for field, value in building_update.dict().items():
        setattr(db_building, field, value)
    
    db.commit()
    db.refresh(db_building)
    return db_building


# Building Entrances
@app.get(f"{settings.API_V1_PREFIX}/buildings/{{building_id}}/entrances", response_model=List[BuildingEntranceSchema])
def get_building_entrances(building_id: str, db: Session = Depends(get_db)):
    entrances = db.query(BuildingEntrance).filter(BuildingEntrance.building_id == building_id).all()
    return entrances


@app.post(f"{settings.API_V1_PREFIX}/buildings/{{building_id}}/entrances", response_model=BuildingEntranceSchema, status_code=201)
def create_entrance(
    building_id: str,
    entrance: BuildingEntranceCreate,
    db: Session = Depends(get_db)
):
    entrance_id = generate_id()
    
    db_entrance = BuildingEntrance(
        id=entrance_id,
        building_id=building_id,
        entrance_number=entrance.entrance_number,
        latitude=entrance.latitude,
        longitude=entrance.longitude,
        access_method=entrance.access_method
    )
    db.add(db_entrance)
    db.commit()
    db.refresh(db_entrance)
    return db_entrance


@app.patch(f"{settings.API_V1_PREFIX}/buildings/entrances/{{entrance_id}}/confirm")
def confirm_entrance(
    entrance_id: str,
    timestamp: int = Query(...),
    db: Session = Depends(get_db)
):
    db_entrance = db.query(BuildingEntrance).filter(BuildingEntrance.id == entrance_id).first()
    if not db_entrance:
        raise HTTPException(status_code=404, detail="Entrance not found")
    
    db_entrance.is_confirmed = True
    db_entrance.confirmation_count += 1
    db_entrance.last_confirmed = timestamp
    
    db.commit()
    return {"message": "Entrance confirmed successfully"}


# ============ DOMOFON CODES ENDPOINTS ============

@app.get(f"{settings.API_V1_PREFIX}/domofon-codes/building/{{building_id}}", response_model=List[DomofonCodeSchema])
def get_codes_by_building(building_id: str, db: Session = Depends(get_db)):
    codes = db.query(DomofonCode).filter(DomofonCode.building_id == building_id).all()
    return codes


@app.get(f"{settings.API_V1_PREFIX}/domofon-codes/building/{{building_id}}/verified", response_model=DomofonCodeSchema)
def get_most_verified_code(building_id: str, db: Session = Depends(get_db)):
    code = db.query(DomofonCode).filter(
        DomofonCode.building_id == building_id,
        DomofonCode.is_verified == True
    ).order_by(DomofonCode.verification_count.desc()).first()
    
    if not code:
        raise HTTPException(status_code=404, detail="No verified code found")
    return code


@app.get(f"{settings.API_V1_PREFIX}/domofon-codes/{{code_id}}", response_model=DomofonCodeSchema)
def get_code_by_id(code_id: str, db: Session = Depends(get_db)):
    code = db.query(DomofonCode).filter(DomofonCode.id == code_id).first()
    if not code:
        raise HTTPException(status_code=404, detail="Code not found")
    return code


@app.get(f"{settings.API_V1_PREFIX}/domofon-codes/find", response_model=DomofonCodeSchema)
def find_code(
    building_id: str = Query(...),
    code: str = Query(...),
    db: Session = Depends(get_db)
):
    db_code = db.query(DomofonCode).filter(
        DomofonCode.building_id == building_id,
        DomofonCode.code == code
    ).first()
    
    if not db_code:
        raise HTTPException(status_code=404, detail="Code not found")
    return db_code


@app.post(f"{settings.API_V1_PREFIX}/domofon-codes", response_model=DomofonCodeSchema, status_code=201)
def create_code(code: DomofonCodeCreate, db: Session = Depends(get_db)):
    code_id = generate_id()
    
    db_code = DomofonCode(
        id=code_id,
        building_id=code.building_id,
        entrance_number=code.entrance_number,
        code=code.code,
        code_type=code.code_type,
        added_by=code.added_by,
        notes=code.notes
    )
    db.add(db_code)
    db.commit()
    db.refresh(db_code)
    return db_code


@app.put(f"{settings.API_V1_PREFIX}/domofon-codes/{{code_id}}", response_model=DomofonCodeSchema)
def update_code(code_id: str, code_update: DomofonCodeCreate, db: Session = Depends(get_db)):
    db_code = db.query(DomofonCode).filter(DomofonCode.id == code_id).first()
    if not db_code:
        raise HTTPException(status_code=404, detail="Code not found")
    
    for field, value in code_update.dict().items():
        setattr(db_code, field, value)
    
    db.commit()
    db.refresh(db_code)
    return db_code


@app.patch(f"{settings.API_V1_PREFIX}/domofon-codes/{{code_id}}/verify")
def verify_code(code_id: str, timestamp: int = Query(...), db: Session = Depends(get_db)):
    db_code = db.query(DomofonCode).filter(DomofonCode.id == code_id).first()
    if not db_code:
        raise HTTPException(status_code=404, detail="Code not found")
    
    db_code.is_verified = True
    db_code.verification_count += 1
    db_code.last_verified = timestamp
    
    db.commit()
    return {"message": "Code verified successfully"}


@app.patch(f"{settings.API_V1_PREFIX}/domofon-codes/{{code_id}}/decrement")
def decrement_verification_count(code_id: str, db: Session = Depends(get_db)):
    db_code = db.query(DomofonCode).filter(DomofonCode.id == code_id).first()
    if not db_code:
        raise HTTPException(status_code=404, detail="Code not found")
    
    db_code.verification_count = max(0, db_code.verification_count - 1)
    
    db.commit()
    return {"message": "Verification count decremented"}


# ============ LOCATIONS ENDPOINTS ============

@app.get(f"{settings.API_V1_PREFIX}/locations/latest", response_model=LocationSchema)
def get_latest_location(courier_id: str = Query(...), db: Session = Depends(get_db)):
    location = db.query(Location).filter(
        Location.courier_id == courier_id
    ).order_by(Location.timestamp.desc()).first()
    
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return location


@app.get(f"{settings.API_V1_PREFIX}/locations/since", response_model=List[LocationSchema])
def get_locations_since(
    courier_id: str = Query(...),
    start_time: int = Query(...),
    db: Session = Depends(get_db)
):
    locations = db.query(Location).filter(
        Location.courier_id == courier_id,
        Location.timestamp >= start_time
    ).order_by(Location.timestamp).all()
    return locations


@app.post(f"{settings.API_V1_PREFIX}/locations")
def save_location(location: LocationCreate, db: Session = Depends(get_db)):
    location_id = generate_id()
    
    db_location = Location(
        id=location_id,
        courier_id=location.courier_id,
        latitude=location.latitude,
        longitude=location.longitude,
        accuracy=location.accuracy,
        altitude=location.altitude,
        timestamp=location.timestamp
    )
    db.add(db_location)
    db.commit()
    return {"message": "Location saved successfully"}


# Location Points
@app.get(f"{settings.API_V1_PREFIX}/locations/points/delivery/{{delivery_id}}", response_model=List[LocationPointSchema])
def get_trajectory_by_delivery(delivery_id: str, db: Session = Depends(get_db)):
    points = db.query(LocationPoint).filter(
        LocationPoint.delivery_id == delivery_id
    ).order_by(LocationPoint.timestamp).all()
    return points


@app.get(f"{settings.API_V1_PREFIX}/locations/points/recent", response_model=List[LocationPointSchema])
def get_recent_trajectory(
    delivery_id: str = Query(...),
    start_time: int = Query(...),
    db: Session = Depends(get_db)
):
    points = db.query(LocationPoint).filter(
        LocationPoint.delivery_id == delivery_id,
        LocationPoint.timestamp >= start_time
    ).order_by(LocationPoint.timestamp).all()
    return points


@app.post(f"{settings.API_V1_PREFIX}/locations/points")
def save_location_point(point: LocationPointCreate, db: Session = Depends(get_db)):
    point_id = generate_id()
    
    db_point = LocationPoint(
        id=point_id,
        delivery_id=point.delivery_id,
        latitude=point.latitude,
        longitude=point.longitude,
        accuracy=point.accuracy,
        altitude=point.altitude,
        timestamp=point.timestamp,
        speed=point.speed,
        activity_type=point.activity_type
    )
    db.add(db_point)
    db.commit()
    return {"message": "Location point saved successfully"}


@app.delete(f"{settings.API_V1_PREFIX}/locations/points/old")
def delete_old_location_points(old_timestamp: int = Query(...), db: Session = Depends(get_db)):
    db.query(LocationPoint).filter(LocationPoint.timestamp < old_timestamp).delete()
    db.commit()
    return {"message": "Old location points deleted successfully"}


# ============ AI ENDPOINTS ============

@app.post(f"{settings.API_V1_PREFIX}/ai/geocode", response_model=GeocodingResponse)
def geocode_address(request: GeocodingRequest):
    """Convert address to coordinates using OpenStreetMap"""
    result = GeocodingService.geocode(request.address)
    if result:
        return GeocodingResponse(**result)
    raise HTTPException(status_code=404, detail="Address not found")


@app.post(f"{settings.API_V1_PREFIX}/ai/reverse-geocode")
def reverse_geocode(lat: float = Query(...), lon: float = Query(...)):
    """Convert coordinates to address"""
    result = GeocodingService.reverse_geocode(lat, lon)
    if result:
        return {"address": result}
    raise HTTPException(status_code=404, detail="Address not found")


@app.post(f"{settings.API_V1_PREFIX}/ai/thermal-predict", response_model=ThermalPredictionResponse)
def predict_thermal(request: ThermalPredictionRequest):
    """Predict food temperature after delivery time"""
    predicted_temp = ThermalCalculationService.predict_temperature(
        request.initial_temp,
        request.external_temp,
        request.insulation_coefficient,
        request.time_minutes
    )
    
    thermal_check = ThermalCalculationService.is_thermal_critical(
        predicted_temp,
        55.0,  # min acceptable for hot food
        85.0   # max acceptable for hot food
    )
    
    return ThermalPredictionResponse(
        predicted_temp=predicted_temp,
        is_critical=thermal_check['is_critical'],
        message=thermal_check['message'],
        priority=thermal_check['priority']
    )


@app.post(f"{settings.API_V1_PREFIX}/ai/difficulty-time", response_model=DifficultyTimeResponse)
def calculate_difficulty_time(request: DifficultyTimeRequest):
    """Calculate additional time for building access"""
    additional_time = ThermalCalculationService.calculate_difficulty_time(
        request.floors,
        request.has_elevator,
        request.elevator_type
    )
    return DifficultyTimeResponse(additional_time_seconds=additional_time)


@app.post(f"{settings.API_V1_PREFIX}/ai/trajectory-analyze", response_model=TrajectoryAnalysisResponse)
def analyze_trajectory(request: TrajectoryAnalysisRequest):
    """Analyze trajectory to identify podyezd entrance"""
    result = TrajectoryClusteringService.analyze_trajectory(
        request.vehicle_stops,
        request.pedestrian_points
    )
    
    if result:
        return TrajectoryAnalysisResponse(**result)
    
    return TrajectoryAnalysisResponse(
        entrance_lat=None,
        entrance_lon=None,
        confidence=None
    )


@app.get(f"{settings.API_V1_PREFIX}/ai/weather")
def get_weather(lat: float = Query(...), lon: float = Query(...)):
    """Get current weather for location"""
    result = WeatherService.get_current_weather(lat, lon)
    if result:
        return result
    return {"temp": 25.0, "humidity": 50, "description": "clear"}  # Default fallback


# ============ WEBSOCKET ENDPOINTS ============

@app.websocket("/ws/location/{courier_id}")
async def websocket_location_tracking(websocket: WebSocket, courier_id: str):
    """Real-time location tracking via WebSocket"""
    await manager.connect(courier_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            
            # Save location to database
            location_data = {
                "courier_id": courier_id,
                "latitude": data.get("latitude"),
                "longitude": data.get("longitude"),
                "accuracy": data.get("accuracy"),
                "altitude": data.get("altitude"),
                "timestamp": data.get("timestamp", datetime.now().timestamp() * 1000)
            }
            
            # Update in Redis cache
            redis_service.update_courier_location(courier_id, location_data)
            
            # Update in WebSocket manager
            await manager.update_location(courier_id, location_data)
            
            # Acknowledge
            await websocket.send_json({"status": "received", "timestamp": location_data["timestamp"]})
            
    except WebSocketDisconnect:
        manager.disconnect(courier_id, websocket)


@app.websocket("/ws/admin")
async def websocket_admin_monitor(websocket: WebSocket):
    """Admin monitoring WebSocket for all courier locations"""
    await websocket.accept()
    try:
        while True:
            # Send all courier locations every 5 seconds
            locations = manager.get_all_courier_locations()
            await websocket.send_json({
                "type": "all_locations",
                "locations": locations,
                "timestamp": datetime.now().timestamp()
            })
            
            # Wait 5 seconds
            await asyncio.sleep(5)
            
    except WebSocketDisconnect:
        pass


if __name__ == "__main__":
    import uvicorn
    import asyncio
    uvicorn.run(app, host="0.0.0.0", port=8000)
