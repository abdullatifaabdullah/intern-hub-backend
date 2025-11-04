import os
import pytest
from httpx import AsyncClient
from app.main import create_app


@pytest.mark.asyncio
async def test_healthz_flags():
    app = create_app()
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.get("/healthz")
        assert r.status_code == 200
        data = r.json()
        assert set(["status", "preflight", "db_init_check", "bootstrap", "lazy_loading", "stateless_strict"]).issubset(set(data.keys()))


@pytest.mark.asyncio
async def test_preflight_skip(monkeypatch):
    monkeypatch.setenv("ENABLE_PREFLIGHT", "false")
    app = create_app()
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.get("/healthz")
        assert r.json()["preflight"] in (False, 0)

 