"""Chapter 1 examples, runnable."""
from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}


@app.get("/health")
def health():
    return {"status": "ok"}


client = TestClient(app)


def test_root():
    assert client.get("/").json() == {"message": "Hello, FastAPI!"}


def test_path_param_is_converted():
    assert client.get("/items/42").json() == {"item_id": 42, "q": None}


def test_query_param():
    assert client.get("/items/5", params={"q": "test"}).json() == {"item_id": 5, "q": "test"}


def test_wrong_type_is_422():
    r = client.get("/items/abc")
    assert r.status_code == 422
    err = r.json()["detail"][0]
    assert err["type"] == "int_parsing" and err["loc"] == ["path", "item_id"]


def test_health_and_docs():
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/docs").status_code == 200
    assert "/items/{item_id}" in client.get("/openapi.json").json()["paths"]


def test_docs_can_be_disabled():
    hidden = TestClient(FastAPI(docs_url=None, redoc_url=None))
    assert hidden.get("/docs").status_code == 404


# --- Level project: Personal Profile API
profile = FastAPI(title="Personal Profile API")
SKILLS = ["Python", "FastAPI", "SQL", "Git"]


@profile.get("/")
def home():
    return {"name": "Your Name", "message": "Welcome to my API!"}


@profile.get("/skills")
def list_skills():
    return {"count": len(SKILLS), "skills": SKILLS}


@profile.get("/skills/{skill_id}")
def get_skill(skill_id: int):
    return {"id": skill_id, "skill": SKILLS[skill_id]}


def test_profile_project():
    c = TestClient(profile, raise_server_exceptions=False)
    assert c.get("/skills").json()["count"] == 4
    assert c.get("/skills/1").json() == {"id": 1, "skill": "FastAPI"}
    assert c.get("/skills/10").status_code == 500  # the stretch goal fixes this with a 404
    assert c.get("/openapi.json").json()["info"]["title"] == "Personal Profile API"
