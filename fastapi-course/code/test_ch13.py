"""Chapter 13 examples, runnable: URL shortener, blog slugs/visibility, orders (atomic stock, idempotency, cents)."""
import asyncio
import re
import string
import unicodedata
from datetime import datetime, timezone
from enum import Enum
from typing import Annotated, AsyncIterator

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field, HttpUrl
from sqlalchemy import String, select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.pool import NullPool

# --- URL shortener -----------------------------------------------------------
ALPHABET = string.digits + string.ascii_lowercase + string.ascii_uppercase


def encode_base62(n: int) -> str:
    if n == 0:
        return ALPHABET[0]
    out = []
    while n:
        n, rem = divmod(n, 62)
        out.append(ALPHABET[rem])
    return "".join(reversed(out))


def decode_base62(code: str) -> int:
    n = 0
    for ch in code:
        n = n * 62 + ALPHABET.index(ch)
    return n


short = FastAPI()
LINKS: dict[int, dict] = {}


class LinkIn(BaseModel):
    url: HttpUrl


@short.post("/links", status_code=201)
async def create_link(data: LinkIn):
    link_id = len(LINKS) + 100_000
    LINKS[link_id] = {"url": str(data.url), "clicks": 0}
    return {"code": encode_base62(link_id), "url": str(data.url)}


@short.get("/{code}")
async def follow(code: str):
    link = LINKS.get(decode_base62(code)) if code.isalnum() else None
    if link is None:
        raise HTTPException(404, "Link not found")
    link["clicks"] += 1
    return RedirectResponse(link["url"], status_code=307)


def test_base62_roundtrip_and_redirect():
    assert encode_base62(100_000) == "q0U"
    assert all(decode_base62(encode_base62(n)) == n for n in (0, 1, 61, 62, 3843, 10**12))
    c = TestClient(short)
    r = c.post("/links", json={"url": "https://fastapi.tiangolo.com"})
    code = r.json()["code"]
    r = c.get(f"/{code}", follow_redirects=False)
    assert r.status_code == 307 and r.headers["location"] == "https://fastapi.tiangolo.com/"
    assert LINKS[decode_base62(code)]["clicks"] == 1
    assert c.post("/links", json={"url": "javascript:alert(1)"}).status_code == 422
    assert c.get("/zzzz", follow_redirects=False).status_code == 404


# --- Blog / CMS --------------------------------------------------------------
def slugify(title: str) -> str:
    text = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def unique_slug(title: str, taken: set[str]) -> str:
    base = slug = slugify(title)
    n = 2
    while slug in taken:
        slug = f"{base}-{n}"
        n += 1
    return slug


class Status(str, Enum):
    draft = "draft"
    published = "published"


def test_slugs():
    assert slugify("FastAPI in 2026: Café Edition!") == "fastapi-in-2026-cafe-edition"
    assert unique_slug("Hello World", {"hello-world", "hello-world-2"}) == "hello-world-3"


blog = FastAPI()
POSTS = [
    {"slug": "hello", "status": Status.published, "author_id": 1},
    {"slug": "secret-draft", "status": Status.draft, "author_id": 1},
]


async def current_user_id(x_user: Annotated[int | None, Header()] = None) -> int | None:
    return x_user


@blog.get("/posts/{slug}")
async def read_post(slug: str, user_id: Annotated[int | None, Depends(current_user_id)]):
    post = next((p for p in POSTS if p["slug"] == slug), None)
    visible = post and (post["status"] == Status.published or post["author_id"] == user_id)
    if not visible:
        raise HTTPException(404, "Post not found")
    return post


def test_drafts_hidden_from_public():
    c = TestClient(blog)
    assert c.get("/posts/hello").status_code == 200
    assert c.get("/posts/secret-draft").status_code == 404
    assert c.get("/posts/secret-draft", headers={"X-User": "2"}).status_code == 404
    assert c.get("/posts/secret-draft", headers={"X-User": "1"}).status_code == 200


# --- E-commerce orders -------------------------------------------------------
def test_float_money_is_wrong():
    assert 0.1 + 0.2 != 0.3
    assert 10 + 20 == 30  # cents


