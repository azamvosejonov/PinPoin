from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, JSON, DateTime, func
from app.core.database import Base

class Building(Base):
    __tablename__ = "buildings"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String, nullable=False)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    total_floors = Column(Integer, nullable=False)
    has_elevator = Column(Boolean, default=False)
    entrance_code = Column(String, nullable=True)
    floor_map = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

class ApartmentAccess(Base):
    __tablename__ = "apartment_access"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    building_id = Column(Integer, ForeignKey("buildings.id"), nullable=False)
    apartment_number = Column(String, nullable=False)
    floor = Column(Integer, nullable=False)
    door_code_encrypted = Column(String, nullable=True)  # Fernet bilan shifrlangan
    position = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
