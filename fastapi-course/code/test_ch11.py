"""Chapter 11 examples, runnable: uploads, SSE, WebSockets, cursor pagination, Redis cache, rate limits."""
import asyncio
import json
from pathlib import Path
from typing import Annotated

import pytest
from fakeredis import FakeAsyncRedis
from fastapi import Depends, FastAPI, HTTPException, Query, Request, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.sse import EventSourceResponse, ServerSentEvent
from fastapi.testclient import TestClient
from pydantic import BaseModel
from redis.asyncio import Redis

app = FastAPI()
UPLOAD_DIR = Path("/tmp/ch11_uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# --- uploads -------------------------------------------------------------
MAX_BYTES = 5 * 1024 * 1024
ALLOWED = {"image/png", "image/jpeg", "application/pdf"}


@app.post("/tasks/{task_id}/attachments", status_code=201)
async def upload(task_id: int, file: UploadFile):
    if file.content_type not in ALLOWED:
        raise HTTPException(415, "Only PNG, JPEG or PDF")
    path = UPLOAD_DIR / f"{task_id}-{Path(file.filename).name}"
    size = 0
    with path.open("wb") as out:
        while chunk := await file.read(1024 * 1024):
            size += len(chunk)
            if size > MAX_BYTES:
                path.unlink(missing_ok=True)
                raise HTTPException(413, "File larger than 5 MB")
            out.write(chunk)
    return {"filename": path.name, "size": size}


# --- server-sent events ----------------------------------------------------
@app.get("/reports/{report_id}/progress", response_class=EventSourceResponse)
async def report_progress(report_id: int):
    for percent in (0, 25, 50, 75, 100):
        yield ServerSentEvent(event="progress", data={"report": report_id, "percent": percent})
        await asyncio.sleep(0.01)
    yield ServerSentEvent(event="done", data={"url": f"/reports/{report_id}.pdf"})


# --- websockets ------------------------------------------------------------
class Board:
    def __init__(self):
        self.sockets: list[WebSocket] = []

    async def join(self, ws: WebSocket):
        await ws.accept()
        self.sockets.append(ws)

    def leave(self, ws: WebSocket):
        self.sockets.remove(ws)

    async def broadcast(self, message: dict):
        for ws in self.sockets:
            await ws.send_json(message)


board = Board()


@app.websocket("/ws/board")
async def board_socket(ws: WebSocket, name: str):
    await board.join(ws)
    try:
        while True:
            text = await ws.receive_text()
            await board.broadcast({"from": name, "text": text})
    except WebSocketDisconnect:
        board.leave(ws)


# --- cursor pagination -------------------------------------------------------
TASKS = [{"id": i, "title": f"Task {i}"} for i in range(1, 26)]


class Page(BaseModel):
    items: list[dict]
    next_cursor: int | None


@app.get("/tasks", response_model=Page)
async def list_tasks(limit: Annotated[int, Query(ge=1, le=100)] = 10, cursor: int = 0):
    rows = [t for t in TASKS if t["id"] > cursor][: limit + 1]
    has_more = len(rows) > limit
    items = rows[:limit]
    return {"items": items, "next_cursor": items[-1]["id"] if has_more else None}


# --- redis cache + rate limit ------------------------------------------------
redis_client: Redis = FakeAsyncRedis(decode_responses=True)
CALLS = {"db": 0}


async def get_redis() -> Redis:
    return redis_client


RedisDep = Annotated[Redis, Depends(get_redis)]


async def load_stats_from_db(user_id: int) -> dict:
    CALLS["db"] += 1
    await asyncio.sleep(0.05)
    return {"user_id": user_id, "open": 7, "done": 42}


@app.get("/users/{user_id}/stats")
async def stats(user_id: int, redis: RedisDep):
    key = f"stats:{user_id}"
    if cached := await redis.get(key):
        return json.loads(cached)
    data = await load_stats_from_db(user_id)
    await redis.set(key, json.dumps(data), ex=60)
    return data


@app.post("/users/{user_id}/tasks/done")
async def mark_done(user_id: int, redis: RedisDep):
    await redis.delete(f"stats:{user_id}")
    return {"ok": True}


def rate_limit(limit: int, window: int):
    async def check(request: Request, redis: RedisDep):
        key = f"rl:{request.client.host}:{request.url.path}"
        count = await redis.incr(key)
        if count == 1:
            await redis.expire(key, window)
        if count > limit:
            ttl = await redis.ttl(key)
            raise HTTPException(429, "Too many requests", headers={"Retry-After": str(ttl)})
    return Depends(check)


@app.post("/auth/token", dependencies=[rate_limit(limit=5, window=60)])
async def login():
    return {"access_token": "..."}


client = TestClient(app)


def test_upload_ok_and_limits():
    r = client.post("/tasks/7/attachments", files={"file": ("receipt.pdf", b"%PDF-1.7 hello", "application/pdf")})
    assert r.status_code == 201 and r.json() == {"filename": "7-receipt.pdf", "size": 14}
    r = client.post("/tasks/7/attachments", files={"file": ("x.exe", b"MZ", "application/octet-stream")})
    assert r.status_code == 415
    big = b"0" * (MAX_BYTES + 1)
    r = client.post("/tasks/7/attachments", files={"file": ("big.png", big, "image/png")})
    assert r.status_code == 413
    assert not (UPLOAD_DIR / "7-big.png").exists()


def test_filename_path_traversal_is_stripped():
    r = client.post("/tasks/1/attachments", files={"file": ("../../etc/passwd.png", b"x", "image/png")})
    assert r.json()["filename"] == "1-passwd.png"


def test_sse_stream():
    with client.stream("GET", "/reports/9/progress") as r:
        assert r.headers["content-type"].startswith("text/event-stream")
        body = "".join(r.iter_text())
    print(body)
    assert 'event: progress\ndata: {"report": 9, "percent": 0}' in body
    assert 'event: done\ndata: {"url": "/reports/9.pdf"}' in body


def test_websocket_broadcast():
    with client.websocket_connect("/ws/board?name=riya") as riya, \
            client.websocket_connect("/ws/board?name=aman") as aman:
        riya.send_text("Standup in 5 minutes")
        assert aman.receive_json() == {"from": "riya", "text": "Standup in 5 minutes"}
        assert riya.receive_json() == {"from": "riya", "text": "Standup in 5 minutes"}


def test_cursor_pagination():
    first = client.get("/tasks?limit=10").json()
    assert [t["id"] for t in first["items"]][:2] == [1, 2] and first["next_cursor"] == 10
    second = client.get(f"/tasks?limit=10&cursor={first['next_cursor']}").json()
    assert second["items"][0]["id"] == 11 and second["next_cursor"] == 20
    last = client.get("/tasks?limit=10&cursor=20").json()
    assert len(last["items"]) == 5 and last["next_cursor"] is None


def test_cache_hits_and_invalidation():
    CALLS["db"] = 0
    assert client.get("/users/1/stats").json()["done"] == 42
    client.get("/users/1/stats")
    client.get("/users/1/stats")
    assert CALLS["db"] == 1
    client.post("/users/1/tasks/done")
    client.get("/users/1/stats")
    assert CALLS["db"] == 2


def test_rate_limit():
    codes = [client.post("/auth/token").status_code for _ in range(7)]
    assert codes == [200] * 5 + [429, 429]
    r = client.post("/auth/token")
    assert r.headers["Retry-After"] == "60"