class Base(DeclarativeBase):
    pass


class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    price_cents: Mapped[int]
    stock: Mapped[int]


class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int]
    quantity: Mapped[int]
    total_cents: Mapped[int]
    idempotency_key: Mapped[str] = mapped_column(String(64), unique=True)


engine = create_async_engine("sqlite+aiosqlite:////tmp/ch13_shop.db", poolclass=NullPool)
Session = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with Session() as s:
        yield s


SessionDep = Annotated[AsyncSession, Depends(get_session)]
shop = FastAPI()


class OrderIn(BaseModel):
    product_id: int
    quantity: int = Field(gt=0, le=10)


async def reserve_stock_unsafe(session: AsyncSession, product_id: int, qty: int) -> bool:
    product = await session.get(Product, product_id)
    if product.stock < qty:
        return False
    await asyncio.sleep(0.01)  # another request runs here
    product.stock -= qty
    return True


async def reserve_stock(session: AsyncSession, product_id: int, qty: int) -> bool:
    result = await session.execute(
        update(Product)
        .where(Product.id == product_id, Product.stock >= qty)
        .values(stock=Product.stock - qty)
    )
    return result.rowcount == 1


@shop.post("/orders", status_code=201)
async def place_order(data: OrderIn, session: SessionDep,
                      idempotency_key: Annotated[str, Header(min_length=8, max_length=64)]):
    if existing := await session.scalar(
            select(Order.id).where(Order.idempotency_key == idempotency_key)):
        return {"order_id": existing, "replayed": True}
    if not await reserve_stock(session, data.product_id, data.quantity):
        raise HTTPException(409, "Out of stock")
    product = await session.get(Product, data.product_id)
    order = Order(product_id=product.id, quantity=data.quantity,
                  total_cents=product.price_cents * data.quantity, idempotency_key=idempotency_key)
    session.add(order)
    await session.commit()
    return {"order_id": order.id, "total_cents": order.total_cents, "replayed": False}


async def reset(stock: int):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    async with Session() as s:
        s.add(Product(id=1, name="Keyboard", price_cents=249_900, stock=stock))
        await s.commit()


async def stock_now() -> int:
    async with Session() as s:
        return (await s.get(Product, 1)).stock


def test_unsafe_reservation_oversells():
    async def main():
        await reset(stock=1)

        async def buyer():
            async with Session() as s:
                ok = await reserve_stock_unsafe(s, 1, 1)
                await s.commit()
                return ok
        results = await asyncio.gather(buyer(), buyer())
        return results, await stock_now()
    results, stock = asyncio.run(main())
    assert results == [True, True]  # two customers both "bought" the last keyboard
    assert stock == 0               # ...but stock only went down once


def test_atomic_reservation_never_oversells():
    async def main():
        await reset(stock=1)

        async def buyer():
            async with Session() as s:
                ok = await reserve_stock(s, 1, 1)
                await s.commit()
                return ok
        results = await asyncio.gather(*(buyer() for _ in range(5)))
        return results, await stock_now()
    results, stock = asyncio.run(main())
    assert results.count(True) == 1 and stock == 0


def test_idempotent_orders():
    asyncio.run(reset(stock=5))
    c = TestClient(shop)
    h = {"Idempotency-Key": "a1b2c3d4-retry"}
    r1 = c.post("/orders", json={"product_id": 1, "quantity": 2}, headers=h)
    r2 = c.post("/orders", json={"product_id": 1, "quantity": 2}, headers=h)
    assert r1.status_code == 201 and r1.json() == {"order_id": 1, "total_cents": 499_800, "replayed": False}
    assert r2.json() == {"order_id": 1, "replayed": True}
    assert asyncio.run(stock_now()) == 3
    r3 = c.post("/orders", json={"product_id": 1, "quantity": 9}, headers={"Idempotency-Key": "other-key-1"})
    assert r3.status_code == 409
    assert c.post("/orders", json={"product_id": 1, "quantity": 1}).status_code == 422
