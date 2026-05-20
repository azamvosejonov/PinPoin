import pytest
import json
from unittest.mock import patch, AsyncMock

# ── Notification service unit testlari ───────────────

@pytest.mark.asyncio
async def test_notify_order_status_publishes():
    with patch("app.services.notification_service.redis_client") as mock_redis:
        mock_redis.publish = AsyncMock()
        from app.services.notification_service import notify_order_status
        await notify_order_status(user_id=1, order_id=42, status="delivered")
        mock_redis.publish.assert_called_once()
        channel, payload = mock_redis.publish.call_args[0]
        assert channel == "notify:user:1"
        data = json.loads(payload)
        assert data["type"] == "order_status"
        assert data["data"]["order_id"] == 42
        assert data["data"]["status"] == "delivered"

@pytest.mark.asyncio
async def test_notify_courier_assigned_publishes():
    with patch("app.services.notification_service.redis_client") as mock_redis:
        mock_redis.publish = AsyncMock()
        from app.services.notification_service import notify_courier_assigned
        await notify_courier_assigned(courier_id=5, order_id=10, restaurant_name="Osh Markazi")
        mock_redis.publish.assert_called_once()
        channel, payload = mock_redis.publish.call_args[0]
        assert channel == "notify:user:5"
        data = json.loads(payload)
        assert data["type"] == "new_order"
        assert "Osh Markazi" in data["body"]

@pytest.mark.asyncio
async def test_notify_support_reply_publishes():
    with patch("app.services.notification_service.redis_client") as mock_redis:
        mock_redis.publish = AsyncMock()
        from app.services.notification_service import notify_support_reply
        await notify_support_reply(user_id=3, ticket_id=7)
        mock_redis.publish.assert_called_once()
        channel, payload = mock_redis.publish.call_args[0]
        assert channel == "notify:user:3"
        data = json.loads(payload)
        assert data["type"] == "support_reply"
        assert data["data"]["ticket_id"] == 7

def test_all_order_statuses_have_messages():
    from app.services.notification_service import ORDER_MESSAGES
    for s in ["confirmed", "preparing", "picked_up", "on_the_way", "delivered", "cancelled"]:
        assert s in ORDER_MESSAGES
        title, body = ORDER_MESSAGES[s]
        assert len(title) > 0 and len(body) > 0

# ── Token validatsiya testi (sync) ────────────────────

def test_notification_ws_invalid_token_rejected():
    """Noto'g'ri token JWTError berishi kerak"""
    from jose import jwt, JWTError
    from app.core.config import settings
    try:
        jwt.decode("invalid_token", settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert False, "Noto'g'ri token qabul qilinmasligi kerak"
    except JWTError:
        pass

def test_notification_ws_valid_token_decoded(customer_token):
    """To'g'ri token muvaffaqiyatli decode bo'lishi kerak"""
    from jose import jwt
    from app.core.config import settings
    payload = jwt.decode(customer_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload.get("type") == "access"
    assert payload.get("sub") is not None

# ── Integratsiya: order yaratilganda notification ─────

@pytest.mark.asyncio
async def test_order_creation_notifies_courier(client, customer_token, restaurant_id, menu_item_id):
    fake_courier = {"courier_id": 99, "lat": 41.30, "lon": 69.24}
    with patch("app.api.v1.endpoints.orders.get_all_available_couriers", AsyncMock(return_value=[fake_courier])), \
         patch("app.services.ai_service.analyze_order", AsyncMock(return_value={})), \
         patch("app.services.notification_service.redis_client") as mock_redis:
        mock_redis.publish = AsyncMock()
        r = await client.post("/api/v1/orders/", json={
            "restaurant_id": restaurant_id,
            "delivery_address": "Test",
            "delivery_lat": 41.3, "delivery_lon": 69.2,
            "items": [{"menu_item_id": menu_item_id, "quantity": 1}]
        }, headers={"Authorization": f"Bearer {customer_token}"})

    assert r.status_code == 201
    mock_redis.publish.assert_called_once()
    assert mock_redis.publish.call_args[0][0] == "notify:user:99"

@pytest.mark.asyncio
async def test_status_change_notifies_customer(client, customer_token, restaurant_id, menu_item_id):
    """Admin status o'zgartirsa mijozga notification ketadi"""
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

    # Admin yaratish
    await client.post("/api/v1/auth/register", json={
        "full_name": "Admin2", "phone": "+998911111111",
        "password": "admin1234", "role": "admin"
    })
    admin_login = await client.post("/api/v1/auth/login", json={"phone": "+998911111111", "password": "admin1234"})
    admin_token = admin_login.json()["access_token"]

    with patch("app.services.notification_service.redis_client") as mock_redis:
        mock_redis.publish = AsyncMock()
        r = await client.patch(
            f"/api/v1/orders/{order_id}/status?status=confirmed",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

    assert r.status_code == 200
    mock_redis.publish.assert_called_once()
    payload = json.loads(mock_redis.publish.call_args[0][1])
    assert payload["type"] == "order_status"
    assert payload["data"]["status"] == "confirmed"

# ── SSRF himoya testlari ──────────────────────────────

@pytest.mark.asyncio
async def test_webhook_ssrf_blocked(client, restaurant_token, restaurant_id):
    key_r = await client.post("/api/v1/integration/api-keys?name=POS",
        headers={"Authorization": f"Bearer {restaurant_token}"}
    )
    api_key = key_r.json()["key"]
    r = await client.post("/api/v1/integration/orders", json={
        "delivery_address": "Test",
        "delivery_lat": 41.0, "delivery_lon": 69.0,
        "items": [{"name": "Test", "quantity": 1, "price": 10000}],
        "webhook_url": "http://localhost:8080/internal"
    }, headers={"X-Api-Key": api_key})
    assert r.status_code == 422

@pytest.mark.asyncio
async def test_webhook_private_ip_blocked(client, restaurant_token, restaurant_id):
    key_r = await client.post("/api/v1/integration/api-keys?name=POS2",
        headers={"Authorization": f"Bearer {restaurant_token}"}
    )
    api_key = key_r.json()["key"]
    r = await client.post("/api/v1/integration/orders", json={
        "delivery_address": "Test",
        "delivery_lat": 41.0, "delivery_lon": 69.0,
        "items": [{"name": "Test", "quantity": 1, "price": 10000}],
        "webhook_url": "http://192.168.1.1/steal-data"
    }, headers={"X-Api-Key": api_key})
    assert r.status_code == 422
