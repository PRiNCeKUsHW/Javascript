"""Chapter 7 examples, runnable: TaskHub v2 with routers, services and repositories."""
from contextlib import asynccontextmanager
from functools import lru_cache
from typing import Annotated, AsyncIterator

import httpx
import pytest
from fastapi import APIRouter, Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import String, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.pool import StaticPool


# core/config.py
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    app_name: str = "TaskHub"
    database_url: str = "sqlite+aiosqlite:///./taskhub.db"
    debug: bool = False
    secret_key: str


@lru_cache
def get_settings() -> Settings:
    return Settings()


def test_settings_read_env_and_fail_fast(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "s3cret")
    monkeypatch.setenv("DEBUG", "true")
    s = Settings()
    assert s.secret_key == "s3cret" and s.debug is True
    monkeypatch.delenv("SECRET_KEY")
    with pytest.raises(ValidationError):
        Settings(_env_file=None)


# models / db
class Base(DeclarativeBase):
    pass


class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    done: Mapped[bool] = mapped_column(default=False)


engine = create_async_engine("sqlite+aiosqlite://", poolclass=StaticPool)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]


# schemas
class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    done: bool


# repositories/tasks.py
class TaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list(self, done: bool | None = None) -> list[Task]:
        stmt = select(Task).order_by(Task.id.desc())
        if done is not None:
            stmt = stmt.where(Task.done == done)
        return list(await self.session.scalars(stmt))

    async def exists_title(self, title: str) -> bool:
        stmt = select(Task.id).where(Task.title == title)
        return (await self.session.scalar(stmt)) is not None

    async def add(self, task: Task) -> Task:
        self.session.add(task)
        await self.session.flush()
        return task


# services/tasks.py
class TaskAlreadyExists(Exception):
    def __init__(self, title: str):
        self.title = title


class TaskService:
    def __init__(self, repo: TaskRepository, session: AsyncSession):
        self.repo = repo
        self.session = session

    async def list_tasks(self, done: bool | None = None) -> list[Task]:
        return await self.repo.list(done)

    async def create(self, data: TaskCreate) -> Task:
        if await self.repo.exists_title(data.title):
            raise TaskAlreadyExists(data.title)
        task = await self.repo.add(Task(**data.model_dump()))
        await self.session.commit()
        return task


def get_task_service(session: SessionDep) -> TaskService:
    return TaskService(TaskRepository(session), session)


TaskServiceDep = Annotated[TaskService, Depends(get_task_service)]


# api/v1/tasks.py
router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/", response_model=list[TaskRead])
async def list_tasks(service: TaskServiceDep, done: bool | None = None):
    return await service.list_tasks(done)


@router.post("/", response_model=TaskRead, status_code=201)
async def create_task(data: TaskCreate, service: TaskServiceDep):
    return await service.create(data)


# main.py
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    app.state.http = httpx.AsyncClient(timeout=10)
    yield
    await app.state.http.aclose()


app = FastAPI(title="TaskHub", lifespan=lifespan)
app.include_router(router, prefix="/api/v1")


@app.exception_handler(TaskAlreadyExists)
async def task_exists(request: Request, exc: TaskAlreadyExists):
    return JSONResponse(status_code=409, content={"error": {"code": "task_exists", "title": exc.title}})


def test_layered_taskhub():
    with TestClient(app) as c:
        assert c.post("/api/v1/tasks/", json={"title": "Plan sprint"}).status_code == 201
        r = c.post("/api/v1/tasks/", json={"title": "Plan sprint"})
        assert r.status_code == 409 and r.json()["error"]["code"] == "task_exists"
        assert [t["title"] for t in c.get("/api/v1/tasks/").json()] == ["Plan sprint"]
        assert "tasks" in c.get("/openapi.json").json()["paths"]["/api/v1/tasks/"]["get"]["tags"]
        assert isinstance(app.state.http, httpx.AsyncClient)


def test_settings_override_in_tests(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "x")
    probe = FastAPI()

    @probe.get("/name")
    def name(settings: Annotated[Settings, Depends(get_settings)]):
        return {"name": settings.app_name}

    probe.dependency_overrides[get_settings] = lambda: Settings(app_name="TaskHub-test", secret_key="t")
    assert TestClient(probe).get("/name").json() == {"name": "TaskHub-test"}
