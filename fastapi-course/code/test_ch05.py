"""Chapter 5 examples, runnable."""
from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel

app = FastAPI()
BOOKS = [f"book-{i}" for i in range(30)]


def pagination(skip: int = 0, limit: int = 10) -> dict:
    return {"skip": skip, "limit": min(limit, 100)}


@app.get("/authors")
def list_authors(page: Annotated[dict, Depends(pagination)]):
    return {"page": page}


class Paginator:
    def __init__(self, skip: int = 0, limit: int = 10):
        self.skip = skip
        self.limit = min(limit, 100)

    def apply(self, items: list) -> list:
        return items[self.skip : self.skip + self.limit]


PageDep = Annotated[Paginator, Depends()]


@app.get("/books")
def list_books(page: PageDep):
    return page.apply(BOOKS)


API_KEYS = {"key-123": "riya"}


def get_api_key(x_api_key: Annotated[str, Header()]) -> str:
    if x_api_key not in API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key


def get_current_user(key: Annotated[str, Depends(get_api_key)]) -> str:
    return API_KEYS[key]


@app.get("/me")
def read_me(user: Annotated[str, Depends(get_current_user)]):
    return {"user": user}


EVENTS: list[str] = []


class Connection:
    def __init__(self):
        EVENTS.append("open")

    def close(self):
        EVENTS.append("close")


def get_db():
    db = Connection()
    try:
        yield db
    finally:
        db.close()


@app.get("/stats")
def stats(db: Annotated[Connection, Depends(get_db)]):
    return {"ok": True}


CALLS: list[int] = []


def counted() -> int:
    CALLS.append(1)
    return len(CALLS)


def uses_counted(n: Annotated[int, Depends(counted)]) -> int:
    return n


@app.get("/cache")
def cache(a: Annotated[int, Depends(counted)], b: Annotated[int, Depends(uses_counted)]):
    return {"a": a, "b": b}


c = TestClient(app)


def test_function_and_class_deps():
    assert c.get("/authors?limit=500").json() == {"page": {"skip": 0, "limit": 100}}
    assert c.get("/books?skip=5&limit=2").json() == ["book-5", "book-6"]


def test_sub_dependencies():
    assert c.get("/me", headers={"X-API-Key": "key-123"}).json() == {"user": "riya"}
    assert c.get("/me", headers={"X-API-Key": "nope"}).status_code == 401
    assert c.get("/me").status_code == 422  # header missing


def test_yield_cleanup():
    EVENTS.clear()
    c.get("/stats")
    assert EVENTS == ["open", "close"]


def test_cached_per_request():
    CALLS.clear()
    assert c.get("/cache").json() == {"a": 1, "b": 1}


def test_override():
    def fake_user() -> str:
        return "test-user"

    app.dependency_overrides[get_current_user] = fake_user
    assert c.get("/me").json() == {"user": "test-user"}
    app.dependency_overrides.clear()


# --- Level project: Library API
lib = FastAPI(title="Library API")
MEMBERS = {
    "key-riya": {"name": "Riya", "role": "member"},
    "key-asha": {"name": "Asha", "role": "admin"},
}
SHELF: list[str] = []


def current_member(x_api_key: Annotated[str, Header()]) -> dict:
    member = MEMBERS.get(x_api_key)
    if member is None:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return member


def require_admin(member: Annotated[dict, Depends(current_member)]) -> dict:
    if member["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    return member


class BookIn(BaseModel):
    title: str


admin = APIRouter(prefix="/admin", dependencies=[Depends(require_admin)])
MemberDep = Annotated[dict, Depends(current_member)]


@lib.get("/me")
def me(member: MemberDep):
    return member


@admin.post("/books", status_code=201)
def add_book(book: BookIn):
    SHELF.append(book.title)
    return {"added": book.title}


lib.include_router(admin)


def test_library_project():
    lc = TestClient(lib)
    assert lc.get("/me", headers={"X-API-Key": "key-riya"}).json()["role"] == "member"
    assert lc.post("/admin/books", json={"title": "Dune"}, headers={"X-API-Key": "key-riya"}).status_code == 403
    assert lc.post("/admin/books", json={"title": "Dune"}, headers={"X-API-Key": "key-asha"}).status_code == 201
    assert lc.post("/admin/books", json={"title": "Dune"}).status_code == 422


# --- the leaking connection mistake
LEAK: list[str] = []


class Conn:
    def __init__(self):
        LEAK.append("open")

    def close(self):
        LEAK.append("close")


def get_db_wrong():
    db = Conn()
    yield db
    db.close()


def get_db_right():
    db = Conn()
    try:
        yield db
    finally:
        db.close()


leaky = FastAPI()


@leaky.get("/wrong")
def wrong(db: Annotated[Conn, Depends(get_db_wrong)]):
    raise RuntimeError("boom")


@leaky.get("/right")
def right(db: Annotated[Conn, Depends(get_db_right)]):
    raise RuntimeError("boom")


def test_yield_without_finally_leaks():
    lc = TestClient(leaky, raise_server_exceptions=False)
    LEAK.clear()
    lc.get("/wrong")
    assert LEAK == ["open"]  # never closed
    LEAK.clear()
    lc.get("/right")
    assert LEAK == ["open", "close"]
