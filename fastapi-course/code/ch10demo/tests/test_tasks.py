import httpx

from app.main import app, get_http


async def test_create_and_list_tasks(client, auth_headers):
    headers = await auth_headers()
    r = await client.post("/tasks", json={"title": "Write tests"}, headers=headers)
    assert r.status_code == 201
    r = await client.get("/tasks", headers=headers)
    assert [t["title"] for t in r.json()] == ["Write tests"]


async def test_cannot_read_someone_elses_task(client, auth_headers):
    riya = await auth_headers("riya@example.com")
    aman = await auth_headers("aman@example.com")
    r = await client.post("/tasks", json={"title": "Riya's task"}, headers=riya)
    task_id = r.json()["id"]
    r = await client.get(f"/tasks/{task_id}", headers=aman)
    assert r.status_code == 404


def fake_http(handler):
    async def override():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as c:
            yield c
    return override


async def test_holiday_check_uses_fake_api(client, auth_headers):
    def handler(request):
        assert request.url.path == "/api/v3/PublicHolidays/2026/IN"
        return httpx.Response(200, json=[{"date": "2026-01-26"}])

    app.dependency_overrides[get_http] = fake_http(handler)
    headers = await auth_headers()
    r = await client.post("/tasks", json={"title": "Parade", "due": "2026-01-26"}, headers=headers)
    r = await client.get(f"/tasks/{r.json()['id']}/holiday-check", headers=headers)
    assert r.json() == {"due": "2026-01-26", "is_holiday": True}


async def test_holiday_api_down_is_503(client, auth_headers):
    def handler(request):
        raise httpx.ConnectTimeout("too slow")

    app.dependency_overrides[get_http] = fake_http(handler)
    headers = await auth_headers()
    r = await client.post("/tasks", json={"title": "Trip", "due": "2026-03-04"}, headers=headers)
    r = await client.get(f"/tasks/{r.json()['id']}/holiday-check", headers=headers)
    assert r.status_code == 503
