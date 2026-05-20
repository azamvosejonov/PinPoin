from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, func
from app.core.database import Base
import secrets

class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    key = Column(String, unique=True, nullable=False, default=lambda: f"pp_{secrets.token_urlsafe(32)}")
    name = Column(String, nullable=False)  # "iiko integration", "my pos system"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    last_used_at = Column(DateTime, nullable=True)
