from sqlalchemy import Column, Integer, String, Boolean, Enum, Float, DateTime, ForeignKey, func
from app.core.database import Base
import enum

class UserRole(str, enum.Enum):
    customer = "customer"
    courier = "courier"
    restaurant = "restaurant"
    company = "company"
    admin = "admin"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    phone = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=True)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)
    # Kuryer uchun
    current_lat = Column(Float, nullable=True)
    current_lon = Column(Float, nullable=True)
    is_available = Column(Boolean, default=True)
    # Transport turi
    vehicle_type = Column(String, nullable=True, default="motorcycle")
    # Kim tomonidan yaratilgan (restoran yoki kompaniya)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
