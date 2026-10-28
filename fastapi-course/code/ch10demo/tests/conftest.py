import httpx
import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.main import Base, app, get_session


@pytest.fixture
async def session_factory():
    engine = create_async_engine("sqlite+aiosqlite://", poolclass=StaticPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield async_sessionmaker(engine, expire_on_commit=False)
    await engine.dispose()


@pytest.fixture
async def client(session_factory):
    async def override_session():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_session] = override_session
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
async def auth_headers(client):
    async def make(email="riya@example.com", password="secret123"):
        await client.post("/auth/register", json={"email": email, "password": password})
        r = await client.post("/auth/token", data={"username": email, "password": password})
        return {"Authorization": f"Bearer {r.json()['access_token']}"}
    return make
