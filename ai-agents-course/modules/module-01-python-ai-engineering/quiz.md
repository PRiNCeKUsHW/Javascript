# Module 1 quiz with answers

Quick checks appear at the end of lessons 2–5; the five module questions close lesson 7.

## Lesson quick checks

**L2.** What does this print?
```python
message = {"role": "user", "content": "Hi"}
print(message.get("model", "unknown"))
```
A) `None` B) `unknown` C) a `KeyError` D) `model`
**Answer: B.** `.get()` returns the default when the key is missing; only `message["model"]` raises `KeyError`.

**L3.** Why is `def add(msg, history=[])` dangerous?
**Answer:** the default list is created once and shared by every call that uses it (one user's
messages leak into another's). Use `history=None` and create a new list inside.

**L4.** Which call turns the JSON text `'{"ok": true}'` into a Python dict?
A) `json.dumps(text)` B) `json.loads(text)` C) `dict(text)` D) `json.load(text)`
**Answer: B.** `loads` loads from a string; `dumps` goes the other way; `json.load` reads from an open file object.

**L5.** An API replies `429`. What does it mean, and what should your code do?
**Answer:** too many requests (rate limit). Wait, often for as long as the response says, then retry with backoff (Module 2).

## Module quiz

1. An agent may only use `search` and `calculator`. Fastest "is this tool allowed?" check?
   A) list B) **set** C) string D) tuple
   *Set membership stays fast however many items it holds, and duplicates are impossible.*
2. What does `@dataclass(frozen=True)` add to `UsageRecord`?
   A) faster JSON parsing B) automatic type validation C) **fields can't change after creation** D) can't be printed
   *Dataclasses do not validate types. That is why `from_dict` checks every field.*
3. In `try / except / else / finally`, which block runs every time?
   A) `try` B) `except` C) `else` D) **`finally`**
4. Why does `fetch_all` use `asyncio.gather`?
   **To download all URLs concurrently, so the total time is roughly the slowest download instead of the sum.**
   It saves waiting time; it does not add CPU power, and it does not retry.
5. Where should the real API key live?
   **In an environment variable or a git-ignored `.env` file.** `.env.example` holds only fake placeholders.

## Extension challenge (code + a test for each)

- `--top N` option for `report`.
- p95 latency (sort latencies, take the 95th-percentile value). Compare it with the 4,200 ms average.
- Per-day breakdown using `record.created_at.date()`.
- `--format csv` using the standard `csv` module.
