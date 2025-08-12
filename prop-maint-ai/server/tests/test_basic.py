import os
import pytest
import httpx
from fastapi import status

os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("ALLOW_OPEN_ADMIN_SIGNUP", "true")

from app.main import app  # noqa: E402
from app.database import Base, engine  # noqa: E402

# Ensure tables exist for tests
Base.metadata.create_all(bind=engine)


@pytest.mark.asyncio
async def test_health():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/health/live")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_auth_register_and_login():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        # register
        resp = await ac.post("/auth/register", json={"email": "t1@example.com", "password": "Temp1234!", "role": "tenant"})
        assert resp.status_code in (200, 400)
        # login
        data = {"username": "t1@example.com", "password": "Temp1234!"}
        resp = await ac.post("/auth/login", data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
        assert resp.status_code == status.HTTP_200_OK
        token = resp.json()["access_token"]
        assert token