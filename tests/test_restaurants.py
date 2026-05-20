import pytest

@pytest.mark.asyncio
async def test_create_restaurant(client, restaurant_token):
    r = await client.post("/api/v1/restaurants/", json={
        "name": "Osh Markazi", "address": "Chilonzor",
        "lat": 41.29, "lon": 69.24,
        "open_time": "09:00", "close_time": "22:00",
        "delivery_fee": 5000, "min_order_price": 20000
    }, headers={"Authorization": f"Bearer {restaurant_token}"})
    assert r.status_code == 201
    assert r.json()["name"] == "Osh Markazi"
    assert r.json()["delivery_fee"] == 5000

@pytest.mark.asyncio
async def test_create_restaurant_forbidden_for_customer(client, customer_token):
    r = await client.post("/api/v1/restaurants/", json={
        "name": "Test", "address": "Test",
        "lat": 41.0, "lon": 69.0,
        "open_time": "09:00", "close_time": "22:00",
        "delivery_fee": 0, "min_order_price": 0
    }, headers={"Authorization": f"Bearer {customer_token}"})
    assert r.status_code == 403

@pytest.mark.asyncio
async def test_list_restaurants(client, restaurant_id):
    r = await client.get("/api/v1/restaurants/")
    assert r.status_code == 200
    assert len(r.json()) >= 1

@pytest.mark.asyncio
async def test_add_menu_item(client, restaurant_token, restaurant_id):
    r = await client.post(f"/api/v1/restaurants/{restaurant_id}/menu", json={
        "name": "Lag'mon", "price": 30000, "calories": 600, "temperature_sensitive": True
    }, headers={"Authorization": f"Bearer {restaurant_token}"})
    assert r.status_code == 201
    assert r.json()["name"] == "Lag'mon"

@pytest.mark.asyncio
async def test_get_menu(client, restaurant_id, menu_item_id):
    r = await client.get(f"/api/v1/restaurants/{restaurant_id}/menu")
    assert r.status_code == 200
    assert len(r.json()) >= 1

@pytest.mark.asyncio
async def test_add_menu_wrong_restaurant(client, restaurant_token):
    r = await client.post("/api/v1/restaurants/9999/menu", json={
        "name": "Test", "price": 10000
    }, headers={"Authorization": f"Bearer {restaurant_token}"})
    assert r.status_code == 403
