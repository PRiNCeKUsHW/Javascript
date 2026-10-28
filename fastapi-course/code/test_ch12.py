"""Chapter 12 examples, runnable: JSON logs, request IDs, health/readiness, error handler, metrics."""
import json
import logging
import uuid
from contextvars import ContextVar

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from prometheus_fastapi_instrumentator import Instrumentator

request_id_var: ContextVar[str] = ContextVar("request_id", default="-")


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        entry = {
            "time": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": request_id_var.get(),
        }
        if record.exc_info:
            entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(entry)


LINES: list[str] = []


class ListHandler(logging.Handler):
    def emit(self, record):
        LINES.append(self.format(record))


handler = ListHandler()
handler.setFormatter(JsonFormatter())
logging.basicConfig(level=logging.INFO, handlers=[handler], force=True)
log = logging.getLogger("taskhub")

app = FastAPI()
STATE = {"db_up": True}


@app.middleware("http")
async def request_context(request: Request, call_next):
    rid = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request_id_var.set(rid)
    response = await call_next(request)
    response.headers["X-Request-ID"] = rid
    return response


@app.exception_handler(Exception)
async def unhandled(request: Request, exc: Exception):
    log.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500,
                        content={"detail": "Internal server error", "request_id": request_id_var.get()})


async def check_db():
    if not STATE["db_up"]:
        raise ConnectionError("db down")


@app.get("/healthz")
async def liveness():
    return {"status": "ok"}


@app.get("/readyz")
async def readiness():
    try:
        await check_db()
    except Exception:
        log.warning("Readiness check failed: database")
        return JSONResponse(status_code=503, content={"status": "unavailable", "database": "down"})
    return {"status": "ready", "database": "up"}


@app.get("/tasks/{task_id}")
async def read_task(task_id: int):
    log.info("Reading task %s", task_id)
    if task_id == 13:
        raise RuntimeError("password=hunter2 in a bad place")
    return {"id": task_id}


Instrumentator().instrument(app).expose(app, include_in_schema=False)


def test_json_logs_carry_request_id():
    LINES.clear()
    with TestClient(app) as c:
        r = c.get("/tasks/7", headers={"X-Request-ID": "abc-123"})
    assert r.headers["X-Request-ID"] == "abc-123"
    line = next(l for l in LINES if '"logger": "taskhub"' in l)
    print(line)
    entry = json.loads(line)
    assert entry["message"] == "Reading task 7" and entry["request_id"] == "abc-123"
    assert entry["level"] == "INFO" and entry["logger"] == "taskhub"


def test_unhandled_error_is_generic_500_with_request_id():
    LINES.clear()
    with TestClient(app, raise_server_exceptions=False) as c:
        r = c.get("/tasks/13", headers={"X-Request-ID": "req-13"})
    assert r.status_code == 500
    assert r.json() == {"detail": "Internal server error", "request_id": "req-13"}
    assert "hunter2" not in r.text
    assert any("RuntimeError" in l and "req-13" in l for l in LINES)


def test_liveness_and_readiness():
    with TestClient(app) as c:
        assert c.get("/healthz").json() == {"status": "ok"}
        assert c.get("/readyz").status_code == 200
        STATE["db_up"] = False
        r = c.get("/readyz")
        assert r.status_code == 503 and r.json()["database"] == "down"
        assert c.get("/healthz").status_code == 200
        STATE["db_up"] = True


def test_metrics_endpoint():
    with TestClient(app) as c:
        c.get("/tasks/1")
        body = c.get("/metrics").text
    assert "http_requests_total" in body
    assert 'handler="/tasks/{task_id}"' in body
    print([l for l in body.splitlines() if l.startswith("http_requests_total")][:2])
