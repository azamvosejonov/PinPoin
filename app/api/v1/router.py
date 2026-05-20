from fastapi import APIRouter
from app.api.v1.endpoints import auth, restaurants, orders, delivery, buildings, admin, support, staff, integration, notifications, tracking

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(restaurants.router)
api_router.include_router(orders.router)
api_router.include_router(delivery.router)
api_router.include_router(buildings.router)
api_router.include_router(admin.router)
api_router.include_router(support.router)
api_router.include_router(staff.router)
api_router.include_router(integration.router)
api_router.include_router(notifications.router)
