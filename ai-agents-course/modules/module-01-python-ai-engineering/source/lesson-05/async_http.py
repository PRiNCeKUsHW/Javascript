# async_http.py: several real HTTP requests at the same time
import asyncio

import httpx

URLS = [f"http://127.0.0.1:8765/{name}" for name in ("usage_sample.json", "usage_broken.json")]


async def fetch(client: httpx.AsyncClient, url: str) -> int:
    response = await client.get(url)
    response.raise_for_status()
    return len(response.json())


async def main() -> None:
    async with httpx.AsyncClient(timeout=5.0) as client:
        counts = await asyncio.gather(*(fetch(client, url) for url in URLS))
    for url, count in zip(URLS, counts):
        print(f"{count:>3} records from {url.rsplit('/', 1)[1]}")


asyncio.run(main())
