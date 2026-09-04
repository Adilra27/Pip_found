# PWF Backend

FastAPI + SQLAlchemy 2.0 backend for the Piplad Welfare Foundation. Production
runs on Render with **PostgreSQL** (no SQLite).

## Prerequisites

- Python 3.12+
- PostgreSQL (Render managed instance, or a local Postgres for development)

## Setup

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Set the required environment variable(s). The app refuses to start without a
   database URL:

   ```bash
   # Linux/macOS
   export DATABASE_URL="postgresql+psycopg://USER:PASSWORD@HOST:PORT/DBNAME?sslmode=require"

   # Windows (PowerShell)
   $env:DATABASE_URL="postgresql+psycopg://USER:PASSWORD@HOST:PORT/DBNAME?sslmode=require"
   ```

   A local `backend/.env` file (gitignored) is loaded automatically if present.
   Copy `backend/.env.example` to `backend/.env` and fill it in.

3. Boot:

   ```bash
   uvicorn app.main:app --reload
   ```

   Tables are created automatically on startup. `/docs` gives you the Swagger UI.

### Environment variables

| Variable | Required | Purpose |
| --- | --- | --- |
| `DATABASE_URL` | Yes | PostgreSQL connection string (`postgresql+psycopg://...`) |
| `CORS_ORIGINS` | No | Comma-separated allowed browser origins (defaults to localhost dev ports) |
| `RAZORPAY_KEY_ID` / `RAZORPAY_KEY_SECRET` | No | Razorpay credentials; absent => mock orders for sandbox testing |
| `ADMIN_USER` / `ADMIN_PASSWORD` | No | Basic-auth credentials for `/api/admin` and SQL admin |

## Seeding

```bash
python seed_data.py
```

## Deploying the frontend to Render

The repository root contains `render.yaml` for the Vite static site. In Render,
create a Blueprint from this repository, or create a Static Site with:

- Root directory: `frontend`
- Build command: `npm ci && npm run build`
- Publish directory: `dist`
- Environment variable: `VITE_API_URL=https://piplad-api.onrender.com/api`

The blueprint also adds the SPA rewrite required by React Router. Set the
backend `CORS_ORIGINS` variable to the exact Render frontend URL after the site
is created. The example assumes `https://pip-found-frontend.onrender.com`.

## Migrating legacy SQLite data (one-time, already run in prod)

`backend/pwf_app.db` was the old SQLite database. To copy its rows into a fresh
Postgres database locally, run:

```bash
DATABASE_URL="postgresql+psycopg://USER:PASSWORD@HOST:PORT/DBNAME?sslmode=require" python migrate_sqlite_to_postgres.py
```

This recreates the schema, truncates the target tables, copies all rows while
preserving IDs, resets identity sequences, and verifies row counts. The SQLite
files (`pwf_app.db`) are no longer used by the app and are gitignored.