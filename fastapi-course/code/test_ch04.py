"""Chapter 4 examples, runnable."""
import logging

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from pydantic import BaseModel, EmailStr, Field

logger = logging.getLogger("app")
app = FastAPI()


class UserIn(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    email: EmailStr


@app.post("/users", response_model=UserOut, status_code=201)
def create_user(user: UserIn):
    return user


@app.get("/me")
def read_me() -> UserOut:
    user = {"email": "riya@example.com", "password": "secret"}
    return user


NOTES = {1: {"id": 1, "text": "Buy milk"}}


@app.get("/notes/{note_id}")
def get_note(note_id: int):
    note = NOTES.get(note_id)
    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note {note_id} not found",
        )
    return note


@app.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: int) -> None:
    if NOTES.pop(note_id, None) is None:
        raise HTTPException(status_code=404, detail="Note not found")


class DuplicateError(Exception):
    def __init__(self, field: str):
        self.field = field


@app.exception_handler(DuplicateError)
async def duplicate_handler(request: Request, exc: DuplicateError):
    return JSONResponse(
        status_code=409,
        content={"error": {"code": "duplicate", "field": exc.field}},
    )


@app.post("/dup")
def dup():
    raise DuplicateError("email")


@app.exception_handler(Exception)
async def unhandled(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s", request.url.path)
    return JSONResponse(status_code=500, content={"error": {"code": "internal"}})


@app.get("/boom")
def boom():
    raise RuntimeError("secret internals")


c = TestClient(app, raise_server_exceptions=False)


def test_response_model_filters():
    r = c.post("/users", json={"email": "riya@example.com", "password": "x"})
    assert r.status_code == 201 and r.json() == {"email": "riya@example.com"}
    assert c.get("/me").json() == {"email": "riya@example.com"}


def test_404_and_204():
    assert c.get("/notes/9").json() == {"detail": "Note 9 not found"}
    r = c.delete("/notes/1")
    assert r.status_code == 204 and r.content == b""
    assert c.delete("/notes/1").status_code == 404


def test_custom_and_catch_all():
    assert c.post("/dup").json() == {"error": {"code": "duplicate", "field": "email"}}
    r = c.get("/boom")
    assert r.status_code == 500 and "secret" not in r.text


# --- Level project: Notes API with clean errors
notes = FastAPI(title="Notes API")


def error(status: int, code: str, message: str) -> JSONResponse:
    body = {"error": {"code": code, "message": message}}
    return JSONResponse(status_code=status, content=body)


class NoteExists(Exception):
    pass


@notes.exception_handler(NoteExists)
async def note_exists(request: Request, exc: NoteExists):
    return error(409, "note_exists", "A note with this title already exists")


@notes.exception_handler(HTTPException)
async def http_error(request: Request, exc: HTTPException):
    return error(exc.status_code, "http_error", str(exc.detail))


class NoteIn(BaseModel):
    title: str = Field(min_length=1, max_length=80)
    text: str = ""

class NoteOut(NoteIn):
    id: int

STORE: dict[int, NoteOut] = {}

@notes.post("/notes", response_model=NoteOut, status_code=201)
def create_note(note: NoteIn):
    if any(n.title == note.title for n in STORE.values()):
        raise NoteExists()
    note_id = len(STORE) + 1
    STORE[note_id] = NoteOut(id=note_id, **note.model_dump())
    return STORE[note_id]


@notes.get("/notes/{note_id}", response_model=NoteOut)
def read_note(note_id: int):
    if note_id not in STORE:
        raise HTTPException(status_code=404, detail="Note not found")
    return STORE[note_id]


def test_notes_project():
    nc = TestClient(notes)
    assert nc.post("/notes", json={"title": "Todo"}).status_code == 201
    r = nc.post("/notes", json={"title": "Todo"})
    assert r.status_code == 409 and r.json()["error"]["code"] == "note_exists"
    assert nc.get("/notes/99").json() == {"error": {"code": "http_error", "message": "Note not found"}}


# --- the password-hash leak and its fix
leak = FastAPI()
ROW = {"email": "riya@example.com", "password_hash": "$argon2id$...", "is_admin": False}


@leak.get("/wrong/{user_id}")
def get_user_wrong(user_id: int):
    return ROW


@leak.get("/right/{user_id}")
def get_user_right(user_id: int) -> UserOut:
    return ROW


def test_password_hash_leak_and_fix():
    lc = TestClient(leak)
    assert "password_hash" in lc.get("/wrong/1").json()
    assert lc.get("/right/1").json() == {"email": "riya@example.com"}
