import pytest

@pytest.mark.asyncio
async def test_register(client):
    r = await client.post("/api/v1/auth/register", json={
        "full_name": "Ali Valiyev", "phone": "+998901234567",
        "password": "secret123", "role": "customer"
    })
    assert r.status_code == 201
    assert r.json()["phone"] == "+998901234567"
    assert r.json()["role"] == "customer"

@pytest.mark.asyncio
async def test_register_duplicate_phone(client):
    data = {"full_name": "Ali", "phone": "+998901234567", "password": "secret123", "role": "customer"}
    await client.post("/api/v1/auth/register", json=data)
    r = await client.post("/api/v1/auth/register", json=data)
    assert r.status_code == 400

@pytest.mark.asyncio
async def test_login_success(client):
    await client.post("/api/v1/auth/register", json={
        "full_name": "Ali", "phone": "+998901234567", "password": "secret123", "role": "customer"
    })
    r = await client.post("/api/v1/auth/login", json={"phone": "+998901234567", "password": "secret123"})
    assert r.status_code == 200
    assert "access_token" in r.json()
    assert "refresh_token" in r.json()

@pytest.mark.asyncio
async def test_login_wrong_password(client):
    await client.post("/api/v1/auth/register", json={
        "full_name": "Ali", "phone": "+998901234567", "password": "secret123", "role": "customer"
    })
    r = await client.post("/api/v1/auth/login", json={"phone": "+998901234567", "password": "wrong"})
    assert r.status_code == 401

@pytest.mark.asyncio
async def test_refresh_token(client):
    await client.post("/api/v1/auth/register", json={
        "full_name": "Ali", "phone": "+998901234567", "password": "secret123", "role": "customer"
    })
    login = await client.post("/api/v1/auth/login", json={"phone": "+998901234567", "password": "secret123"})
    r = await client.post("/api/v1/auth/refresh", json={"refresh_token": login.json()["refresh_token"]})
    assert r.status_code == 200
    assert "access_token" in r.json()

@pytest.mark.asyncio
async def test_me(client, customer_token):
    r = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {customer_token}"})
    assert r.status_code == 200
    assert r.json()["role"] == "customer"

@pytest.mark.asyncio
async def test_change_password(client, customer_token):
    r = await client.post("/api/v1/auth/change-password",
        json={"old_password": "test1234", "new_password": "newpass123"},
        headers={"Authorization": f"Bearer {customer_token}"}
    )
    assert r.status_code == 200

@pytest.mark.asyncio
async def test_change_password_wrong_old(client, customer_token):
    r = await client.post("/api/v1/auth/change-password",
        json={"old_password": "wrongpass", "new_password": "newpass123"},
        headers={"Authorization": f"Bearer {customer_token}"}
    )
    assert r.status_code == 400

@pytest.mark.asyncio
async def test_unauthorized_without_token(client):
    r = await client.get("/api/v1/auth/me")
    assert r.status_code == 401
