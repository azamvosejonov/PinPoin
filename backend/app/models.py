from __future__ import annotations

from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from app.database import Base


class Building(Base):
    __tablename__ = "buildings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    external_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    address: Mapped[str] = mapped_column(String)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    building_type: Mapped[str] = mapped_column(String, default="OTHER")
    difficulty_index: Mapped[int] = mapped_column(Integer, default=1)
    has_lift: Mapped[bool] = mapped_column(Boolean, default=False)
    requires_chip: Mapped[bool] = mapped_column(Boolean, default=False)
    entrance_hint: Mapped[str | None] = mapped_column(String, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    entrances: Mapped[list[Entrance]] = relationship("Entrance", back_populates="building", cascade="all, delete-orphan")
    trajectories: Mapped[list[Trajectory]] = relationship("Trajectory", back_populates="building", cascade="all, delete-orphan")
    indoor_map: Mapped[IndoorMap | None] = relationship(
        "IndoorMap", back_populates="building", cascade="all, delete-orphan", uselist=False
    )


class Entrance(Base):
    __tablename__ = "entrances"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    building_id: Mapped[int] = mapped_column(ForeignKey("buildings.id"))
    label: Mapped[str] = mapped_column(String)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    domofon_code: Mapped[str | None] = mapped_column(String, nullable=True)
    has_barrier: Mapped[bool] = mapped_column(Boolean, default=False)
    validated_count: Mapped[int] = mapped_column(Integer, default=0)
    last_validated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    building: Mapped[Building] = relationship("Building", back_populates="entrances")


class Trajectory(Base):
    __tablename__ = "trajectories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    building_id: Mapped[int] = mapped_column(ForeignKey("buildings.id"))
    courier_id: Mapped[str] = mapped_column(String)
    delivered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    points: Mapped[list[dict]] = mapped_column(JSON)

    building: Mapped[Building] = relationship("Building", back_populates="trajectories")


class DeliverySession(Base):
    __tablename__ = "delivery_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    order_id: Mapped[str] = mapped_column(String, unique=True)
    courier_id: Mapped[str] = mapped_column(String, index=True)
    building_id: Mapped[int] = mapped_column(ForeignKey("buildings.id"))
    start_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    end_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    temperature_model: Mapped[str] = mapped_column(String)
    start_temperature: Mapped[float] = mapped_column(Float)
    predicted_temperature: Mapped[float] = mapped_column(Float)
    predicted_eta_minutes: Mapped[int] = mapped_column(Integer)
    transport_mode: Mapped[str | None] = mapped_column(String, nullable=True)

    building: Mapped[Building] = relationship("Building")


class IndoorMap(Base):
    __tablename__ = "indoor_maps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    building_id: Mapped[int] = mapped_column(ForeignKey("buildings.id"), unique=True)
    anchor_latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    anchor_longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    anchor_altitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    floors: Mapped[list[dict]] = mapped_column(JSON)
    extras: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    building: Mapped[Building] = relationship("Building", back_populates="indoor_map")
    paths: Mapped[list[IndoorPath]] = relationship("IndoorPath", back_populates="indoor_map", cascade="all, delete-orphan")


class IndoorPath(Base):
    __tablename__ = "indoor_paths"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    indoor_map_id: Mapped[int] = mapped_column(ForeignKey("indoor_maps.id"))
    courier_id: Mapped[str] = mapped_column(String, index=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    path: Mapped[list[dict]] = mapped_column(JSON)

    indoor_map: Mapped[IndoorMap] = relationship("IndoorMap", back_populates="paths")
