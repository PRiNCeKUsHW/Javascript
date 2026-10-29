# comprehensions.py: build new collections in one readable line
records = [
    {"id": "req-1", "tokens": 600, "status": "ok"},
    {"id": "req-2", "tokens": 0, "status": "error"},
    {"id": "req-3", "tokens": 250, "status": "ok"},
]
ok_ids = [r["id"] for r in records if r["status"] == "ok"]
print(ok_ids)

tokens_by_id = {r["id"]: r["tokens"] for r in records}
print(tokens_by_id)

print(sum(r["tokens"] for r in records), "tokens in total")
