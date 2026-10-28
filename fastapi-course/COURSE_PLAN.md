# FastAPI: Zero to Production — Course Plan

A complete video course that takes a Python beginner to building, testing, securing and
deploying production FastAPI services. Every chapter ends with **Practice Questions**
(pause-and-try, then the answer) and a **Mock Interview** (interviewer asks, model answer
explained).

## Audience, language and teaching style

- **Audience:** college students and working professionals who want FastAPI for projects, jobs and interviews.
- **Language:** narration in **Hinglish** (Hindi + English tech terms, the way developers actually talk);
  on-screen titles, points and code in English so they read like real documentation.
- **Style:** easy first. Every new idea starts with an everyday analogy ("API ek restaurant ke waiter jaisa hai"),
  then the code, then why it matters at work. Short sentences, one idea per slide, no jargon without a meaning.

## Outcome

- **Starts at:** knows basic Python (functions, classes, `pip`), has never built an API.
- **Ends at:** can design a layered FastAPI service with a real database, auth, tests,
  background work, Docker and CI, and can answer FastAPI interview questions from junior to
  senior level.

## Video format

| Item | Choice |
| --- | --- |
| Canvas | 1920x1080, 30 fps, one MP4 per chapter + one full-course MP4 |
| Length | about 3.5 hours in total: ~16 min per level (lesson ~7, challenges ~3, project ~2, boss round ~4) |
| Narration | Hinglish, built-in local TTS. Instructor: Hindi female voice (`hf_alpha`). Mock interviewer: Hindi male voice (`hm_omega`). |
| Look | Light studio-white ground, FastAPI teal `#05998B` brand rail, dark editor panels for code, Inter / Outfit / JetBrains Mono |
| Code | 34–38 px JetBrains Mono, syntax highlighted, revealed line by line in sync with the narration, the line being explained is highlighted |
| Extras | Hinglish `.srt` subtitles per chapter, YouTube chapter timestamps for the full video |
| Accuracy | Every Python snippet is compiled, and each chapter's main app is run under pytest before rendering |

## Segment types used in every chapter

1. **Title card** — chapter number, title, what you will learn.
2. **Concept** — heading + 3–5 points revealed as they are spoken.
3. **Flow diagram** — e.g. request → middleware → router → dependencies → handler → response.
4. **Code walkthrough** — a file builds up line by line; the active line is highlighted.
5. **Terminal** — command typed, output appears.
6. **Recap** — the chapter's key takeaways.
7. **Challenge Time** (5 practice questions) — question on screen, 5-second "pause and solve" timer, then the solution.
8. **Project Time** — the Level Project brief, build it yourself, then the solution walkthrough.
9. **Boss Round** (5 mock-interview questions) — tagged Junior / Mid / Senior; interviewer voice asks, the model answer's key points build on screen.
10. **Level Complete** — stars, a skill badge, the next level, "comment your answers".

## Theme: Code Quest

The course plays like a game so learners stay engaged: each chapter is a **Level** on a course map,
an **XP bar** fills as you watch, a speaking waveform shows when the instructor talks, and **Byte**,
a friendly robot guide, appears on the level map, section breaks and the Level Complete screen.

## Practice projects

Projects are where the concepts stick, so every level ends its practice with a **Level Project**:
a brief (each requirement tagged with the concept it practises), the endpoints to build, a pause to
build it yourself, a short solution walkthrough, and a stretch goal.

