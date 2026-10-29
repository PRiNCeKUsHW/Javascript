"""Chapter 2 examples, runnable."""
from enum import Enum
from typing import Annotated

from fastapi import FastAPI, Path, Query
from fastapi.testclient import TestClient

app = FastAPI()


@app.get("/users/me")
def read_current_user():
    return {"user": "the current user"}


@app.get("/users/{user_id}")
def read_user(user_id: int):
    return {"user_id": user_id}


class Genre(str, Enum):
    action = "action"
    comedy = "comedy"
    drama = "drama"


@app.get("/movies/genre/{genre}")
def movies_by_genre(genre: Genre):
    if genre is Genre.comedy:
        return {"genre": genre, "tip": "Get the popcorn ready!"}
    return {"genre": genre}


@app.get("/movies/{movie_id}")
def get_movie(
    movie_id: Annotated[int, Path(ge=1, description="Movie ID")],
    q: Annotated[str | None, Query(min_length=3, max_length=50)] = None,
):
    return {"movie_id": movie_id, "q": q}


@app.get("/square/{n}")
def square(n: Annotated[int, Path(ge=1, le=100)]):
    return {"n": n, "square": n * n}


@app.get("/search")
def search(q: Annotated[str, Query(min_length=3)]):
    return {"q": q}


@app.get("/posts")
def posts(tag: Annotated[list[str] | None, Query()] = None):
    return {"tags": tag or []}


@app.get("/stream")
def stream(hd: bool = False):
    return {"hd": hd}


c = TestClient(app)


def test_route_order():
    assert c.get("/users/me").json() == {"user": "the current user"}
    assert c.get("/users/7").json() == {"user_id": 7}


def test_route_order_bug():
    bad = FastAPI()

    @bad.get("/users/{user_id}")
    def read_user(user_id: int):
        return {"user_id": user_id}

    @bad.get("/users/me")
    def me():
        return {}

    assert TestClient(bad).get("/users/me").status_code == 422


def test_enum():
    assert c.get("/movies/genre/comedy").json()["tip"]
    assert c.get("/movies/genre/horror").status_code == 422


def test_annotated_validation():
    assert c.get("/movies/0").status_code == 422
    assert c.get("/movies/3?q=abc").json() == {"movie_id": 3, "q": "abc"}
    assert c.get("/movies/3?q=ab").status_code == 422


def test_square():
    assert c.get("/square/12").json()["square"] == 144
    assert c.get("/square/101").status_code == 422


def test_required_and_short():
    assert c.get("/search?q=py").json()["detail"][0]["type"] == "string_too_short"
    assert c.get("/search").json()["detail"][0]["type"] == "missing"


def test_list_query():
    assert c.get("/posts?tag=python&tag=api").json() == {"tags": ["python", "api"]}


def test_bool_parsing():
    for v in ("1", "yes", "on", "TRUE"):
        assert c.get(f"/stream?hd={v}").json() == {"hd": True}
    for v in ("0", "no", "off", "false"):
        assert c.get(f"/stream?hd={v}").json() == {"hd": False}
    assert c.get("/stream?hd=maybe").status_code == 422


# --- query filter example
q_app = FastAPI()
MOVIES_SIMPLE = [{"title": "Inception", "year": 2010}, {"title": "Dangal", "year": 2016}]


@q_app.get("/movies")
def list_simple(skip: int = 0, limit: int = 10, year: int | None = None):
    results = [m for m in MOVIES_SIMPLE if year is None or m["year"] == year]
    return results[skip : skip + limit]


def test_query_filters():
    qc = TestClient(q_app)
    assert qc.get("/movies?year=2016&limit=5").json() == [{"title": "Dangal", "year": 2016}]
    assert qc.get("/movies?limit=abc").json()["detail"][0]["loc"] == ["query", "limit"]


# --- Level project: Movie Catalog
catalog = FastAPI(title="Movie Catalog")


class CGenre(str, Enum):
    action = "action"
    drama = "drama"
    comedy = "comedy"


MOVIES = [
    {"id": 1, "title": "Inception", "year": 2010, "genre": "action", "rating": 8.8},
    {"id": 2, "title": "Dangal", "year": 2016, "genre": "drama", "rating": 8.3},
]


@catalog.get("/movies")
def list_movies(
    genre: CGenre | None = None,
    year: int | None = None,
    min_rating: Annotated[float, Query(ge=0, le=10)] = 0,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
):
    results = [
        m for m in MOVIES
        if (genre is None or m["genre"] == genre)
        and (year is None or m["year"] == year)
        and m["rating"] >= min_rating
    ]
    return {"total": len(results), "items": results[skip : skip + limit]}


def test_catalog_project():
    cc = TestClient(catalog)
    assert cc.get("/movies?genre=drama").json()["items"][0]["title"] == "Dangal"
    assert cc.get("/movies?min_rating=8.5").json()["total"] == 1
    assert cc.get("/movies?limit=51").status_code == 422
    assert cc.get("/movies?min_rating=11").status_code == 422
