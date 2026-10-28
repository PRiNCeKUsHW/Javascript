"""Chapter 10 examples, runnable: the TaskHub test suite plus the facts the chapter claims."""
import subprocess
import sys
from pathlib import Path

import httpx
import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

DEMO = Path(__file__).parent / "ch10demo"


def test_demo_suite_passes_with_coverage():
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "--cov=app", "-p", "no:cacheprovider"],
                       cwd=DEMO, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "11 passed" in r.stdout
    assert "89%" in r.stdout


# --- lifespan: TestClient as a context manager runs it, ASGITransport does not
events: list[str] = []


def make_app():
    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def lifespan(app):
        events.append("startup")
        yield
        events.append("shutdown")

    return FastAPI(lifespan=lifespan)


def test_testclient_with_block_runs_lifespan():
    events.clear()
    with TestClient(make_app()):
        pass
    assert events == ["startup", "shutdown"]


def test_testclient_without_with_skips_lifespan():
    events.clear()
    TestClient(make_app()).get("/docs")
    assert events == []


@pytest.mark.asyncio
async def test_asgitransport_skips_lifespan():
    events.clear()
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=make_app()), base_url="http://t") as c:
        await c.get("/docs")
    assert events == []


# --- the mistake: an override that is never cleared leaks into the next test
app = FastAPI()


def get_user():
    return "real"


@app.get("/whoami")
def whoami(user: str = Depends(get_user)):
    return {"user": user}


def test_override_leaks_when_not_cleared():
    app.dependency_overrides[get_user] = lambda: "fake-admin"
    assert TestClient(app).get("/whoami").json() == {"user": "fake-admin"}
    # a later test, written by someone else, now sees the fake user too:
    assert TestClient(app).get("/whoami").json() == {"user": "fake-admin"}
    app.dependency_overrides.clear()
    assert TestClient(app).get("/whoami").json() == {"user": "real"}
