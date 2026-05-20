from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum, DateTime, JSON, Boolean, func
from app.core.database import Base
import enum
import secrets

class OrderStatus(str, enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    preparing = "preparing"
    picked_up = "picked_up"
    on_the_way = "on_the_way"
    delivered = "delivered"
    cancelled = "cancelled"

class PaymentStatus(str, enum.Enum):
    unpaid = "unpaid"
    paid = "paid"
    refunded = "refunded"

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    courier_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(Enum(OrderStatus), default=OrderStatus.pending)

    # Mehmon tracking token
    tracking_token = Column(String, unique=True, nullable=False, default=lambda: secrets.token_urlsafe(16))

    # Yetkazib berish manzili
    delivery_address = Column(String, nullable=False)
    delivery_lat = Column(Float, nullable=False)
    delivery_lon = Column(Float, nullable=False)

    # Bino navigatsiya
    building_id = Column(Integer, ForeignKey("buildings.id"), nullable=True)
    apartment_number = Column(String, nullable=True)
    floor = Column(Integer, nullable=True)

    # Narxlar
    items_price = Column(Float, nullable=False, default=0.0)
    delivery_fee = Column(Float, nullable=False, default=0.0)
    total_price = Column(Float, nullable=False)

    # To'lov
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.unpaid)
    payment_method = Column(String, nullable=True)  # cash, card, online

    # Bekor qilish
    cancelled_by = Column(String, nullable=True)   # customer / courier / restaurant
    cancel_reason = Column(String, nullable=True)

    ai_analysis = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    delivered_at = Column(DateTime, nullable=True)

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=True)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)

class CourierEarning(Base):
    """Kuryer daromadi — har bir yetkazib berish uchun"""
    __tablename__ = "courier_earnings"

    id = Column(Integer, primary_key=True, index=True)
    courier_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    amount = Column(Float, nullable=False)
    distance_km = Column(Float, nullable=True)
    earned_at = Column(DateTime, server_default=func.now())
