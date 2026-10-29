import asyncio
import json
from pathlib import Path
from typing import Any

import httpx

from toolkit.errors import ToolkitError


async def fetch_one(client: httpx.AsyncClient, url: str) -> list[Any]:
    try:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()
    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code
        raise ToolkitError(f"{url} returned HTTP {status}") from None
    except httpx.RequestError as exc:
        reason = type(exc).__name__
        raise ToolkitError(f"could not reach {url}: {reason}") from None
    except json.JSONDecodeError:
        raise ToolkitError(f"{url} did not return JSON") from None
    if not isinstance(data, list):
        raise ToolkitError(f"{url} must return a JSON list of records")
    return data


async def fetch_all(urls: list[str],
                    transport: httpx.AsyncBaseTransport | None = None,
                    ) -> list[Any]:
    """Download every URL at the same time; join the lists in order."""
    async with httpx.AsyncClient(timeout=10.0, transport=transport) as client:
        batches = await asyncio.gather(*(fetch_one(client, u) for u in urls))
    return [item for batch in batches for item in batch]


def save_json(data: list[Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
