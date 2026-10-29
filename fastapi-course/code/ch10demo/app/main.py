"""A compact TaskHub used by the Level 10 test suite."""
from contextlib import asynccontextmanager
from datetime import date, datetime, timedelta, timezone
from typing import Annotated, AsyncIterator

import httpx
import jwt
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pwdlib import PasswordHash
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from sqlalchemy import ForeignKey, String, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

SECRET_KEY = "change-me-in-production-0123456789abcdef"
ALGORITHM = "HS256"
password_hash = PasswordHash.recommended()


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str]


class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    done: Mapped[bool] = mapped_column(default=False)
    due: Mapped[date | None]
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))


engine = create_async_engine("sqlite+aiosqlite:///taskhub.db")
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session


async def get_http(request: Request) -> httpx.AsyncClient:
    return request.app.state.http


SessionDep = Annotated[AsyncSession, Depends(get_session)]
HttpDep = Annotated[httpx.AsyncClient, Depends(get_http)]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


async def get_current_user(session: SessionDep, token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    try:
        user_id = int(jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token",
                            headers={"WWW-Authenticate": "Bearer"})
    user = await session.get(User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with httpx.AsyncClient(timeout=5) as client:
        app.state.http = client
        yield


app = FastAPI(lifespan=lifespan)


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    due: date | None = None


class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    done: bool
    due: date | None


@app.post("/auth/register", status_code=201, response_model=UserOut)
async def register(data: UserCreate, session: SessionDep):
    if await session.scalar(select(User).where(User.email == data.email)):
        raise HTTPException(409, "Email already registered")
    user = User(email=data.email, password_hash=password_hash.hash(data.password))
    session.add(user)
    await session.commit()
    return user


@app.post("/auth/token")
async def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep):
    user = await session.scalar(select(User).where(User.email == form.username))
    if not user or not password_hash.verify(form.password, user.password_hash):
        raise HTTPException(401, "Wrong email or password")
    expires = datetime.now(timezone.utc) + timedelta(minutes=30)
    token = jwt.encode({"sub": str(user.id), "exp": expires}, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}


@app.post("/tasks", status_code=201, response_model=TaskOut)
async def create_task(data: TaskCreate, user: CurrentUser, session: SessionDep):
    task = Task(**data.model_dump(), owner_id=user.id)
    session.add(task)
    await session.commit()
    return task


@app.get("/tasks", response_model=list[TaskOut])
async def list_tasks(user: CurrentUser, session: SessionDep):
    return await session.scalars(select(Task).where(Task.owner_id == user.id))


async def get_owned_task(task_id: int, user: CurrentUser, session: SessionDep) -> Task:
    task = await session.get(Task, task_id)
    if task is None or task.owner_id != user.id:
        raise HTTPException(404, "Task not found")
    return task


OwnedTaskDep = Annotated[Task, Depends(get_owned_task)]


@app.get("/tasks/{task_id}", response_model=TaskOut)
async def read_task(task: OwnedTaskDep):
    return task


@app.get("/tasks/{task_id}/holiday-check")
async def holiday_check(task: OwnedTaskDep, http: HttpDep):
    if task.due is None:
        raise HTTPException(400, "Task has no due date")
    url = f"https://date.nager.at/api/v3/PublicHolidays/{task.due.year}/IN"
    try:
        r = await http.get(url)
        r.raise_for_status()
    except httpx.HTTPError:
        raise HTTPException(503, "Holiday service unavailable")
    holidays = {h["date"] for h in r.json()}
    return {"due": task.due, "is_holiday": task.due.isoformat() in holidays}
