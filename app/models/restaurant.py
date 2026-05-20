from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, func, UniqueConstraint
from app.core.database import Base

class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    phone = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    # Ish vaqti
    open_time = Column(String, nullable=False, default="09:00")   # "HH:MM"
    close_time = Column(String, nullable=False, default="23:00")  # "HH:MM"
    # Yetkazib berish
    delivery_fee = Column(Float, nullable=False, default=0.0)
    min_order_price = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime, server_default=func.now())

class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    calories = Column(Float, nullable=True)
    temperature_sensitive = Column(Boolean, default=False)
    is_available = Column(Boolean, default=True)

class RestaurantCourier(Base):
    __tablename__ = "restaurant_couriers"
    __table_args__ = (UniqueConstraint("restaurant_id", "courier_id"),)

    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    courier_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_at = Column(DateTime, server_default=func.now())