| Level | Project | Concepts practised |
| --- | --- | --- |
| 1 | Personal Profile API | routes, path params, JSON responses, `/docs` |
| 2 | Movie Catalog Search API | path vs query params, `Enum` genres, filters, validation |
| 3 | Student Registration API | Pydantic models, `Field` rules, validators, nested models, create/update schemas |
| 4 | Notes API with clean errors | status codes, `response_model`, `HTTPException`, custom error handler |
| 5 | Library API with API keys | dependencies: API-key header, pagination, shared services, overrides |
| 6 | TaskHub v1: tasks CRUD | SQLAlchemy 2.0 async, sessions, Alembic migrations |
| 7 | TaskHub v2: clean architecture | `APIRouter`, layers, `pydantic-settings`, lifespan |
| 8 | TaskHub v3: users and JWT login | password hashing, OAuth2 + JWT, per-user data, roles |
| 9 | TaskHub v4: reminders and middleware | async I/O, `BackgroundTasks`, request-ID middleware |
| 10 | TaskHub test suite | pytest, fixtures, test DB, dependency overrides, coverage |
| 11 | TaskHub live: attachments and notifications | uploads, WebSockets, cursor pagination, caching |
| 12 | Ship TaskHub | Docker, Postgres, health checks, logging, GitHub Actions CI |

**Bonus episode — Portfolio Projects (Level 13):** three resume-grade builds with architecture,
endpoints, key code and the interview talking points for each:
1. **URL Shortener** — Redis caching, rate limiting, click analytics.
2. **Blog / CMS API** — authors and editors (roles), drafts and publishing, search, pagination.
3. **E-commerce Orders API** — inventory, idempotency keys, payment-webhook simulation, background jobs.

## Running project

From Chapter 6 onward we build one app, **TaskHub** — a multi-user task manager API — and
take it all the way to production: database, layered structure, JWT auth, background
emails, tests, Docker, CI and observability.

## Chapters

### 0. Welcome (≈2 min)
Why FastAPI, what we build, course roadmap, how practice and interview segments work.

### 1. Getting Started
- What FastAPI is: Starlette + Pydantic, ASGI, type hints drive validation and docs
- Virtual environment, `pip install "fastapi[standard]"`
- First app: `app = FastAPI()`, `@app.get("/")`
- `fastapi dev main.py` vs `fastapi run`, Uvicorn underneath
- Interactive docs at `/docs` (Swagger UI) and `/redoc`, the OpenAPI schema at `/openapi.json`
- **Practice:** run the app on another port, add a `/health` route, find a route in the OpenAPI JSON, …
- **Interview:** WSGI vs ASGI, why FastAPI is fast, where validation comes from, …

### 2. Path and Query Parameters
- Path parameters with types and automatic conversion; route order matters
- `Enum` path parameters
- Query parameters: required, optional (`str | None = None`), defaults, `bool` parsing, lists
- Validation with `Annotated[..., Path(ge=1)]` and `Query(min_length=…, max_length=…, pattern=…)`
- The 422 error response and how to read it
- **Practice / Interview:** route ordering bugs, path vs query design, validation errors, …

### 3. Request Bodies and Pydantic v2
- `BaseModel` request bodies, optional fields and defaults
- `Field(...)` constraints, examples, aliases
- Nested models and lists of models
- `@field_validator` and `@model_validator`
- Separate input / output models (`TaskCreate`, `TaskRead`, `TaskUpdate`), `model_dump(exclude_unset=True)` for PATCH
- **Practice / Interview:** v1 → v2 changes, partial updates, why separate schemas, …

### 4. Responses, Status Codes and Errors
- `response_model` and filtering sensitive fields; `response_model_exclude_unset`
- `status_code=201`, `204 No Content`, the `status` module
- `HTTPException`, custom exception classes and `@app.exception_handler`
- A consistent error envelope for an API
- `JSONResponse`, `RedirectResponse`, `FileResponse`, `StreamingResponse` overview
- **Practice / Interview:** 400 vs 404 vs 409 vs 422, leaking data through responses, …

### 5. Dependency Injection
- `Depends` with functions and `Annotated` aliases (`SessionDep`, `CurrentUser`)
- Shared query parameters as a dependency, class-based dependencies
- Sub-dependencies and caching per request
- `yield` dependencies for setup and teardown
- Router-level and app-level dependencies
- `app.dependency_overrides` for testing
- **Practice / Interview:** how DI enables testing, dependency caching, yield cleanup order, …

