import os
import pytest
from httpx import AsyncClient
from fastapi import status

os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("ALLOW_OPEN_ADMIN_SIGNUP", "true")

from app.main import app  # noqa: E402


@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.get("/health/live")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_auth_register_and_login():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # register
        resp = await ac.post("/auth/register", json={"email": "t1@example.com", "password": "Temp1234!", "role": "tenant"})
        assert resp.status_code in (200, 400)  # might already exist
        # login
        data = {"username": "t1@example.com", "password": "Temp1234!"}
        resp = await ac.post("/auth/login", data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
        assert resp.status_code == status.HTTP_200_OK
        token = resp.json()["access_token"]
        assert token