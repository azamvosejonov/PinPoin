from datetime import datetime
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, status, Query, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession
from app import schemas, services, models
from app.database import get_db
from app.config import get_settings

app = FastAPI(title="PinPoInt Backend", version="1.0.0")
settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0"}


@app.post("/predictive-pin", response_model=schemas.PredictivePinResponse)
async def predictive_pin(request: schemas.PredictivePinRequest):
    return services.heuristic_predictive_pin(request)


@app.post("/thermal-projection", response_model=schemas.ThermalProjectionResponse)
async def thermal_projection(request: schemas.ThermalProjectionRequest):
    return services.compute_thermal_projection(request)


@app.post("/buildings", response_model=schemas.Building)
async def upsert_building(payload: schemas.BuildingCreate, db: AsyncSession = Depends(get_db)):
    building = await services.save_building(db, payload)
    return services.building_to_schema(building)


@app.get("/buildings/{external_id}", response_model=schemas.Building)
async def get_building(external_id: str, db: AsyncSession = Depends(get_db)):
    building = await services.get_building_by_external_id(db, external_id)
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
    return services.building_to_schema(building)


@app.put("/buildings/{external_id}/indoor-map", response_model=schemas.IndoorMap)
async def put_indoor_map(
    external_id: str,
    indoor_map: schemas.IndoorMapCreate,
    db: AsyncSession = Depends(get_db),
):
    building = await services.get_building_by_external_id(db, external_id)
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
    await services.upsert_indoor_map(db, building.id, indoor_map)
    refreshed = await services.get_indoor_map(db, building.id)
    if not refreshed:
        raise HTTPException(status_code=500, detail="Indoor map not stored")
    return services.indoor_map_to_schema(refreshed)


@app.get("/buildings/{external_id}/indoor-map", response_model=schemas.IndoorMap)
async def get_indoor_map(external_id: str, db: AsyncSession = Depends(get_db)):
    building = await services.get_building_by_external_id(db, external_id)
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
    if not building.indoor_map:
        raise HTTPException(status_code=404, detail="Indoor map not defined")
    return services.indoor_map_to_schema(building.indoor_map)


@app.post("/buildings/{external_id}/indoor-map/paths", response_model=schemas.IndoorPathDetail)
async def record_indoor_path_endpoint(
    external_id: str,
    path: schemas.IndoorPathCreate,
    db: AsyncSession = Depends(get_db),
):
    building = await services.get_building_by_external_id(db, external_id)
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
    try:
        indoor_path = await services.record_indoor_path(db, building.id, path)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return services.indoor_path_to_detail(indoor_path)


@app.get("/indoor-paths/{path_id}", response_model=schemas.IndoorPathDetail)
async def get_indoor_path(path_id: int, db: AsyncSession = Depends(get_db)):
    indoor_path = await services.get_indoor_path(db, path_id)
    if not indoor_path:
        raise HTTPException(status_code=404, detail="Indoor path not found")
    return services.indoor_path_to_detail(indoor_path)


@app.post("/buildings/{external_id}/trajectories", response_model=schemas.SyncResponse)
async def submit_trajectory(
    external_id: str,
    trajectory: schemas.TrajectoryCreate,
    db: AsyncSession = Depends(get_db)
):
    building = await services.get_building_by_external_id(db, external_id)
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
    delivered_time = datetime.utcfromtimestamp(trajectory.delivered_at / 1000) if trajectory.delivered_at else None
    await services.record_trajectory(
        db,
        building,
        trajectory.courier_id,
        [p.model_dump() for p in trajectory.points],
        delivered_time,
    )
    return schemas.SyncResponse()


