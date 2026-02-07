import pytest
from httpx import AsyncClient, ASGITransport

from main import app
from database.mongodb import get_database
from api.v1.endpoints.authApi import pwd_context,SECRET_KEY, ALGORITHM
from jose import jwt
# import jwt


@pytest.mark.asyncio
async def test_auth_client(auth_client):
    res = await auth_client.post("/auth/my-own-profile", json={})
    assert res.status_code == 200
    # data = res.json()
    # assert "email" in data


@pytest.mark.asyncio
async def test_get_user_by_id(auth_client):
    res = await auth_client.get(f"/user/get-user-by-id")
    assert res.status_code == 200
    # data = res.json()
    # assert "email" in data