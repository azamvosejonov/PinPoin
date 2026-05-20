from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from app.core.database import Base

class TrackingPageVisit(Base):
    __tablename__ = "tracking_page_visits"

    id = Column(Integer, primary_key=True, index=True)
    tracking_token = Column(String, nullable=False, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    visited_at = Column(DateTime, server_default=func.now())
