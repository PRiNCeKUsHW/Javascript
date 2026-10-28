import pytest


async def test_register_returns_201_without_password(client):
    r = await client.post("/auth/register",
                          json={"email": "riya@example.com", "password": "secret123"})
    assert r.status_code == 201
    assert r.json() == {"id": 1, "email": "riya@example.com"}


async def test_duplicate_email_is_409(client):
    body = {"email": "riya@example.com", "password": "secret123"}
    await client.post("/auth/register", json=body)
    r = await client.post("/auth/register", json=body)
    assert r.status_code == 409


@pytest.mark.parametrize("body", [
    {"email": "not-an-email", "password": "secret123"},
    {"email": "riya@example.com", "password": "short"},
    {"email": "riya@example.com"},
])
async def test_invalid_signup_is_422(client, body):
    r = await client.post("/auth/register", json=body)
    assert r.status_code == 422


async def test_wrong_password_is_401(client, auth_headers):
    await auth_headers()
    r = await client.post("/auth/token",
                          data={"username": "riya@example.com", "password": "wrong-pass"})
    assert r.status_code == 401


async def test_tasks_need_a_token(client):
    r = await client.get("/tasks")
    assert r.status_code == 401
