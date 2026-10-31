# Module 1 question bank: Python for AI Engineering

Every question asked in the Module 1 videos, with answers. **9 questions.**

How to use it: read the question, answer it out loud or on paper, *then* click **Show answer**. Getting one wrong is useful: rewatch that lesson's chapter.

Short answer key, practice answers and the extension challenge: [quiz.md](quiz.md) · Module guide: [README.md](README.md)

## Lesson 2: Python Core Data: Variables, Lists, Dictionaries and Sets

### Quick check

**What does this code print?**

```python
message = {"role": "user", "content": "Hi"}
print(message.get("model", "unknown"))
```

- A) `None`
- B) `unknown`
- C) A `KeyError`
- D) `model`

<details>
<summary>Show answer</summary>

**B) `unknown`**

`.get()` returns the default, `"unknown"`, when the key is missing. Only `message["model"]` would raise a `KeyError`.

</details>

## Lesson 3: Functions, Classes and Exceptions

### Quick check

**Why is `def add(msg, history=[])` dangerous?**

- A) Lists can't be parameters
- B) The same list is shared by every call that uses the default
- C) It makes the function slow
- D) `history` becomes read-only

<details>
<summary>Show answer</summary>

**B) The same list is shared by every call that uses the default**

Default values are created **once**, when the function is defined. Use `history=None` and create a new list inside.

</details>

## Lesson 4: Modules, Packages, Files, JSON and Environment Variables

### Quick check

**Which call turns the JSON text `'{"ok": true}'` into a Python dictionary?**

- A) `json.dumps(text)`
- B) `json.loads(text)`
- C) `dict(text)`
- D) `json.load(text)`

<details>
<summary>Show answer</summary>

**B) `json.loads(text)`**

`loads` = load from a **string**. `dumps` goes the other way. `json.load` (no s) reads from an open **file** object, not a string.

</details>

## Lesson 5: Type Hints, HTTP Requests and Async

### Quick check

**An API replies with status `429`. What does it mean, and what should your code do?**

- A) The URL is wrong: fix it
- B) Too many requests: wait, then retry
- C) Success: read the body
- D) The server crashed: give up

<details>
<summary>Show answer</summary>

**B) Too many requests: wait, then retry**

429 means you hit a **rate limit**. Wait (often the response says how long), then retry. Module 2 implements this with backoff.

</details>

## Lesson 7: Project, Part 2: Reports, CLI, Tests and Wrap-up

### Module quiz

**Q1. An agent may only use the tools `search` and `calculator`. Which structure gives the fastest "is this tool allowed?" check?**

- A) A list
- B) A set
- C) A string
- D) A tuple

<details>
<summary>Show answer</summary>

**B) A set**

Membership checks on a **set** are fast however many items it holds, and duplicates are impossible.

</details>

**Q2. What does `@dataclass(frozen=True)` add to `UsageRecord`?**

- A) Faster JSON parsing
- B) Automatic validation of types
- C) Fields can't be changed after creation
- D) It can't be printed

<details>
<summary>Show answer</summary>

**C) Fields can't be changed after creation**

Frozen dataclasses raise an error if you assign to a field after creation. Note: a dataclass does **not** validate types; that's why `from_dict` checks them.

</details>

**Q3. In `try / except / else / finally`, which block runs every time?**

- A) `try`
- B) `except`
- C) `else`
- D) `finally`

<details>
<summary>Show answer</summary>

**D) `finally`**

`finally` always runs, success or failure, which makes it the place for cleanup.

</details>

**Q4. Why does `fetch_all` use `asyncio.gather`?**

- A) To retry failed downloads
- B) To download all URLs concurrently, so total time ≈ the slowest one
- C) To use more CPU cores
- D) Because `httpx` requires it

<details>
<summary>Show answer</summary>

**B) To download all URLs concurrently, so total time ≈ the slowest one**

`gather` waits for all downloads at once. It saves waiting time; it doesn't add CPU power.

</details>

**Q5. Where should the real API key for your project live?**

- A) In `config.py`
- B) In `.env.example`
- C) In an environment variable or a git-ignored `.env`
- D) In the README

<details>
<summary>Show answer</summary>

**C) In an environment variable or a git-ignored `.env`**

Secrets live in environment variables (or a `.env` that is in `.gitignore`). `.env.example` holds only fake placeholder values.

</details>