@app.post("/entrances/{entrance_id}/domofon", response_model=schemas.Entrance)
async def validate_domofon_code(
    entrance_id: int,
    validation: schemas.DomofonValidationRequest,
    db: AsyncSession = Depends(get_db)
):
    updated = await services.update_domofon_code(db, entrance_id, validation.code, validation.success)
    return schemas.Entrance.from_orm(updated)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    if await services.is_token_blacklisted(db, token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has been revoked")
    payload = services.decode_access_token(token)
    if not payload.sub:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = await services.get_user_by_email(db, payload.sub)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def require_role(*roles: schemas.UserRole):
    async def dependency(current_user=Depends(get_current_user)):
        if schemas.UserRole(current_user.role) not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return current_user

    return dependency


@app.post("/auth/register", response_model=schemas.UserRead)
async def register_user(payload: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    user = await services.create_user(db, payload, auto_activate=False)
    return schemas.UserRead.model_validate(user)


@app.post("/auth/token", response_model=schemas.TokenPair)
async def login_for_access_token(payload: schemas.UserLogin, db: AsyncSession = Depends(get_db)):
    user = await services.authenticate_user(db, payload.email, payload.password)
    access = services.create_access_token(user.email, user.role)
    refresh = services.create_refresh_token(user.email, user.role)
    return schemas.TokenPair(access_token=access, refresh_token=refresh)


@app.post("/auth/refresh", response_model=schemas.TokenPair)
async def refresh_access_token(payload: schemas.RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    if await services.is_token_blacklisted(db, payload.refresh_token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has been revoked")
    token_data = services.decode_refresh_token(payload.refresh_token)
    if not token_data.sub:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = await services.get_user_by_email(db, token_data.sub)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    await services.blacklist_token(db, payload.refresh_token)
    access = services.create_access_token(user.email, user.role)
    refresh = services.create_refresh_token(user.email, user.role)
    return schemas.TokenPair(access_token=access, refresh_token=refresh)


@app.post("/auth/logout")
async def logout(
    payload: schemas.LogoutRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    await services.blacklist_token(db, payload.token)
    return {"message": "Logged out"}


@app.get("/auth/me", response_model=schemas.UserRead)
async def read_current_user(current_user=Depends(get_current_user)):
    return schemas.UserRead.model_validate(current_user)


@app.patch("/auth/me", response_model=schemas.UserRead)
async def update_current_user(
    payload: schemas.UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    user = await services.update_user_profile(db, current_user, payload)
    return schemas.UserRead.model_validate(user)


@app.get("/admin/users/pending", response_model=list[schemas.UserRead])
async def list_pending_users(db: AsyncSession = Depends(get_db), _: schemas.UserRead = Depends(require_role(schemas.UserRole.admin))):
    users = await services.list_pending_users(db)
    return [schemas.UserRead.model_validate(user) for user in users]


@app.post("/admin/users/{user_id}/approve", response_model=schemas.UserRead)
async def approve_user(user_id: int, db: AsyncSession = Depends(get_db), _: schemas.UserRead = Depends(require_role(schemas.UserRole.admin))):
    user = await services.set_user_active(db, user_id, True)
    return schemas.UserRead.model_validate(user)


@app.post("/admin/users/{user_id}/deactivate", response_model=schemas.UserRead)
async def deactivate_user(user_id: int, db: AsyncSession = Depends(get_db), _: schemas.UserRead = Depends(require_role(schemas.UserRole.admin))):
    user = await services.set_user_active(db, user_id, False)
    return schemas.UserRead.model_validate(user)


@app.delete("/admin/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_account(user_id: int, db: AsyncSession = Depends(get_db), _: schemas.UserRead = Depends(require_role(schemas.UserRole.admin))):
    await services.delete_user(db, user_id)
    return None


@app.post("/auth/request-verification")
async def request_email_verification(payload: schemas.VerificationRequest, db: AsyncSession = Depends(get_db)):
    user = await services.get_user_by_email(db, payload.email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    settings = get_settings()
    token = await services.create_user_token(db, user, "email_verification", settings.verification_token_expire_minutes)
    return {"message": "Verification token generated", "token": token.token}


@app.post("/auth/confirm-verification")
async def confirm_email_verification(payload: schemas.VerificationConfirm, db: AsyncSession = Depends(get_db)):
    token = await services.consume_user_token(db, payload.token, "email_verification")
    user = await services.get_user_by_id(db, token.user_id)
    if user:
        user.is_active = True
        await db.commit()
    return {"message": "Email verified"}


@app.post("/auth/request-password-reset")
async def request_password_reset(payload: schemas.PasswordResetRequest, db: AsyncSession = Depends(get_db)):
    user = await services.get_user_by_email(db, payload.email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    settings = get_settings()
    token = await services.create_user_token(db, user, "password_reset", settings.password_reset_token_expire_minutes)
    return {"message": "Password reset token generated", "token": token.token}


@app.post("/auth/confirm-password-reset")
async def confirm_password_reset(payload: schemas.PasswordResetConfirm, db: AsyncSession = Depends(get_db)):
    token = await services.consume_user_token(db, payload.token, "password_reset")
    user = await services.get_user_by_id(db, token.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.password_hash = services.hash_password(payload.new_password)
    await db.commit()
    return {"message": "Password updated"}


@app.post("/restaurants", response_model=schemas.RestaurantRead)
async def create_restaurant_endpoint(
    payload: schemas.RestaurantCreate,
    db: AsyncSession = Depends(get_db),
    _: schemas.UserRead = Depends(require_role(schemas.UserRole.admin, schemas.UserRole.restaurant_owner)),
):
    restaurant = await services.create_restaurant(db, payload)
    return schemas.RestaurantRead.model_validate(restaurant)


@app.get("/restaurants", response_model=list[schemas.RestaurantRead])
async def list_restaurants_endpoint(
    db: AsyncSession = Depends(get_db),
    _: schemas.UserRead = Depends(require_role(schemas.UserRole.admin, schemas.UserRole.restaurant_owner, schemas.UserRole.restaurant_operator, schemas.UserRole.courier)),
):
    restaurants = await services.list_restaurants(db)
    return [schemas.RestaurantRead.model_validate(r) for r in restaurants]


@app.get("/restaurants/{restaurant_id}", response_model=schemas.RestaurantRead)
async def get_restaurant_endpoint(
    restaurant_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    restaurant = await services.get_restaurant_by_id(db, restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")
    return schemas.RestaurantRead.model_validate(restaurant)


@app.patch("/restaurants/{restaurant_id}", response_model=schemas.RestaurantRead)
async def update_restaurant_endpoint(
    restaurant_id: int,
    payload: schemas.RestaurantUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    restaurant = await services.get_restaurant_by_id(db, restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")
    ensure_restaurant_access(restaurant, current_user)
    restaurant = await services.update_restaurant(db, restaurant_id, payload)
    return schemas.RestaurantRead.model_validate(restaurant)


def ensure_restaurant_access(restaurant: models.Restaurant, current_user) -> None:
    if schemas.UserRole(current_user.role) == schemas.UserRole.admin:
        return
    if schemas.UserRole(current_user.role) not in (schemas.UserRole.restaurant_owner, schemas.UserRole.restaurant_operator) or restaurant.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")


@app.get("/restaurants/{restaurant_id}/couriers", response_model=list[schemas.UserRead])
async def list_restaurant_couriers(
    restaurant_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    restaurant = await services.get_restaurant_by_id(db, restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")
    ensure_restaurant_access(restaurant, current_user)
    couriers = await services.list_couriers_for_restaurant(db, restaurant_id)
    return [schemas.UserRead.model_validate(courier) for courier in couriers]


@app.post("/restaurants/{restaurant_id}/couriers", response_model=schemas.UserRead)
async def add_restaurant_courier(
    restaurant_id: int,
    payload: schemas.RestaurantCourierCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    restaurant = await services.get_restaurant_by_id(db, restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")
    ensure_restaurant_access(restaurant, current_user)
    courier = await services.add_courier_to_restaurant(db, restaurant, payload)
    return schemas.UserRead.model_validate(courier)


@app.delete("/restaurants/{restaurant_id}/couriers/{courier_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_restaurant_courier(
    restaurant_id: int,
    courier_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    restaurant = await services.get_restaurant_by_id(db, restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")
    ensure_restaurant_access(restaurant, current_user)
    await services.remove_courier_from_restaurant(db, restaurant_id, courier_id)
    return None


@app.post("/orders", response_model=schemas.OrderRead)
async def create_order_endpoint(
    payload: schemas.OrderCreate,
    db: AsyncSession = Depends(get_db),
    _: schemas.UserRead = Depends(require_role(schemas.UserRole.admin, schemas.UserRole.restaurant_owner, schemas.UserRole.restaurant_operator)),
):
    order = await services.create_order(db, payload)
    return schemas.OrderRead.model_validate(order)


@app.post("/orders/{order_id}/assign", response_model=schemas.OrderRead)
async def assign_order_endpoint(
    order_id: int,
    payload: schemas.OrderAssign,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role(schemas.UserRole.admin, schemas.UserRole.restaurant_owner, schemas.UserRole.restaurant_operator)),
):
    order = await services.assign_order(db, order_id, payload.courier_id)
    await services.log_order_status_change(db, order_id, schemas.OrderStatus.pending.value, schemas.OrderStatus.accepted.value, current_user.id)
    await db.refresh(order)
    return schemas.OrderRead.model_validate(order)


@app.post("/orders/batch-assign", response_model=list[schemas.OrderRead])
async def batch_assign_orders_endpoint(
    payload: schemas.OrderBatchAssign,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role(schemas.UserRole.admin, schemas.UserRole.restaurant_owner, schemas.UserRole.restaurant_operator)),
):
    orders = await services.batch_assign_orders(db, payload.order_ids, payload.courier_id, current_user.id)
    return [schemas.OrderRead.model_validate(o) for o in orders]


@app.patch("/orders/{order_id}", response_model=schemas.OrderRead)
async def update_order_details_endpoint(
    order_id: int,
    payload: schemas.OrderUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    order = await services.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if current_user.role == schemas.UserRole.restaurant_owner.value and order.restaurant_id != current_user.id:
        restaurant = await services.get_restaurant_by_id(db, current_user.id)
        if not restaurant or restaurant.id != order.restaurant_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your restaurant order")
    if current_user.role == schemas.UserRole.restaurant_operator.value and order.restaurant_id != current_user.id:
        restaurant = await services.get_restaurant_by_id(db, current_user.id)
        if not restaurant or restaurant.id != order.restaurant_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your restaurant order")
    order = await services.update_order_details(db, order_id, payload)
    return schemas.OrderRead.model_validate(order)


@app.post("/orders/{order_id}/status", response_model=schemas.OrderRead)
async def update_order_status_endpoint(
    order_id: int,
    payload: schemas.OrderStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    order = await services.update_order_status(db, order_id, payload, current_user.id)
    return schemas.OrderRead.model_validate(order)


@app.post("/orders/{order_id}/unassign", response_model=schemas.OrderRead)
async def unassign_order_endpoint(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role(schemas.UserRole.admin, schemas.UserRole.restaurant_owner, schemas.UserRole.restaurant_operator)),
):
    order = await services.unassign_order(db, order_id, current_user.id)
    return schemas.OrderRead.model_validate(order)


@app.post("/orders/{order_id}/reassign", response_model=schemas.OrderRead)
async def reassign_order_endpoint(
    order_id: int,
    payload: schemas.OrderAssign,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role(schemas.UserRole.admin, schemas.UserRole.restaurant_owner, schemas.UserRole.restaurant_operator)),
):
    order = await services.reassign_order(db, order_id, payload.courier_id, current_user.id)
    return schemas.OrderRead.model_validate(order)


@app.post("/orders/{order_id}/decline", response_model=schemas.OrderRead)
async def decline_order_endpoint(
    order_id: int,
    payload: schemas.OrderDecline,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role(schemas.UserRole.admin, schemas.UserRole.courier)),
):
    order = await services.decline_order(db, order_id, payload.reason, current_user.id)
    return schemas.OrderRead.model_validate(order)


@app.post("/orders/{order_id}/delivery-failed", response_model=schemas.OrderRead)
async def mark_delivery_failed_endpoint(
    order_id: int,
    payload: schemas.OrderDeliveryFailed,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role(schemas.UserRole.admin, schemas.UserRole.courier)),
):
    order = await services.mark_delivery_failed(db, order_id, payload, current_user.id)
    return schemas.OrderRead.model_validate(order)


@app.post("/orders/{order_id}/ready-for-pickup", response_model=schemas.OrderRead)
async def mark_ready_for_pickup_endpoint(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role(schemas.UserRole.admin, schemas.UserRole.restaurant_owner, schemas.UserRole.restaurant_operator)),
):
    order = await services.mark_order_ready_for_pickup(db, order_id, current_user.id)
    return schemas.OrderRead.model_validate(order)


@app.post("/orders/{order_id}/auto-assign", response_model=schemas.OrderRead)
async def auto_assign_order_endpoint(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role(schemas.UserRole.admin, schemas.UserRole.restaurant_owner, schemas.UserRole.restaurant_operator)),
):
    order = await services.auto_assign_order(db, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No available couriers found")
    return schemas.OrderRead.model_validate(order)


@app.get("/orders/my/summary", response_model=schemas.CourierDailySummary)
async def get_my_daily_summary(
    date: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role(schemas.UserRole.courier)),
):
    from datetime import datetime
    parsed_date = None
    if date:
        parsed_date = datetime.strptime(date, "%Y-%m-%d")
    summary = await services.get_courier_daily_summary(db, current_user.id, parsed_date)
    return summary


@app.get("/orders/my", response_model=list[schemas.OrderRead])
async def list_my_orders(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role == schemas.UserRole.courier.value:
        orders = await services.list_orders_for_courier(db, current_user.id)
    elif current_user.role == schemas.UserRole.restaurant_owner.value or current_user.role == schemas.UserRole.restaurant_operator.value:
        restaurants = await services.list_restaurants(db)
        my_rest_ids = [r.id for r in restaurants if r.owner_id == current_user.id]
        orders = []
        for rid in my_rest_ids:
            orders.extend(await services.list_orders_for_restaurant(db, rid))
    else:
        orders, _ = await services.list_orders_paginated(db)
    return [schemas.OrderRead.model_validate(o) for o in orders]


@app.get("/orders/search", response_model=schemas.PaginatedOrders)
async def search_orders(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    restaurant_id: Optional[int] = None,
    courier_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_role(schemas.UserRole.admin)),
):
    items, total = await services.list_orders_paginated(db, page, per_page, status_filter, restaurant_id, courier_id)
    return schemas.PaginatedOrders(
        items=[schemas.OrderRead.model_validate(o) for o in items],
        total=total,
        page=page,
        per_page=per_page,
    )


@app.get("/orders/{order_id}", response_model=schemas.OrderRead)
async def get_order_endpoint(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    order = await services.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if current_user.role == schemas.UserRole.courier.value and order.courier_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your order")
    if current_user.role == schemas.UserRole.restaurant_owner.value and order.restaurant_id != current_user.id:
        restaurant = await services.get_restaurant_by_id(db, current_user.id)
        if not restaurant or restaurant.id != order.restaurant_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your restaurant order")
    if current_user.role == schemas.UserRole.restaurant_operator.value and order.restaurant_id != current_user.id:
        restaurant = await services.get_restaurant_by_id(db, current_user.id)
        if not restaurant or restaurant.id != order.restaurant_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your restaurant order")
    return schemas.OrderRead.model_validate(order)


@app.get("/orders/restaurant/{restaurant_id}", response_model=list[schemas.OrderRead])
async def list_orders_for_restaurant_endpoint(
    restaurant_id: int,
    db: AsyncSession = Depends(get_db),
    _: schemas.UserRead = Depends(require_role(schemas.UserRole.admin, schemas.UserRole.restaurant_owner, schemas.UserRole.restaurant_operator)),
):
    orders = await services.list_orders_for_restaurant(db, restaurant_id)
    return [schemas.OrderRead.model_validate(o) for o in orders]


@app.get("/orders/courier/{courier_id}", response_model=list[schemas.OrderRead])
async def list_orders_for_courier_endpoint(
    courier_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role(schemas.UserRole.admin, schemas.UserRole.courier)),
):
    if schemas.UserRole(current_user.role) == schemas.UserRole.courier and current_user.id != courier_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot view other courier orders")
    orders = await services.list_orders_for_courier(db, courier_id)
    return [schemas.OrderRead.model_validate(o) for o in orders]


@app.post("/orders/{order_id}/cancel", response_model=schemas.OrderRead)
async def cancel_order_endpoint(
    order_id: int,
    payload: schemas.OrderCancel,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role(schemas.UserRole.admin, schemas.UserRole.restaurant_owner, schemas.UserRole.restaurant_operator)),
):
    order = await services.cancel_order(db, order_id, payload.reason)
    await services.log_order_status_change(db, order_id, order.status, schemas.OrderStatus.canceled.value, current_user.id)
    await db.refresh(order)
    return schemas.OrderRead.model_validate(order)


@app.post("/courier/location", response_model=schemas.CourierLocationRead)
async def update_my_location(
    payload: schemas.CourierLocationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role(schemas.UserRole.admin, schemas.UserRole.restaurant_owner, schemas.UserRole.restaurant_operator, schemas.UserRole.courier)),
):
    loc = await services.update_courier_location(db, current_user.id, payload)
    return schemas.CourierLocationRead(
        courier_id=loc.courier_id,
        latitude=loc.latitude,
        longitude=loc.longitude,
        bearing=loc.bearing,
        speed=loc.speed,
        updated_at=loc.updated_at,
    )


@app.get("/courier/{courier_id}/location", response_model=schemas.CourierLocationRead)
async def get_courier_location_endpoint(
    courier_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role(schemas.UserRole.admin, schemas.UserRole.restaurant_owner, schemas.UserRole.restaurant_operator, schemas.UserRole.courier)),
):
    loc = await services.get_courier_location(db, courier_id)
    if not loc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
    return schemas.CourierLocationRead(
        courier_id=loc.courier_id,
        latitude=loc.latitude,
        longitude=loc.longitude,
        bearing=loc.bearing,
        speed=loc.speed,
        updated_at=loc.updated_at,
    )


@app.post("/courier/status", response_model=schemas.CourierStatusRead)
async def update_courier_status_endpoint(
    payload: schemas.CourierStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role(schemas.UserRole.courier)),
):
    status = await services.update_courier_status(db, current_user.id, payload)
    return schemas.CourierStatusRead(
        courier_id=status.courier_id,
        status=schemas.CourierStatusEnum(status.status),
        updated_at=status.updated_at,
        last_online_at=status.last_online_at,
        cash_balance=status.cash_balance,
    )


@app.post("/courier/{courier_id}/collect-cash", response_model=schemas.CourierStatusRead)
async def collect_cash_from_courier_endpoint(
    courier_id: int,
    payload: schemas.CourierCashCollect,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role(schemas.UserRole.admin, schemas.UserRole.restaurant_owner)),
):
    status = await services.collect_cash_from_courier(db, courier_id, payload.amount)
    return schemas.CourierStatusRead(
        courier_id=status.courier_id,
        status=schemas.CourierStatusEnum(status.status),
        updated_at=status.updated_at,
        last_online_at=status.last_online_at,
        cash_balance=status.cash_balance,
    )


@app.get("/courier/status", response_model=schemas.CourierStatusRead)
async def get_courier_status_endpoint(
    courier_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role(schemas.UserRole.admin, schemas.UserRole.restaurant_owner, schemas.UserRole.restaurant_operator, schemas.UserRole.courier)),
):
    status = await services.get_courier_status(db, courier_id)
    if not status:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Courier status not found")
    return schemas.CourierStatusRead(
        courier_id=status.courier_id,
        status=schemas.CourierStatusEnum(status.status),
        updated_at=status.updated_at,
        last_online_at=status.last_online_at,
        cash_balance=status.cash_balance,
    )


@app.get("/public/tracking/{tracking_hash}", response_model=schemas.OrderTracking)
@limiter.limit("10/minute")
async def public_tracking_endpoint(
    tracking_hash: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    return await services.get_order_tracking_data(db, tracking_hash)
