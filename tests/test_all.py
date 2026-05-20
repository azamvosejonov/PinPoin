import pytest
from unittest.mock import patch, AsyncMock

# ── Admin ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_admin_stats(client, admin_token):
    r = await client.get("/api/v1/admin/stats", headers={"Authorization": f"Bearer {admin_token}"})
    assert r.status_code == 200
    data = r.json()
    assert "total_users" in data
    assert "total_orders" in data
    assert "total_revenue" in data

@pytest.mark.asyncio
async def test_admin_list_users(client, admin_token, customer_token):
    r = await client.get("/api/v1/admin/users", headers={"Authorization": f"Bearer {admin_token}"})
    assert r.status_code == 200
    assert isinstance(r.json(), list)

@pytest.mark.asyncio
async def test_admin_list_users_by_role(client, admin_token):
    r = await client.get("/api/v1/admin/users?role=customer", headers={"Authorization": f"Bearer {admin_token}"})
    assert r.status_code == 200

@pytest.mark.asyncio
async def test_admin_forbidden_for_customer(client, customer_token):
    r = await client.get("/api/v1/admin/stats", headers={"Authorization": f"Bearer {customer_token}"})
    assert r.status_code == 403

@pytest.mark.asyncio
async def test_admin_update_user(client, admin_token, customer_token):
    me = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {customer_token}"})
    user_id = me.json()["id"]
    r = await client.patch(f"/api/v1/admin/users/{user_id}",
        json={"is_active": False},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert r.status_code == 200
    assert r.json()["is_active"] is False

@pytest.mark.asyncio
async def test_admin_restaurants(client, admin_token, restaurant_id):
    r = await client.get("/api/v1/admin/restaurants", headers={"Authorization": f"Bearer {admin_token}"})
    assert r.status_code == 200
    assert len(r.json()) >= 1

@pytest.mark.asyncio
async def test_admin_orders(client, admin_token):
    r = await client.get("/api/v1/admin/orders", headers={"Authorization": f"Bearer {admin_token}"})
    assert r.status_code == 200

# ── Staff ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_add_courier(client, restaurant_token):
    r = await client.post("/api/v1/staff/couriers", json={
        "full_name": "Yangi Kuryer", "phone": "+998909999999", "vehicle_type": "motorcycle"
    }, headers={"Authorization": f"Bearer {restaurant_token}"})
    assert r.status_code == 201
    assert "plain_password" in r.json()

@pytest.mark.asyncio
async def test_add_courier_forbidden_for_customer(client, customer_token):
    r = await client.post("/api/v1/staff/couriers", json={
        "full_name": "Test", "phone": "+998908888888"
    }, headers={"Authorization": f"Bearer {customer_token}"})
    assert r.status_code == 403

@pytest.mark.asyncio
async def test_my_couriers(client, restaurant_token):
    await client.post("/api/v1/staff/couriers", json={
        "full_name": "Kuryer 1", "phone": "+998907777777"
    }, headers={"Authorization": f"Bearer {restaurant_token}"})
    r = await client.get("/api/v1/staff/couriers", headers={"Authorization": f"Bearer {restaurant_token}"})
    assert r.status_code == 200
    assert len(r.json()) >= 1

@pytest.mark.asyncio
async def test_reset_courier_password(client, restaurant_token):
    add = await client.post("/api/v1/staff/couriers", json={
        "full_name": "Kuryer Reset", "phone": "+998906666666"
    }, headers={"Authorization": f"Bearer {restaurant_token}"})
    courier_id = add.json()["id"]
    r = await client.patch(f"/api/v1/staff/couriers/{courier_id}/reset-password",
        headers={"Authorization": f"Bearer {restaurant_token}"}
    )
    assert r.status_code == 200
    assert "new_password" in r.json()

@pytest.mark.asyncio
async def test_toggle_courier(client, restaurant_token):
    add = await client.post("/api/v1/staff/couriers", json={
        "full_name": "Kuryer Toggle", "phone": "+998905555555"
    }, headers={"Authorization": f"Bearer {restaurant_token}"})
    courier_id = add.json()["id"]
    r = await client.patch(f"/api/v1/staff/couriers/{courier_id}/toggle",
        headers={"Authorization": f"Bearer {restaurant_token}"}
    )
    assert r.status_code == 200
    assert r.json()["is_active"] is False

@pytest.mark.asyncio
async def test_staff_overview(client, restaurant_token):
    r = await client.get("/api/v1/staff/overview", headers={"Authorization": f"Bearer {restaurant_token}"})
    assert r.status_code == 200
    assert "restaurants" in r.json()
    assert "unassigned_couriers" in r.json()

# ── Support ───────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_ticket(client, customer_token):
    r = await client.post("/api/v1/support/tickets", json={
        "category": "delivery", "subject": "Kech keldi", "message": "30 daqiqa kechikdi"
    }, headers={"Authorization": f"Bearer {customer_token}"})
    assert r.status_code == 201
    assert r.json()["status"] == "open"

@pytest.mark.asyncio
async def test_my_tickets(client, customer_token):
    await client.post("/api/v1/support/tickets", json={
        "category": "other", "subject": "Test", "message": "Test xabar"
    }, headers={"Authorization": f"Bearer {customer_token}"})
    r = await client.get("/api/v1/support/tickets", headers={"Authorization": f"Bearer {customer_token}"})
    assert r.status_code == 200
    assert len(r.json()) >= 1

@pytest.mark.asyncio
async def test_send_message_to_ticket(client, customer_token):
    with patch("app.api.v1.endpoints.support.manager.broadcast_to_ticket", AsyncMock()):
        ticket = await client.post("/api/v1/support/tickets", json={
            "category": "other", "subject": "Test", "message": "Birinchi xabar"
        }, headers={"Authorization": f"Bearer {customer_token}"})
        ticket_id = ticket.json()["id"]
        r = await client.post(f"/api/v1/support/tickets/{ticket_id}/messages",
            json={"message": "Ikkinchi xabar"},
            headers={"Authorization": f"Bearer {customer_token}"}
        )
    assert r.status_code == 201

@pytest.mark.asyncio
async def test_admin_sees_all_tickets(client, admin_token, customer_token):
    await client.post("/api/v1/support/tickets", json={
        "category": "other", "subject": "Test", "message": "Test"
    }, headers={"Authorization": f"Bearer {customer_token}"})
    r = await client.get("/api/v1/support/tickets", headers={"Authorization": f"Bearer {admin_token}"})
    assert r.status_code == 200
    assert len(r.json()) >= 1

@pytest.mark.asyncio
async def test_update_ticket_status(client, admin_token, customer_token):
    with patch("app.api.v1.endpoints.support.manager.broadcast_to_ticket", AsyncMock()):
        ticket = await client.post("/api/v1/support/tickets", json={
            "category": "other", "subject": "Test", "message": "Test"
        }, headers={"Authorization": f"Bearer {customer_token}"})
        ticket_id = ticket.json()["id"]
        r = await client.patch(f"/api/v1/support/tickets/{ticket_id}/status",
            json={"status": "resolved"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
    assert r.status_code == 200
    assert r.json()["status"] == "resolved"

# ── Buildings ─────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_building(client, restaurant_token):
    r = await client.post("/api/v1/buildings/", json={
        "address": "Yunusobod 5-kvartal 12-uy",
        "lat": 41.36, "lon": 69.28,
        "total_floors": 9, "has_elevator": True
    }, headers={"Authorization": f"Bearer {restaurant_token}"})
    assert r.status_code == 201
    assert r.json()["has_elevator"] is True

@pytest.mark.asyncio
async def test_save_apartment_access(client, customer_token, restaurant_token):
    building = await client.post("/api/v1/buildings/", json={
        "address": "Test bino", "lat": 41.3, "lon": 69.2,
        "total_floors": 5, "has_elevator": False
    }, headers={"Authorization": f"Bearer {restaurant_token}"})
    building_id = building.json()["id"]
    r = await client.post("/api/v1/buildings/apartment-access", json={
        "building_id": building_id, "apartment_number": "42",
        "floor": 4, "door_code": "1234"
    }, headers={"Authorization": f"Bearer {customer_token}"})
    assert r.status_code == 201
    assert r.json()["has_door_code"] is True

@pytest.mark.asyncio
async def test_get_apartment_access_decrypted(client, customer_token, restaurant_token):
    building = await client.post("/api/v1/buildings/", json={
        "address": "Test bino 2", "lat": 41.3, "lon": 69.2,
        "total_floors": 5, "has_elevator": False
    }, headers={"Authorization": f"Bearer {restaurant_token}"})
    building_id = building.json()["id"]
    await client.post("/api/v1/buildings/apartment-access", json={
        "building_id": building_id, "apartment_number": "15",
        "floor": 2, "door_code": "5678"
    }, headers={"Authorization": f"Bearer {customer_token}"})
    r = await client.get(f"/api/v1/buildings/apartment-access/{building_id}",
        headers={"Authorization": f"Bearer {customer_token}"}
    )
    assert r.status_code == 200
    assert r.json()[0]["door_code"] == "5678"

# ── Integration / API Key ─────────────────────────────

@pytest.mark.asyncio
async def test_create_api_key(client, restaurant_token):
    r = await client.post("/api/v1/integration/api-keys?name=MyPOS",
        headers={"Authorization": f"Bearer {restaurant_token}"}
    )
    assert r.status_code == 201
    assert r.json()["key"].startswith("pp_")

@pytest.mark.asyncio
async def test_list_api_keys(client, restaurant_token):
    await client.post("/api/v1/integration/api-keys?name=Key1",
        headers={"Authorization": f"Bearer {restaurant_token}"}
    )
    r = await client.get("/api/v1/integration/api-keys",
        headers={"Authorization": f"Bearer {restaurant_token}"}
    )
    assert r.status_code == 200
    assert len(r.json()) >= 1

@pytest.mark.asyncio
async def test_revoke_api_key(client, restaurant_token):
    create = await client.post("/api/v1/integration/api-keys?name=ToRevoke",
        headers={"Authorization": f"Bearer {restaurant_token}"}
    )
    key_id = create.json()["id"]
    r = await client.delete(f"/api/v1/integration/api-keys/{key_id}",
        headers={"Authorization": f"Bearer {restaurant_token}"}
    )
    assert r.status_code == 200

@pytest.mark.asyncio
async def test_external_order_with_api_key(client, restaurant_token, restaurant_id):
    key_r = await client.post("/api/v1/integration/api-keys?name=POS",
        headers={"Authorization": f"Bearer {restaurant_token}"}
    )
    api_key = key_r.json()["key"]
    with patch("app.api.v1.endpoints.integration.get_all_available_couriers", AsyncMock(return_value=[])):
        r = await client.post("/api/v1/integration/orders", json={
            "delivery_address": "Chilonzor 9-kvartal",
            "delivery_lat": 41.28, "delivery_lon": 69.20,
            "items": [{"name": "Osh", "quantity": 1, "price": 25000}]
        }, headers={"X-Api-Key": api_key})
    assert r.status_code == 201
    assert "tracking_link" in r.json()

@pytest.mark.asyncio
async def test_external_order_invalid_key(client):
    r = await client.post("/api/v1/integration/orders", json={
        "delivery_address": "Test",
        "delivery_lat": 41.0, "delivery_lon": 69.0,
        "items": [{"name": "Test", "quantity": 1, "price": 10000}]
    }, headers={"X-Api-Key": "pp_invalid_key"})
    assert r.status_code == 401

# ── Services (unit) ───────────────────────────────────

def test_fuel_cost_calculation():
    from app.services.fuel_service import calculate_fuel_cost
    result = calculate_fuel_cost(10.0)
    assert result["distance_km"] == 10.0
    assert result["cost_uzs"] == 5000
    assert result["price_per_km"] == 500

def test_fuel_cost_zero():
    from app.services.fuel_service import calculate_fuel_cost
    result = calculate_fuel_cost(0)
    assert result["cost_uzs"] == 0

def test_find_nearest_courier():
    from app.services.map_service import find_nearest_courier
    couriers = [
        {"courier_id": 1, "lat": 41.30, "lon": 69.25},
        {"courier_id": 2, "lat": 41.35, "lon": 69.30},
        {"courier_id": 3, "lat": 41.29, "lon": 69.24},
    ]
    nearest = find_nearest_courier(couriers, 41.29, 69.24)
    assert nearest["courier_id"] == 3

def test_find_nearest_courier_empty():
    from app.services.map_service import find_nearest_courier
    assert find_nearest_courier([], 41.0, 69.0) is None

def test_calculate_distance():
    from app.services.map_service import calculate_distance
    dist = calculate_distance(41.299, 69.240, 41.299, 69.240)
    assert dist == 0.0

def test_encrypt_decrypt():
    from app.core.security import encrypt, decrypt
    original = "1234"
    encrypted = encrypt(original)
    assert encrypted != original
    assert decrypt(encrypted) == original
