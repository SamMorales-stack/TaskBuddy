# Deploy TaskBuddy — Design Spec

**Date:** 2026-05-16
**Status:** Approved

## Goal

Deploy TaskBuddy to Streamlit Cloud with persistent task data backed by Neon PostgreSQL.

## Architecture

```
Browser → Streamlit Cloud (app.py) → Neon PostgreSQL (tasks, projects)
```

- **Streamlit Cloud** hosts and serves the app. Connected directly to the `main` branch of `https://github.com/SamMorales-stack/TaskBuddy`. Every push to `main` triggers an automatic redeploy.
- **Neon** provides free serverless PostgreSQL. The app connects via `DATABASE_URL` environment variable, already read in `taskbuddy/db.py:9`.
- Tables are created automatically on first app load via `init_db()` (`taskbuddy/db.py:35`).

## Code Change

**`requirements.txt`** — add `psycopg2-binary` (PostgreSQL driver for SQLAlchemy).

No other code changes are required. `db.py` already switches between SQLite and PostgreSQL based on `DATABASE_URL`.

## One-Time Setup Steps

1. **Neon** — create a free account at neon.tech, create a project, copy the connection string (format: `postgresql://user:pass@host/dbname`)
2. **Streamlit Cloud** — go to share.streamlit.io → New app → repo: `SamMorales-stack/TaskBuddy` → main branch → entry point: `app.py`
3. **Secrets** — in Streamlit Cloud app settings → Secrets, add:
   ```toml
   DATABASE_URL = "postgresql+psycopg2://user:pass@host/dbname"
   ```
   Note the `+psycopg2` dialect prefix required by SQLAlchemy.
4. **Deploy** — Streamlit Cloud installs deps from `requirements.txt`, starts the app, `init_db()` creates all tables on first request.

## Data Persistence

Without `DATABASE_URL`, the app falls back to `sqlite:///taskbuddy.db` (local dev only). On Streamlit Cloud with `DATABASE_URL` set, all task and project data persists permanently in Neon across restarts and redeployments.

## Out of Scope

- Custom domain
- Authentication / access control
- Data migration from local SQLite to Neon
