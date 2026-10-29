"""Chapter 8 examples, runnable: password hashing, OAuth2 + JWT, roles and ownership."""
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.testclient import TestClient
from pwdlib import PasswordHash
from pydantic import BaseModel

SECRET_KEY = "test-secret-key-that-is-long-enough-32b"
ALGORITHM = "HS256"
password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return password_hash.verify(password, hashed)


def create_access_token(subject: str, minutes: int = 30) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


class User(BaseModel):
    id: int
    email: str
    hashed_password: str
    role: str = "member"
    is_active: bool = True


USERS = {
    1: User(id=1, email="riya@example.com", hashed_password=hash_password("secret123")),
    2: User(id=2, email="asha@example.com", hashed_password=hash_password("admin123"), role="admin"),
}
TASKS = {1: {"id": 1, "title": "Riya's task", "owner_id": 1}, 2: {"id": 2, "title": "Asha's task", "owner_id": 2}}


def get_by_email(email: str) -> User | None:
    return next((u for u in USERS.values() if u.email == email), None)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token")
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = get_by_email(form.username)
    if user is None or not verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(subject=str(user.id))
    return {"access_token": token, "token_type": "bearer"}


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.InvalidTokenError:
        raise credentials_error
    user = USERS.get(int(payload["sub"]))
    if user is None or not user.is_active:
        raise credentials_error
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_role(role: str):
    def checker(user: CurrentUser) -> User:
        if user.role != role:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return user
    return checker


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://taskhub.example.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router, prefix="/api/v1")


@app.get("/api/v1/me")
def me(user: CurrentUser):
    return {"id": user.id, "email": user.email, "role": user.role}


@app.get("/api/v1/tasks/{task_id}")
def get_task(task_id: int, user: CurrentUser):
    task = TASKS.get(task_id)
    if task is None or task["owner_id"] != user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.delete("/api/v1/users/{user_id}", status_code=204, dependencies=[Depends(require_role("admin"))])
def delete_user(user_id: int) -> None:
    return None


c = TestClient(app)


def login_as(email, password):
    return c.post("/api/v1/auth/token", data={"username": email, "password": password})


def test_hashing():
    h = hash_password("secret123")
    assert h.startswith("$argon2") and h != "secret123"
    assert verify_password("secret123", h) and not verify_password("nope", h)


def test_login_and_me():
    r = login_as("riya@example.com", "secret123")
    assert r.status_code == 200 and r.json()["token_type"] == "bearer"
    token = r.json()["access_token"]
    assert token.count(".") == 2  # header.payload.signature
    assert jwt.decode(token, options={"verify_signature": False})["sub"] == "1"
    me_r = c.get("/api/v1/me", headers={"Authorization": f"Bearer {token}"})
    assert me_r.json() == {"id": 1, "email": "riya@example.com", "role": "member"}


def test_wrong_password_and_bad_tokens():
    r = login_as("riya@example.com", "wrong")
    assert r.status_code == 401 and r.headers["www-authenticate"] == "Bearer"
    assert c.get("/api/v1/me").status_code == 401
    assert c.get("/api/v1/me", headers={"Authorization": "Bearer garbage"}).status_code == 401
    expired = create_access_token("1", minutes=-1)
    assert c.get("/api/v1/me", headers={"Authorization": f"Bearer {expired}"}).status_code == 401


def test_roles_and_ownership():
    riya = login_as("riya@example.com", "secret123").json()["access_token"]
    asha = login_as("asha@example.com", "admin123").json()["access_token"]
    h = {"Authorization": f"Bearer {riya}"}
    assert c.get("/api/v1/tasks/1", headers=h).status_code == 200
    assert c.get("/api/v1/tasks/2", headers=h).status_code == 404  # not yours: hide it
    assert c.delete("/api/v1/users/1", headers=h).status_code == 403
    assert c.delete("/api/v1/users/1", headers={"Authorization": f"Bearer {asha}"}).status_code == 204


def test_cors_preflight():
    r = c.options("/api/v1/me", headers={"Origin": "https://taskhub.example.com", "Access-Control-Request-Method": "GET"})
    assert r.headers["access-control-allow-origin"] == "https://taskhub.example.com"
    r = c.options("/api/v1/me", headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "GET"})
    assert "access-control-allow-origin" not in r.headers
