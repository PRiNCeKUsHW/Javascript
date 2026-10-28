"""Chapter 6 examples, runnable: TaskHub v1 with async SQLAlchemy 2.0."""
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Annotated, AsyncIterator

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.testclient import TestClient
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import ForeignKey, String, event, func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, selectinload
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    pass


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80))
    tasks: Mapped[list["Task"]] = relationship(back_populates="project")


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    done: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id"))
    project: Mapped[Project | None] = relationship(back_populates="tasks")


engine = create_async_engine("sqlite+aiosqlite://", poolclass=StaticPool)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)
QUERIES: list[str] = []


@event.listens_for(engine.sync_engine, "before_cursor_execute")
def count(conn, cursor, statement, *args):
    QUERIES.append(statement)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)


class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    done: bool


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="TaskHub", lifespan=lifespan)


@app.post("/tasks", response_model=TaskRead, status_code=201)
async def create_task(data: TaskCreate, session: SessionDep):
    task = Task(**data.model_dump())
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


@app.get("/tasks", response_model=list[TaskRead])
async def list_tasks(
    session: SessionDep,
    done: bool | None = None,
    q: Annotated[str | None, Query(min_length=2)] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    stmt = select(Task).order_by(Task.id.desc()).limit(limit)
    if done is not None:
        stmt = stmt.where(Task.done == done)
    if q:
        stmt = stmt.where(Task.title.ilike(f"%{q}%"))
    return (await session.scalars(stmt)).all()


async def get_task_or_404(task_id: int, session: SessionDep) -> Task:
    task = await session.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

TaskDep = Annotated[Task, Depends(get_task_or_404)]

@app.get("/tasks/{task_id}", response_model=TaskRead)
async def read_task(task: TaskDep):
    return task

@app.patch("/tasks/{task_id}", response_model=TaskRead)
async def update_task(task: TaskDep, changes: TaskUpdate, session: SessionDep):
    for field, value in changes.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    await session.commit()
    return task

@app.delete("/tasks/{task_id}", status_code=204)
async def delete_task(task: TaskDep, session: SessionDep) -> None:
    await session.delete(task)
    await session.commit()


@app.get("/projects")
async def projects(session: SessionDep):
    stmt = select(Project).options(selectinload(Project.tasks))
    rows = (await session.scalars(stmt)).all()
    return [{"name": p.name, "tasks": [t.title for t in p.tasks]} for p in rows]


@app.post("/seed-projects")
async def seed(session: SessionDep):
    for i in range(5):
        p = Project(name=f"p{i}")
        p.tasks = [Task(title=f"p{i}-t{j}") for j in range(3)]
        session.add(p)
    await session.commit()
    return {"ok": True}


def test_taskhub_crud():
    with TestClient(app) as c:
        r = c.post("/tasks", json={"title": "Learn SQLAlchemy"})
        assert r.status_code == 201
        tid = r.json()["id"]
        c.post("/tasks", json={"title": "Write tests"})
        assert c.patch(f"/tasks/{tid}", json={"done": True}).json()["done"] is True
        assert [t["title"] for t in c.get("/tasks?done=true").json()] == ["Learn SQLAlchemy"]
        assert len(c.get("/tasks?q=tests").json()) == 1
        assert c.get("/tasks?q=t").status_code == 422
        assert c.delete(f"/tasks/{tid}").status_code == 204
        assert c.get(f"/tasks/{tid}").status_code == 404


def test_selectinload_avoids_n_plus_one():
    with TestClient(app) as c:
        c.post("/seed-projects")
        QUERIES.clear()
        data = c.get("/projects").json()
        assert len(data) == 5 and all(len(p["tasks"]) == 3 for p in data)
        selects = [q for q in QUERIES if q.lstrip().upper().startswith("SELECT")]
        assert len(selects) == 2  # one for projects, one for all their tasks


# --- the forgotten commit
@app.post("/no-commit", status_code=201)
async def create_without_commit(data: TaskCreate, session: SessionDep):
    task = Task(**data.model_dump())
    session.add(task)
    return {"ok": True}


def test_forgetting_commit_loses_the_row():
    with TestClient(app) as c:
        before = len(c.get("/tasks?limit=100").json())
        assert c.post("/no-commit", json={"title": "ghost"}).status_code == 201
        after = c.get("/tasks?limit=100").json()
        assert len(after) == before and all(t["title"] != "ghost" for t in after)
