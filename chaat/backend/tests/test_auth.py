import pytest

@pytest.mark.anyio
async def test_register_duplicate_and_login_wrong_password(client):
    r = await client.post("/auth/register", json={"email": "a@example.com", "password": "secret123"})
    assert r.status_code == 201

    r = await client.post("/auth/register", json={"email": "a@example.com", "password": "secret123"})
    assert r.status_code == 400

    r = await client.post("/auth/login", data={"username": "a@example.com", "password": "wrong"})
    assert r.status_code == 401
