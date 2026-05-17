from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# Delivery Schemas
class DeliveryBase(BaseModel):
    customer_id: str
    courier_id: Optional[str] = None
    address: str
    latitude: float
    longitude: float
    status: str = "PENDING"
    items: Optional[dict] = None
    estimated_time: int
    actual_time: Optional[int] = None
    created_at: int
    picked_up_at: Optional[int] = None
    delivered_at: Optional[int] = None


class DeliveryCreate(BaseModel):
    customer_id: str
    courier_id: Optional[str] = None
    address: str
    latitude: float
    longitude: float
    items: Optional[dict] = None
    estimated_time: int


class DeliveryUpdate(BaseModel):
    status: Optional[str] = None
    actual_time: Optional[int] = None
    picked_up_at: Optional[int] = None
    delivered_at: Optional[int] = None


class Delivery(DeliveryBase):
    id: str
    
    class Config:
        from_attributes = True


# Building Schemas
class BuildingBase(BaseModel):
    address: str
    latitude: float
    longitude: float
    building_type: str
    floors: int
    has_elevator: bool = False
    elevator_type: Optional[str] = None
    difficulty_score: int = 1
    access_notes: Optional[str] = None


class BuildingCreate(BuildingBase):
    pass


class Building(BuildingBase):
    id: str
    entrances: List["BuildingEntrance"] = []
    domofon_codes: List["DomofonCode"] = []
    
    class Config:
        from_attributes = True


# Building Entrance Schemas
class BuildingEntranceBase(BaseModel):
    entrance_number: str
    latitude: float
    longitude: float
    is_confirmed: bool = False
    confirmation_count: int = 0
    last_confirmed: Optional[int] = None
    access_method: str


class BuildingEntranceCreate(BaseModel):
    entrance_number: str
    latitude: float
    longitude: float
    access_method: str


class BuildingEntrance(BuildingEntranceBase):
    id: str
    building_id: str
    
    class Config:
        from_attributes = True


# Domofon Code Schemas
class DomofonCodeBase(BaseModel):
    entrance_number: str
    code: str
    code_type: str
    is_verified: bool = False
    verification_count: int = 0
    last_verified: Optional[int] = None
    added_by: str
    notes: Optional[str] = None


class DomofonCodeCreate(BaseModel):
    building_id: str
    entrance_number: str
    code: str
    code_type: str
    added_by: str
    notes: Optional[str] = None


class DomofonCode(DomofonCodeBase):
    id: str
    building_id: str
    
    class Config:
        from_attributes = True


# Location Schemas
class LocationBase(BaseModel):
    courier_id: str
    latitude: float
    longitude: float
    accuracy: Optional[float] = None
    altitude: Optional[float] = None
    timestamp: int


class LocationCreate(LocationBase):
    pass


class Location(LocationBase):
    id: str
    
    class Config:
        from_attributes = True


# Location Point Schemas
class LocationPointBase(BaseModel):
    delivery_id: str
    latitude: float
    longitude: float
    accuracy: Optional[float] = None
    altitude: Optional[float] = None
    timestamp: int
    speed: Optional[float] = None
    activity_type: str


class LocationPointCreate(LocationPointBase):
    pass


class LocationPoint(LocationPointBase):
    id: str
    
    class Config:
        from_attributes = True


# Update forward references
Building.model_rebuild()