### 6. Databases with SQLAlchemy 2.0 (TaskHub begins)
- SQLAlchemy 2.0 typed models (`Mapped`, `mapped_column`)
- Async engine and `async_sessionmaker`, a session-per-request dependency
- CRUD endpoints for tasks: create, list with filters, get, update, delete
- Migrations with Alembic (`init`, `revision --autogenerate`, `upgrade head`)
- N+1 queries and `selectinload`; transactions and rollback
- **Practice / Interview:** session lifecycle, why migrations, sync vs async drivers, …

### 7. Structuring Larger Applications
- `APIRouter` with prefixes, tags and per-router dependencies
- Project layout: `api/` (routers), `schemas/`, `models/`, `services/`, `repositories/`, `core/`
- Configuration with `pydantic-settings` and `.env` files, per-environment settings
- The `lifespan` context manager for startup and shutdown
- API versioning (`/api/v1`)
- **Practice / Interview:** where business logic lives, settings management, circular imports, …

### 8. Authentication and Authorization
- Password hashing with `pwdlib` (Argon2) — never store plain passwords
- OAuth2 password flow with `OAuth2PasswordBearer` and `OAuth2PasswordRequestForm`
- JWT access tokens with PyJWT: claims, expiry, signing secret
- `get_current_user` dependency; roles and permission checks; resource ownership
- Refresh tokens, CORS, and common security mistakes
- **Practice / Interview:** JWT vs sessions, token revocation, storing tokens, 401 vs 403, …

### 9. Async, Background Work, Middleware and Lifespan
- `async def` vs `def` endpoints, the event loop and the threadpool; never block the loop
- Calling other services with `httpx.AsyncClient`
- `BackgroundTasks` for small jobs; a task queue (Celery / ARQ) for heavy or retried work
- Middleware: timing header, request IDs; `CORSMiddleware`, `GZipMiddleware`
- **Practice / Interview:** what blocks the event loop, BackgroundTasks limits, middleware vs dependency, …

### 10. Testing FastAPI Apps
- `TestClient` and pytest basics
- Async tests with `httpx.AsyncClient` + `ASGITransport`
- Test database per test, fixtures, `dependency_overrides` for auth and DB
- Testing errors, auth flows and edge cases; coverage
- **Practice / Interview:** unit vs integration tests, mocking external APIs, test isolation, …

### 11. Advanced Features
- File uploads with `UploadFile`, size and type checks
- `StreamingResponse` and server-sent events
- WebSockets: connect, receive, broadcast to a room
- Pagination (limit/offset and cursor), filtering and sorting
- Caching with Redis and rate limiting
- **Practice / Interview:** offset vs cursor pagination, WebSocket scaling, cache invalidation, …

### 12. Production Deployment
- Running in production: `fastapi run` / Uvicorn workers, Gunicorn, behind a reverse proxy
- Docker: slim multi-stage image, non-root user, health check
- Configuration and secrets, structured JSON logging, request IDs
- Health and readiness endpoints, metrics and tracing (Prometheus, OpenTelemetry)
- CI/CD with GitHub Actions: lint, type-check, test, build and push image
- Security and performance checklist; TaskHub's final architecture
- **Practice / Interview:** zero-downtime deploys, scaling horizontally, 12-factor config, debugging prod, …

## Production pipeline

1. Each chapter is written as a structured script in `content/chNN.md` (segments, narration, code, practice, interview).
2. `tools/verify_code.py` compiles every snippet and runs each chapter's example tests.
3. `tools/build.py` makes the narration per line (local TTS), times every reveal to its line, and generates a HyperFrames project per chapter under `build/chNN/`.
4. `npx hyperframes check` and frame snapshots for review, then render `renders/chNN.mp4`.
5. `tools/assemble.py` joins the chapters into `renders/fastapi-full-course.mp4` and writes the YouTube chapter list and subtitles.
