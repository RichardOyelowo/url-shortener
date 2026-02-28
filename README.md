<div align="center">

# <img src="images/logo.svg" width="500">

![License](https://img.shields.io/badge/license-MIT-blue.svg)
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
│   │   └── admin.py         # Admin API routes (X-Admin-Key protected)
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
| `GET` | `/admin/links` | List all links with click counts |
| `GET` | `/admin/links/{shortcode}/analytics` | Full click history for a link |
| `DELETE` | `/admin/links/{id}` | Delete a link and its clicks |

### Admin Dashboard

| Route | Description |
|-------|-------------|
| `/admin/` | sqladmin UI — browse and manage Link and Click records |

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
Your `/{shortcode}` route is intercepting sqladmin's static file requests. Make sure the `statics` path is guarded:
```python
if shortcode in ("admin", "statics"):
    return RedirectResponse(url=f"/{shortcode}/")
```

### Admin login redirects back to login page
`SessionMiddleware` is missing or `SECRET_KEY` is `None`. Verify the env variable is set and middleware is added before any routes.

---

## License

Built by Richard Oyelowo for the love of development.