"""Chapter 3 examples, runnable."""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, EmailStr, Field, ValidationError, field_validator, model_validator

app = FastAPI()


class Student(BaseModel):
    name: str
    age: int
    email: str
    city: str | None = None


@app.post("/students-basic")
def create_student(student: Student):
    return {"message": f"Welcome {student.name}!", "data": student}


class StrictStudent(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    age: int = Field(ge=16, le=60)
    email: EmailStr
    skills: list[str] = Field(default_factory=list, max_length=10)


class Address(BaseModel):
    city: str
    pincode: str = Field(pattern=r"^\d{6}$")


class NestedStudent(BaseModel):
    name: str
    address: Address
    marks: list[int] = []


@app.post("/students")
def create_nested(student: NestedStudent):
    return student


class SignUp(BaseModel):
    username: str
    password: str
    confirm_password: str

    @field_validator("username")
    @classmethod
    def no_spaces(cls, v: str) -> str:
        if " " in v:
            raise ValueError("username must not contain spaces")
        return v.lower()

    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("passwords do not match")
        return self


class TaskBase(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    done: bool = False


class TaskRead(TaskBase):
    id: int


class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None


TASKS: dict[int, TaskRead] = {1: TaskRead(id=1, title="Learn FastAPI")}


@app.patch("/tasks/{task_id}")
def update_task(task_id: int, changes: TaskUpdate) -> TaskRead:
    stored = TASKS[task_id]
    updates = changes.model_dump(exclude_unset=True)
    TASKS[task_id] = stored.model_copy(update=updates)
    return TASKS[task_id]


class Item(BaseModel):
    name: str


@app.put("/items/{item_id}")
def put_item(item_id: int, q: str, item: Item):
    return {"item_id": item_id, "q": q, "item": item}


class Product(BaseModel):
    name: str = Field(min_length=3, max_length=40)
    price: float = Field(gt=0)


class Person(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def clean_name(cls, v: str) -> str:
        return v.strip().title()


c = TestClient(app)


def test_body():
    r = c.post("/students-basic", json={"name": "Riya", "age": 21, "email": "r@x.com"})
    assert r.json()["message"] == "Welcome Riya!"


def test_field_rules():
    StrictStudent(name="Riya", age=21, email="riya@example.com")
    with pytest.raises(ValidationError):
        StrictStudent(name="R", age=12, email="nope")


def test_nested_and_conversion():
    body = {"name": "Riya", "address": {"city": "Pune", "pincode": "411001"}, "marks": [91, "88"]}
    assert c.post("/students", json=body).json()["marks"] == [91, 88]
    body["address"]["pincode"] = "4110"
    assert c.post("/students", json=body).status_code == 422


def test_validators():
    assert SignUp(username="Riya", password="x", confirm_password="x").username == "riya"
    with pytest.raises(ValidationError):
        SignUp(username="ri ya", password="x", confirm_password="x")
    with pytest.raises(ValidationError):
        SignUp(username="riya", password="x", confirm_password="y")


def test_patch_keeps_unsent_fields():
    r = c.patch("/tasks/1", json={"done": True})
    assert r.json() == {"id": 1, "title": "Learn FastAPI", "done": True}


def test_param_sources():
    r = c.put("/items/3?q=hi", json={"name": "pen"})
    assert r.json() == {"item_id": 3, "q": "hi", "item": {"name": "pen"}}


def test_practice_models():
    with pytest.raises(ValidationError):
        Product(name="pen", price=0)
    assert Person(name=" riya sharma ").name == "Riya Sharma"


def test_lax_and_strict():
    class M(BaseModel):
        age: int

    class S(BaseModel):
        age: int = Field(strict=True)

    assert M(age="21").age == 21
    with pytest.raises(ValidationError):
        M(age="twenty")
    with pytest.raises(ValidationError):
        S(age="21")


# --- Level project: Student Registration
class StudentCreate(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    age: int = Field(ge=16, le=60)
    email: EmailStr
    address: Address
    password: str = Field(min_length=8)
    confirm_password: str

    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("passwords do not match")
        return self


class StudentRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    address: Address


DB: dict[int, dict] = {}


@app.post("/register", response_model=StudentRead, status_code=201)
def register(student: StudentCreate):
    new_id = len(DB) + 1
    DB[new_id] = {"id": new_id, **student.model_dump(exclude={"confirm_password"})}
    return DB[new_id]


def test_registration_project():
    body = {"name": "Riya", "age": 20, "email": "riya@example.com",
            "address": {"city": "Pune", "pincode": "411001"},
            "password": "secret123", "confirm_password": "secret123"}
    r = c.post("/register", json=body)
    assert r.status_code == 201
    assert "password" not in r.json() and r.json()["id"] == 1
    body["confirm_password"] = "other"
    assert c.post("/register", json=body).status_code == 422


# --- level 3 additions: all errors at once, and the PATCH data-loss mistake
def test_all_errors_reported_at_once():
    try:
        StrictStudent(name="R", age=12, email="nope")
    except ValidationError as e:
        errs = {err["loc"][0]: err["msg"] for err in e.errors()}
    assert errs["name"] == "String should have at least 2 characters"
    assert errs["age"] == "Input should be greater than or equal to 16"
    assert errs["email"].startswith("value is not a valid email address")


bug = FastAPI()
STORE: dict[int, TaskRead] = {}


@bug.patch("/wrong/{task_id}")
def update_wrong(task_id: int, changes: TaskUpdate):
    stored = STORE[task_id]
    updates = changes.model_dump()
    STORE[task_id] = stored.model_copy(update=updates)
    return STORE[task_id]


@bug.patch("/right/{task_id}")
def update_right(task_id: int, changes: TaskUpdate):
    stored = STORE[task_id]
    updates = changes.model_dump(exclude_unset=True)
    STORE[task_id] = stored.model_copy(update=updates)
    return STORE[task_id]


def test_patch_mistake_silently_loses_data():
    bc = TestClient(bug)
    STORE[1] = TaskRead(id=1, title="Write docs")
    r = bc.patch("/wrong/1", json={"done": True})
    assert r.status_code == 200 and r.json()["title"] is None  # silent data loss
    STORE[1] = TaskRead(id=1, title="Write docs")
    assert bc.patch("/right/1", json={"done": True}).json()["title"] == "Write docs"


def test_field_examples():
    class TaskCreate(BaseModel):
        title: str = Field(min_length=1, max_length=100, examples=["Write the API docs"])

    assert TaskCreate.model_json_schema()["properties"]["title"]["examples"] == ["Write the API docs"]
