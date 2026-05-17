from sqlalchemy import Column, String, Integer, Float, Boolean, BigInteger, JSON, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Delivery(Base):
    __tablename__ = "deliveries"
    
    id = Column(String(50), primary_key=True, index=True)
    customer_id = Column(String(50), nullable=False)
    courier_id = Column(String(50), nullable=True)
    address = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    status = Column(String(20), nullable=False, default="PENDING")
    items = Column(JSON, nullable=True)
    estimated_time = Column(Integer, nullable=False)
    actual_time = Column(Integer, nullable=True)
    created_at = Column(BigInteger, nullable=False)
    picked_up_at = Column(BigInteger, nullable=True)
    delivered_at = Column(BigInteger, nullable=True)


class Building(Base):
    __tablename__ = "buildings"
    
    id = Column(String(50), primary_key=True, index=True)
    address = Column(String, nullable=False, unique=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    building_type = Column(String(20), nullable=False)
    floors = Column(Integer, nullable=False)
    has_elevator = Column(Boolean, nullable=False, default=False)
    elevator_type = Column(String(20), nullable=True)
    difficulty_score = Column(Integer, nullable=False, default=1)
    access_notes = Column(String, nullable=True)
    
    entrances = relationship("BuildingEntrance", back_populates="building", cascade="all, delete-orphan")
    domofon_codes = relationship("DomofonCode", back_populates="building", cascade="all, delete-orphan")


class BuildingEntrance(Base):
    __tablename__ = "building_entrances"
    
    id = Column(String(50), primary_key=True, index=True)
    building_id = Column(String(50), ForeignKey("buildings.id", ondelete="CASCADE"), nullable=False)
    entrance_number = Column(String(10), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    is_confirmed = Column(Boolean, nullable=False, default=False)
    confirmation_count = Column(Integer, nullable=False, default=0)
    last_confirmed = Column(BigInteger, nullable=True)
    access_method = Column(String(20), nullable=False)
    
    building = relationship("Building", back_populates="entrances")


class DomofonCode(Base):
    __tablename__ = "domofon_codes"
    
    id = Column(String(50), primary_key=True, index=True)
    building_id = Column(String(50), ForeignKey("buildings.id", ondelete="CASCADE"), nullable=False)
    entrance_number = Column(String(10), nullable=False)
    code = Column(String(50), nullable=False)
    code_type = Column(String(20), nullable=False)
    is_verified = Column(Boolean, nullable=False, default=False)
    verification_count = Column(Integer, nullable=False, default=0)
    last_verified = Column(BigInteger, nullable=True)
    added_by = Column(String(50), nullable=False)
    notes = Column(String, nullable=True)
    
    building = relationship("Building", back_populates="domofon_codes")


class Location(Base):
    __tablename__ = "locations"
    
    id = Column(String(50), primary_key=True, index=True)
    courier_id = Column(String(50), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    accuracy = Column(Float, nullable=True)
    altitude = Column(Float, nullable=True)
    timestamp = Column(BigInteger, nullable=False)


class LocationPoint(Base):
    __tablename__ = "location_points"
    
    id = Column(String(50), primary_key=True, index=True)
    delivery_id = Column(String(50), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    accuracy = Column(Float, nullable=True)
    altitude = Column(Float, nullable=True)
    timestamp = Column(BigInteger, nullable=False)
    speed = Column(Float, nullable=True)
    activity_type = Column(String(20), nullable=False)
