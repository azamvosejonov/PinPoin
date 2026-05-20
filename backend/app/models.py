from __future__ import annotations

from typing import Optional

from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, DateTime, JSON, UniqueConstraint
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
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="dropoff_building")


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


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    full_name: Mapped[str | None] = mapped_column(String, nullable=True)
    phone: Mapped[str | None] = mapped_column(String, nullable=True)
    password_hash: Mapped[str] = mapped_column(String)
    role: Mapped[str] = mapped_column(String, default="courier")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    restaurants: Mapped[list["Restaurant"]] = relationship("Restaurant", back_populates="owner")
    courier_orders: Mapped[list["Order"]] = relationship(
        "Order", back_populates="courier", foreign_keys="Order.courier_id"
    )
    tokens: Mapped[list["UserToken"]] = relationship("UserToken", back_populates="user", cascade="all, delete-orphan")
    restaurant_assignments: Mapped[list["RestaurantCourier"]] = relationship(
        "RestaurantCourier", back_populates="courier", cascade="all, delete-orphan"
    )
    courier_status: Mapped[Optional["CourierStatus"]] = relationship(
        "CourierStatus", back_populates="courier", cascade="all, delete-orphan", uselist=False
    )


class Restaurant(Base):
    __tablename__ = "restaurants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String)
    contact_phone: Mapped[str | None] = mapped_column(String, nullable=True)
    opening_time: Mapped[str | None] = mapped_column(String, nullable=True)
    closing_time: Mapped[str | None] = mapped_column(String, nullable=True)
    is_open: Mapped[bool] = mapped_column(Boolean, default=True)
    delivery_radius_km: Mapped[float | None] = mapped_column(Float, nullable=True, default=10.0)
    logo_url: Mapped[str | None] = mapped_column(String, nullable=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    building_id: Mapped[int | None] = mapped_column(ForeignKey("buildings.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner: Mapped[User] = relationship("User", back_populates="restaurants")
    building: Mapped[Building | None] = relationship("Building")
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="restaurant")
    couriers: Mapped[list["RestaurantCourier"]] = relationship(
        "RestaurantCourier", back_populates="restaurant", cascade="all, delete-orphan"
    )


class RestaurantCourier(Base):
    __tablename__ = "restaurant_couriers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    restaurant_id: Mapped[int] = mapped_column(ForeignKey("restaurants.id"))
    courier_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    restaurant: Mapped[Restaurant] = relationship("Restaurant", back_populates="couriers")
    courier: Mapped[User] = relationship("User", back_populates="restaurant_assignments")


class CourierStatus(Base):
    __tablename__ = "courier_status"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    courier_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, index=True)
    status: Mapped[str] = mapped_column(String, default="offline")
    transport_mode: Mapped[str] = mapped_column(String, default="pedestrian")  # pedestrian, bicycle, car
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_online_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    cash_balance: Mapped[float] = mapped_column(Float, default=0.0)

    courier: Mapped[User] = relationship("User", back_populates="courier_status")


class OrderStatusLog(Base):
    __tablename__ = "order_status_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False, index=True)
    old_status: Mapped[str | None] = mapped_column(String, nullable=True)
    new_status: Mapped[str] = mapped_column(String, nullable=False)
    changed_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    order: Mapped[Order] = relationship("Order")
    changed_by: Mapped[User | None] = relationship("User")


class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (UniqueConstraint("order_code", name="uq_orders_order_code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    order_code: Mapped[str] = mapped_column(String, nullable=False)
    tracking_hash: Mapped[Optional[str]] = mapped_column(String, unique=True, index=True, nullable=True)
    status: Mapped[str] = mapped_column(String, default="PENDING", index=True)
    customer_name: Mapped[str | None] = mapped_column(String, nullable=True)
    customer_phone: Mapped[str | None] = mapped_column(String, nullable=True)
    notes: Mapped[str | None] = mapped_column(String, nullable=True)
    items: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    dropoff_address: Mapped[str] = mapped_column(String)
    dropoff_latitude: Mapped[float] = mapped_column(Float)
    dropoff_longitude: Mapped[float] = mapped_column(Float)
    restaurant_id: Mapped[int] = mapped_column(ForeignKey("restaurants.id"))
    building_id: Mapped[int | None] = mapped_column(ForeignKey("buildings.id"), nullable=True)
    courier_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    delivery_distance_km: Mapped[float | None] = mapped_column(Float, nullable=True)
    delivery_fee: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    picked_up_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    canceled_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    cancel_reason: Mapped[str | None] = mapped_column(String, nullable=True)
    delivery_failed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    return_reason: Mapped[str | None] = mapped_column(String, nullable=True)
    preparation_time_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ready_for_pickup_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_urgent: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    total_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    payment_method: Mapped[str | None] = mapped_column(String, nullable=True)
    declined_courier_ids: Mapped[str | None] = mapped_column(String, nullable=True)
    compensation_paid: Mapped[bool] = mapped_column(Boolean, default=False)
    max_retries: Mapped[int] = mapped_column(Integer, default=3)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    # Thermal tracking fields
    initial_food_temp: Mapped[float | None] = mapped_column(Float, nullable=True)
    packaging_type: Mapped[str | None] = mapped_column(String, nullable=True)  # standard, thermal_bag, insulated_box
    predicted_arrival_temp: Mapped[float | None] = mapped_column(Float, nullable=True)
    thermal_risk_level: Mapped[str | None] = mapped_column(String, nullable=True)  # LOW, MEDIUM, HIGH
    # Corrected pin
    corrected_latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    corrected_longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    pin_correction_reason: Mapped[str | None] = mapped_column(String, nullable=True)
    # Indoor delivery timing
    indoor_entered_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    indoor_exited_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    restaurant: Mapped[Restaurant] = relationship("Restaurant", back_populates="orders")
    courier: Mapped[User | None] = relationship("User", back_populates="courier_orders", foreign_keys=[courier_id])
    dropoff_building: Mapped[Building | None] = relationship("Building", back_populates="orders")


class UserToken(Base):
    __tablename__ = "user_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    token: Mapped[str] = mapped_column(String, unique=True, index=True)
    purpose: Mapped[str] = mapped_column(String)
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    user: Mapped[User] = relationship("User", back_populates="tokens")


class TokenBlacklist(Base):
    __tablename__ = "token_blacklist"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    token: Mapped[str] = mapped_column(String, unique=True, index=True)
    blacklisted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class CourierLocation(Base):
    __tablename__ = "courier_locations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    courier_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, index=True)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    bearing: Mapped[float | None] = mapped_column(Float, nullable=True)
    speed: Mapped[float | None] = mapped_column(Float, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    courier: Mapped[User] = relationship("User")


class DeliveryMetric(Base):
    __tablename__ = "delivery_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), index=True)
    courier_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    restaurant_id: Mapped[int] = mapped_column(ForeignKey("restaurants.id"), index=True)
    total_delivery_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    indoor_delay_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    outdoor_travel_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    distance_km: Mapped[float | None] = mapped_column(Float, nullable=True)
    final_food_temp: Mapped[float | None] = mapped_column(Float, nullable=True)
    courier_rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    transport_mode: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    order: Mapped[Order] = relationship("Order")
    courier: Mapped[User] = relationship("User")
    restaurant: Mapped[Restaurant] = relationship("Restaurant")


class SuccessfulDeliveryCluster(Base):
    __tablename__ = "successful_delivery_clusters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    building_id: Mapped[int] = mapped_column(ForeignKey("buildings.id"), index=True)
    entrance_label: Mapped[str | None] = mapped_column(String, nullable=True)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    delivery_count: Mapped[int] = mapped_column(Integer, default=1)
    last_delivered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    building: Mapped[Building] = relationship("Building")
