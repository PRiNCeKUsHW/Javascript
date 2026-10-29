import asyncio

import httpx
import pytest

from toolkit.errors import ToolkitError
from toolkit.fetch import fetch_all


def mock_transport():
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/a.json":
            return httpx.Response(200, json=[{"id": "a1"}, {"id": "a2"}])
        if request.url.path == "/b.json":
            return httpx.Response(200, json=[{"id": "b1"}])
        if request.url.path == "/object.json":
            return httpx.Response(200, json={"id": "x"})
        return httpx.Response(404)
    return httpx.MockTransport(handler)


def test_fetch_all_merges_in_order():
    urls = ["http://logs.test/a.json", "http://logs.test/b.json"]
    data = asyncio.run(fetch_all(urls, transport=mock_transport()))
    assert [row["id"] for row in data] == ["a1", "a2", "b1"]


def test_http_error_becomes_toolkit_error():
    urls = ["http://logs.test/missing.json"]
    with pytest.raises(ToolkitError, match="HTTP 404"):
        asyncio.run(fetch_all(urls, transport=mock_transport()))


def test_response_must_be_a_list():
    urls = ["http://logs.test/object.json"]
    with pytest.raises(ToolkitError, match="JSON list"):
        asyncio.run(fetch_all(urls, transport=mock_transport()))
