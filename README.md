<div align="center">

# <img src="images/logo.svg" width="500">

[![CI](https://github.com/RichardOyelowo/Snip/actions/workflows/ci.yml/badge.svg)](https://github.com/RichardOyelowo/Snip/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.14-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.129-green.svg)](https://fastapi.tiangolo.com/)
[![Status](https://img.shields.io/badge/Status-Active-success.svg)]()

A fast, minimal URL shortener built with FastAPI and PostgreSQL. Paste any long URL and get a clean, shareable short link instantly — no account required.

[![](https://img.shields.io/badge/Snip-snip--ly.xyz-e6be64?style=for-the-badge&logo=googlechrome&logoColor=white)](https://snip-ly.xyz)

---

![Snip Thumbnail](images/thumbnail.png)

---

</div>

## Table of Contents

- [Description](#description)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
  - [Local Setup](#local-setup)
  - [With Docker](#with-docker)
- [Environment Variables](#environment-variables)
- [Project Structure](#project-structure)
- [API Routes](#api-routes)
- [Database Schema](#database-schema)
  - [Tables](#tables)
  - [Relationships](#relationships)
- [Architecture Decisions](#architecture-decisions)
  - [Base62 Encoding](#base62-encoding)
  - [Async SQLAlchemy](#async-sqlalchemy)
  - [Click Tracking](#click-tracking)
- [Testing](#testing)
- [Security](#security)
- [What I Learned](#what-i-learned)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Description

Snip was built to practice async FastAPI, Docker deployment, and production database management. It handles URL shortening with Base62 encoding, tracks clicks per link, and includes a protected admin dashboard for managing all links and analytics.

The project deliberately avoids user accounts — the goal was to build a clean, stateless public tool and focus on the backend architecture: async database operations, containerization, and deployment pipeline rather than auth complexity.

No bloat — just paste, shorten, share.

---

## Features

- ✅ **Instant URL shortening** – Base62 encoded short codes generated from auto-incrementing IDs
- ✅ **Click tracking** – Every redirect logs a `Click` record with a timestamp
- ✅ **Duplicate detection** – Same URL always returns the same short link, no duplicates in DB
- ✅ **Admin dashboard** – sqladmin panel with session-based login protection
- ✅ **Auto http prefix** – Bare URLs get `https://` prepended automatically
- ✅ **404 handling** – Custom styled page for unknown short codes
- ✅ **Dockerized** – App + PostgreSQL run together via docker-compose
- ✅ **Auto migrations** – `start.sh` runs Alembic migrations on every deploy
- ✅ **Integration tested** – Full pytest-asyncio test suite with SQLite in-memory DB

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Backend** | Python, FastAPI | Async web framework |
| **Database** | PostgreSQL | Persistent storage |
| **ORM** | async SQLAlchemy | Non-blocking DB operations |
| **Migrations** | Alembic | Schema versioning |
| **Admin** | sqladmin | Auto-generated admin UI |
| **Frontend** | Jinja2, custom CSS | Server-rendered templates |
| **Containerization** | Docker, docker-compose | Consistent environments |
| **Deployment** | Railway | Cloud hosting |
| **Testing** | pytest, pytest-asyncio, httpx, aiosqlite | Async integration tests |

---

## Quick Start

### Local Setup

```bash
# Clone and setup
git clone https://github.com/RichardOyelowo/Snip.git
cd Snip
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your database credentials

# Run migrations
alembic upgrade head

# Start the server
fastapi dev app/main.py
# Visit http://localhost:8000
```

### With Docker

```bash
# Builds app + spins up PostgreSQL container
docker-compose up --build

# Run migrations inside the container
docker-compose run app alembic upgrade head

# Visit http://localhost:8000
```

> **Note:** In Docker, the database host is `db` (the service name), not `localhost`. Make sure your `DATABASE_URL` reflects this — see Environment Variables below.

---

## Environment Variables

Create a `.env` file in the project root:

```bash
# Async URL for SQLAlchemy (runtime)
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/snip_db

# Sync URL for Alembic (migrations only)
DATABASE_SYNC_URL=postgresql://user:password@localhost:5432/snip_db

# Session signing key for sqladmin
SECRET_KEY=your-secret-key

# Admin dashboard password
ADMIN_PASSWORD=your-admin-password

# Docker only — used to initialize the PostgreSQL container
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=snip_db
```

> **Docker vs Local:** Change `localhost` to `db` in both database URLs when running with docker-compose, since `db` is the PostgreSQL service name on Docker's internal network.

---

## Project Structure

```
Snip/
│
├── app/
│   ├── main.py              # FastAPI app, middleware, sqladmin setup
│   ├── database.py          # Async engine, session, SessionDep
│   ├── models.py            # Link and Click SQLAlchemy models
│   ├── schemas.py           # Pydantic request/response schemas
│   ├── templates_config.py  # Shared Jinja2 templates instance
│   ├── utils.py             # Base62 encoding, API key verification
│   │
│   ├── routers/
│   │   ├── links.py         # Public routes (POST /links/, GET /{shortcode})
│   │   └── admin.py         # Admin API routes (/api/admin/*, X-Admin-Key protected)
│   │
│   ├── templates/
│   │   ├── layout.html      # Base template (nav, footer, bg elements)
│   │   ├── index.html       # Landing page with URL form
│   │   ├── result.html      # Result page with copy button
│   │   └── link_not_found.html
│   │
│   └── static/              # CSS, SVG logos, favicon
│
├── migrations/              # Alembic migration files
├── tests/
│   ├── conftest.py          # Fixtures: async SQLite DB, test client, dependency overrides
│   ├── test_links.py        # Integration tests for public routes
│   └── test_admin.py        # Integration tests for admin API routes
├── Dockerfile
├── docker-compose.yml
├── start.sh                 # Runs alembic upgrade head then starts server
├── alembic.ini
└── requirements.txt
```

---

## API Routes

### Public

| Method | Route | Description |
|--------|-------|-------------|
| `GET` | `/` | Landing page with URL form |
| `POST` | `/links/` | Shorten a URL (form submission) |
| `GET` | `/{shortcode}` | Redirect to original URL, log click |

### Admin API (X-Admin-Key header required)

| Method | Route | Description |
|--------|-------|-------------|
| `GET` | `/api/admin/links` | List all links with click counts |
| `GET` | `/api/admin/links/{shortcode}/analytics/` | Full click history for a link |
| `DELETE` | `/api/admin/links/{id}` | Delete a link and its clicks |

### Admin Dashboard

| Route | Description |
|-------|-------------|
| `/admin/` | sqladmin UI — browse and manage Link and Click records |

> **Note:** The admin JSON API uses the `/api/admin` prefix to avoid conflict with sqladmin, which mounts at `/admin` at the ASGI level and intercepts all `/admin/*` requests before FastAPI's router.

---

## Database Schema

### Tables

**link**
```sql
id           SERIAL PRIMARY KEY
original_url VARCHAR NOT NULL
short_code   VARCHAR UNIQUE
click_count  INTEGER DEFAULT 0
created_at   TIMESTAMP DEFAULT now()
```

**click**
```sql
id         SERIAL PRIMARY KEY
link_id    INTEGER REFERENCES link(id)
created_at TIMESTAMP DEFAULT now()
```

### Relationships

- `Link` → `Click`: one-to-many. Each redirect creates one `Click` record.
- `click_count` on `Link` is a denormalized counter updated on every redirect for fast reads without aggregation queries.

---

## Architecture Decisions

### Base62 Encoding

Short codes are generated from the auto-incremented `id` using Base62 encoding (`0-9`, `a-z`, `A-Z`). This guarantees uniqueness without random collisions and keeps codes short — ID `1` becomes `1`, ID `3844` becomes `10`, ID `238,327` becomes `zzz`.

```python
BASE62 = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

def convert_to_shortcode(n: int) -> str:
    result = ""
    while n:
        result = BASE62[n % 62] + result
        n //= 62
    return result or "0"
```

The link is flushed to get its ID before the short code is generated, then committed in a single transaction.

### Async SQLAlchemy

All database operations use `AsyncSession` with `asyncpg` as the driver. This means the server never blocks on a database query — it can handle other requests while waiting for the DB to respond.

Alembic doesn't support async natively, so a separate `DATABASE_SYNC_URL` with `psycopg2` is used for migrations only.

### Click Tracking

Redirects are tracked two ways:
1. A new `Click` row is inserted (full history with timestamps)
2. `click_count` on `Link` is incremented via an atomic `UPDATE` statement

```python
await db.execute(
    update(Link)
    .where(Link.id == link.id)
    .values(click_count=Link.click_count + 1)
)
```

Using `UPDATE ... SET click_count = click_count + 1` is safer than read-modify-write — no race condition under concurrent traffic.

---

## Testing

The test suite uses `pytest-asyncio` with an async SQLite database (via `aiosqlite`) as a drop-in replacement for PostgreSQL. FastAPI's dependency injection system is used to swap the production session for a test session, meaning no real database is touched during tests.

### Running Tests

```bash
pip install pytest pytest-asyncio httpx aiosqlite
pytest tests/ -v
```

### Test Coverage

**`tests/test_links.py`**

| Test | What it verifies |
|------|-----------------|
| `test_create_link` | POST `/links/` returns 200 and a short link in the response |
| `test_load_link_success` | GET `/{shortcode}` returns 302 and correct `Location` header |
| `test_load_link_not_found` | GET `/unknown` returns 200 with the not-found template |
| `test_create_duplicate_link` | POSTing the same URL twice returns the same short link both times |

**`tests/test_admin.py`**

| Test | What it verifies |
|------|-----------------|
| `test_admin_all_links` | GET `/api/admin/links` returns a JSON object containing a `links` key |
| `test_get_analytics` | GET `/api/admin/links/{shortcode}/analytics/` returns click analytics |
| `test_delete_link` | DELETE `/api/admin/links/{id}` returns `{"message": "Link deleted"}` |

### How it Works

```
conftest.py
├── test_engine       → SQLite (aiosqlite) instead of PostgreSQL
├── db_setup          → creates all tables before tests, drops after (session-scoped)
└── client            → AsyncClient with two dependency overrides:
                        ├── get_session  → get_test_session (SQLite)
                        └── verify_header → bypass_header (no auth check)
```

The `client` fixture is function-scoped so each test gets a fresh database state. The `db_setup` fixture is session-scoped so tables are only created and dropped once per test run.

### Bugs Found by Tests

Writing the test suite surfaced four real production bugs:

1. **Missing import** — `update` was used in `load_link` but never imported from SQLAlchemy
2. **Type mismatch** — Pydantic's `HttpUrl` object was passed directly to the DB instead of being converted to a string with `str()`
3. **SQLite constraint difference** — `short_code` needed to be explicitly `nullable=True` in the model because SQLite enforces `NOT NULL` at flush time, while PostgreSQL defers it to commit
4. **Route conflict** — sqladmin mounts at the ASGI level and silently intercepted all `/admin/*` requests, making the admin JSON API unreachable; resolved by moving the API to `/api/admin`

---

## Security

- ✅ **Admin API** – Protected by `X-Admin-Key` header verified against an env variable
- ✅ **Admin dashboard** – Session-based login via sqladmin's `AuthenticationBackend`
- ✅ **Session security** – `SessionMiddleware` with a secret key signs session cookies
- ✅ **Proxy headers** – `ProxyHeadersMiddleware` ensures correct `https://` detection behind Railway's reverse proxy
- ✅ **SQL injection** – SQLAlchemy parameterized queries throughout
- ✅ **No sensitive data** – No user accounts, no PII stored

---

## What I Learned

### Two Database URLs Are Needed
SQLAlchemy's async engine uses `asyncpg` which Alembic can't use for migrations. The fix is a separate `DATABASE_SYNC_URL` using `psycopg2` passed to Alembic's `env.py`.

### Docker Networking
Inside docker-compose, services communicate via their service names. `localhost` becomes `db` — the name of the PostgreSQL service. This caught me off guard the first time.

### Proxy Headers Matter in Production
Behind Railway's reverse proxy, FastAPI saw all requests as `http://` even over HTTPS. Adding `ProxyHeadersMiddleware` with `trusted_hosts="*"` fixed this and also unblocked sqladmin's session cookies which require the correct protocol.

### Atomic Updates Prevent Race Conditions
Early implementation loaded the link, incremented `click_count`, then saved. Under concurrent requests this loses counts. `UPDATE ... SET click_count = click_count + 1` is atomic at the database level — no lost updates.

### ASGI Mounts Override FastAPI Routing
sqladmin mounts as a Starlette sub-application at `/admin`, which intercepts requests at the ASGI level before FastAPI's router ever sees them. No amount of route ordering fixes this — the solution is to use a non-conflicting prefix for any API routes under the same path.

### Dependency Injection Makes Testing Elegant
FastAPI's `dependency_overrides` allows swapping any dependency at test time without touching production code. The entire database layer was replaced with SQLite in a few lines of `conftest.py`, and the routes had no idea.

---

## Troubleshooting

### `relation "link" does not exist`
Migrations haven't run yet. Run:
```bash
alembic upgrade head
# or in Docker:
docker-compose run app alembic upgrade head
```

### `ConnectionRefusedError` in Docker
Your `DATABASE_URL` still points to `localhost`. Change the host to `db`:
```bash
DATABASE_URL=postgresql+asyncpg://user:password@db:5432/snip_db
```

### Admin panel is unstyled
sqladmin's static files are served at `/admin/statics/`. If your catch-all `/{shortcode}` route is intercepting them, make sure sqladmin is mounted before the router is included in `main.py`.

### Admin login redirects back to login page
`SessionMiddleware` is missing or `SECRET_KEY` is `None`. Verify the env variable is set and middleware is added before any routes.

### Admin API returns sqladmin HTML instead of JSON
Your admin API prefix conflicts with sqladmin's `/admin` mount. The API must use a different prefix — in this project it's `/api/admin`.

---

## License

Built by Richard Oyelowo for the love of development.