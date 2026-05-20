from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, JSON, func
from app.core.database import Base

class DeliveryTracking(Base):
    __tablename__ = "delivery_tracking"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    courier_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    # Optimal marshrut: [{lat, lon, instruction}]
    route = Column(JSON, nullable=True)
    estimated_minutes = Column(Integer, nullable=True)
    recorded_at = Column(DateTime, server_default=func.now())
