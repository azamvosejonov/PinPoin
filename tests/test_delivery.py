import pytest
from unittest.mock import patch, AsyncMock

@pytest.mark.asyncio
async def test_courier_toggle_availability(client, courier_token):
    """Kuryer is_available ni almashtira oladi"""
    # Default True — False ga o'tadi
    r = await client.patch("/api/v1/delivery/availability",
        headers={"Authorization": f"Bearer {courier_token}"}
    )
    assert r.status_code == 200
    assert r.json()["is_available"] is False

    # Qayta bosadi — True ga qaytadi
    r = await client.patch("/api/v1/delivery/availability",
        headers={"Authorization": f"Bearer {courier_token}"}
    )
    assert r.status_code == 200
    assert r.json()["is_available"] is True

@pytest.mark.asyncio
async def test_customer_cannot_toggle_availability(client, customer_token):
    r = await client.patch("/api/v1/delivery/availability",
        headers={"Authorization": f"Bearer {customer_token}"}
    )
    assert r.status_code == 403

@pytest.mark.asyncio
async def test_courier_accept_order(client, customer_token, courier_token, restaurant_id, menu_item_id):
    """Kuryer buyurtmani qabul qiladi"""
    # Buyurtma yaratish va kuryerni tayinlash
    courier_me = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {courier_token}"})
    courier_id = courier_me.json()["id"]
    fake_courier = {"courier_id": courier_id, "lat": 41.30, "lon": 69.24}

    with patch("app.api.v1.endpoints.orders.get_all_available_couriers", AsyncMock(return_value=[fake_courier])), \
         patch("app.services.ai_service.analyze_order", AsyncMock(return_value={})), \
         patch("app.services.notification_service.redis_client") as mock_redis:
        mock_redis.publish = AsyncMock()
        order = await client.post("/api/v1/orders/", json={
            "restaurant_id": restaurant_id,
            "delivery_address": "Test",
            "delivery_lat": 41.3, "delivery_lon": 69.2,
            "items": [{"menu_item_id": menu_item_id, "quantity": 1}]
        }, headers={"Authorization": f"Bearer {customer_token}"})
    order_id = order.json()["id"]

    with patch("app.services.notification_service.redis_client") as mock_redis:
        mock_redis.publish = AsyncMock()
        r = await client.post(f"/api/v1/delivery/orders/{order_id}/accept",
            headers={"Authorization": f"Bearer {courier_token}"}
        )

    assert r.status_code == 200
    assert r.json()["status"] == "confirmed"
    # Mijozga notification ketganini tekshirish
    mock_redis.publish.assert_called_once()

@pytest.mark.asyncio
async def test_courier_accept_wrong_order(client, courier_token, customer_token, restaurant_id, menu_item_id):
    """Kuryer o'ziga tegishli bo'lmagan buyurtmani qabul qila olmaydi"""
    with patch("app.api.v1.endpoints.orders.get_all_available_couriers", AsyncMock(return_value=[])), \
         patch("app.services.ai_service.analyze_order", AsyncMock(return_value={})), \
         patch("app.services.notification_service.redis_client") as mock_redis:
        mock_redis.publish = AsyncMock()
        order = await client.post("/api/v1/orders/", json={
            "restaurant_id": restaurant_id,
            "delivery_address": "Test",
            "delivery_lat": 41.3, "delivery_lon": 69.2,
            "items": [{"menu_item_id": menu_item_id, "quantity": 1}]
        }, headers={"Authorization": f"Bearer {customer_token}"})
    order_id = order.json()["id"]

    # Boshqa kuryer qabul qilmoqchi
    r = await client.post(f"/api/v1/delivery/orders/{order_id}/accept",
        headers={"Authorization": f"Bearer {courier_token}"}
    )
    assert r.status_code == 404

@pytest.mark.asyncio
async def test_accept_already_confirmed_order_fails(client, customer_token, courier_token, restaurant_id, menu_item_id):
    """Allaqachon confirmed buyurtmani qayta qabul qilib bo'lmaydi"""
    courier_me = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {courier_token}"})
    courier_id = courier_me.json()["id"]
    fake_courier = {"courier_id": courier_id, "lat": 41.30, "lon": 69.24}

    with patch("app.api.v1.endpoints.orders.get_all_available_couriers", AsyncMock(return_value=[fake_courier])), \
         patch("app.services.ai_service.analyze_order", AsyncMock(return_value={})), \
         patch("app.services.notification_service.redis_client") as mock_redis:
        mock_redis.publish = AsyncMock()
        order = await client.post("/api/v1/orders/", json={
            "restaurant_id": restaurant_id,
            "delivery_address": "Test",
            "delivery_lat": 41.3, "delivery_lon": 69.2,
            "items": [{"menu_item_id": menu_item_id, "quantity": 1}]
        }, headers={"Authorization": f"Bearer {customer_token}"})
    order_id = order.json()["id"]

    with patch("app.services.notification_service.redis_client") as mock_redis:
        mock_redis.publish = AsyncMock()
        await client.post(f"/api/v1/delivery/orders/{order_id}/accept",
            headers={"Authorization": f"Bearer {courier_token}"}
        )
        # Ikkinchi marta qabul qilmoqchi
        r = await client.post(f"/api/v1/delivery/orders/{order_id}/accept",
            headers={"Authorization": f"Bearer {courier_token}"}
        )
    assert r.status_code == 400
