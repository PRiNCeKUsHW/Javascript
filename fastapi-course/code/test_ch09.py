"""Chapter 9 examples, runnable: blocking vs async, BackgroundTasks, middleware, httpx."""
import asyncio
import time
import uuid
from typing import Annotated

import httpx
import pytest
from fastapi import BackgroundTasks, Depends, FastAPI, Request
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.testclient import TestClient
from starlette.concurrency import run_in_threadpool

app = FastAPI()
DELAY = 0.3


@app.get("/blocking")
async def blocking():
    time.sleep(DELAY)          # blocks the whole event loop!
    return {"ok": True}


@app.get("/non-blocking")
async def non_blocking():
    await asyncio.sleep(DELAY)  # other requests keep running
    return {"ok": True}


@app.get("/sync-ok")
def sync_ok():
    time.sleep(DELAY)          # plain def runs in a threadpool
    return {"ok": True}


def slow_library_call() -> str:
    time.sleep(DELAY)
    return "done"


@app.get("/threadpool")
async def threadpool():
    return {"result": await run_in_threadpool(slow_library_call)}


async def timed(path: str, n: int = 5) -> float:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://t") as client:
        start = time.perf_counter()
        await asyncio.gather(*(client.get(path) for _ in range(n)))
        return time.perf_counter() - start


@pytest.mark.asyncio
async def test_blocking_serialises_requests():
    assert await timed("/blocking") >= 5 * DELAY * 0.9
    assert await timed("/non-blocking") < 2 * DELAY
    assert await timed("/sync-ok") < 2 * DELAY
    assert await timed("/threadpool") < 2 * DELAY


# --- BackgroundTasks
EVENTS: list[str] = []


def send_welcome_email(email: str) -> None:
    EVENTS.append(f"email:{email}")


@app.post("/auth/register", status_code=201)
async def register(email: str, background: BackgroundTasks):
    EVENTS.append("saved")
    background.add_task(send_welcome_email, email)
    EVENTS.append("responding")
    return {"email": email}


def test_background_task_runs_after_response():
    EVENTS.clear()
    r = TestClient(app).post("/auth/register?email=riya@example.com")
    assert r.status_code == 201
    assert EVENTS == ["saved", "responding", "email:riya@example.com"]


# --- middleware
mw = FastAPI()
mw.add_middleware(GZipMiddleware, minimum_size=1000)


@mw.middleware("http")
async def add_request_id_and_timing(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start) * 1000
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time-Ms"] = f"{elapsed_ms:.1f}"
    return response


@mw.get("/big")
def big():
    return {"data": "x" * 5000}


def test_middleware_headers_and_gzip():
    mc = TestClient(mw)
    r = mc.get("/big", headers={"X-Request-ID": "abc-123", "Accept-Encoding": "gzip"})
    assert r.headers["x-request-id"] == "abc-123"
    assert float(r.headers["x-process-time-ms"]) >= 0
    assert r.headers["content-encoding"] == "gzip"
    assert len(mc.get("/big").headers["x-request-id"]) == 36


# --- calling another service with a shared httpx client
def fake_weather(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json={"city": request.url.path.split("/")[-1], "temp_c": 31})


ext = FastAPI()
ext.state.http = httpx.AsyncClient(transport=httpx.MockTransport(fake_weather), timeout=10)


def get_http(request: Request) -> httpx.AsyncClient:
    return request.app.state.http


HttpDep = Annotated[httpx.AsyncClient, Depends(get_http)]


@ext.get("/weather/{city}")
async def weather(city: str, http: HttpDep):
    r = await http.get(f"https://api.example.com/weather/{city}")
    r.raise_for_status()
    return r.json()


def test_shared_http_client():
    assert TestClient(ext).get("/weather/pune").json() == {"city": "pune", "temp_c": 31}
