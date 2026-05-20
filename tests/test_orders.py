import pytest
from unittest.mock import patch, AsyncMock

@pytest.mark.asyncio
async def test_create_order(client, customer_token, restaurant_id, menu_item_id):
    with patch("app.api.v1.endpoints.orders.get_all_available_couriers", AsyncMock(return_value=[])), \
         patch("app.services.ai_service.analyze_order", AsyncMock(return_value={"urgency": "low"})), \
         patch("app.services.notification_service.redis_client") as mock_redis:
        mock_redis.publish = AsyncMock()
        r = await client.post("/api/v1/orders/", json={
            "restaurant_id": restaurant_id,
            "delivery_address": "Yunusobod 5-kvartal",
            "delivery_lat": 41.36, "delivery_lon": 69.28,
            "items": [{"menu_item_id": menu_item_id, "quantity": 2}]
        }, headers={"Authorization": f"Bearer {customer_token}"})
    assert r.status_code == 201
    data = r.json()
    assert "tracking_token" in data
    assert "tracking_link" in data
    assert data["items_price"] == 50000
    assert data["delivery_fee"] == 5000
    assert data["total_price"] == 55000

@pytest.mark.asyncio
async def test_create_order_forbidden_for_courier(client, courier_token, restaurant_id, menu_item_id):
    r = await client.post("/api/v1/orders/", json={
        "restaurant_id": restaurant_id,
        "delivery_address": "Test",
        "delivery_lat": 41.3, "delivery_lon": 69.2,
        "items": [{"menu_item_id": menu_item_id, "quantity": 1}]
    }, headers={"Authorization": f"Bearer {courier_token}"})
    assert r.status_code == 403

@pytest.mark.asyncio
async def test_my_orders(client, customer_token, restaurant_id, menu_item_id):
    with patch("app.api.v1.endpoints.orders.get_all_available_couriers", AsyncMock(return_value=[])), \
         patch("app.services.ai_service.analyze_order", AsyncMock(return_value={})), \
         patch("app.services.notification_service.redis_client") as mock_redis:
        mock_redis.publish = AsyncMock()
        await client.post("/api/v1/orders/", json={
            "restaurant_id": restaurant_id,
            "delivery_address": "Test",
            "delivery_lat": 41.3, "delivery_lon": 69.2,
            "items": [{"menu_item_id": menu_item_id, "quantity": 1}]
        }, headers={"Authorization": f"Bearer {customer_token}"})
    r = await client.get("/api/v1/orders/my/list", headers={"Authorization": f"Bearer {customer_token}"})
    assert r.status_code == 200
    assert len(r.json()) >= 1

@pytest.mark.asyncio
async def test_cancel_order(client, customer_token, restaurant_id, menu_item_id):
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

    with patch("app.services.notification_service.redis_client") as mock_redis:
        mock_redis.publish = AsyncMock()
        r = await client.post(f"/api/v1/orders/{order_id}/cancel",
            json={"reason": "Fikrim o'zgardi"},
            headers={"Authorization": f"Bearer {customer_token}"}
        )
    assert r.status_code == 200
    assert r.json()["ok"] is True

@pytest.mark.asyncio
async def test_cancel_delivered_order_fails(client, customer_token, restaurant_id, menu_item_id):
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

    # Admin yaratib delivered qilamiz
    await client.post("/api/v1/auth/register", json={
        "full_name": "Admin4", "phone": "+998933333333",
        "password": "admin1234", "role": "admin"
    })
    admin_login = await client.post("/api/v1/auth/login", json={"phone": "+998933333333", "password": "admin1234"})
    admin_token = admin_login.json()["access_token"]

    with patch("app.services.notification_service.redis_client") as mock_redis:
        mock_redis.publish = AsyncMock()
        await client.patch(f"/api/v1/orders/{order_id}/status?status=delivered",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

    # Mijoz delivered buyurtmani bekor qila olmaydi
    r = await client.post(f"/api/v1/orders/{order_id}/cancel",
        json={"reason": "Test"},
        headers={"Authorization": f"Bearer {customer_token}"}
    )
    assert r.status_code == 400

@pytest.mark.asyncio
async def test_update_payment(client, customer_token, restaurant_id, menu_item_id):
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
    r = await client.patch(f"/api/v1/orders/{order_id}/payment",
        json={"payment_method": "cash"},
        headers={"Authorization": f"Bearer {customer_token}"}
    )
    assert r.status_code == 200
    assert r.json()["payment_status"] == "paid"

@pytest.mark.asyncio
async def test_courier_earnings(client, courier_token):
    r = await client.get("/api/v1/orders/courier/earnings",
        headers={"Authorization": f"Bearer {courier_token}"}
    )
    assert r.status_code == 200
    assert "total_earned" in r.json()
