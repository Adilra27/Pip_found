import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import inspect, text

from .admin_panel import setup_admin
from .database import Base, engine
from .routes import (
    about,
    admin,
    blog,
    causes,
    certificates,
    contact,
    donation,
    media,
    team,
    volunteers,
)


# ============================================================
# DATABASE
# ============================================================

# Creates tables that do not already exist.
#
# IMPORTANT:
# create_all() does NOT modify an existing table.
# Therefore, the compatibility block below handles the
# team_members.team column if the table already existed
# before that column was introduced.
Base.metadata.create_all(bind=engine)


# ============================================================
# TEAM TABLE COMPATIBILITY
# ============================================================

# If an existing team_members table was created before the
# "team" column was introduced, add that column automatically.
#
# This is useful during the transition from the older SQLite
# schema to the current PostgreSQL schema.
with engine.begin() as connection:
    inspector = inspect(connection)

    existing_tables = inspector.get_table_names()

    if "team_members" in existing_tables:
        columns = {
            column["name"]
            for column in inspector.get_columns("team_members")
        }

        if "team" not in columns:
            connection.execute(
                text(
                    """
                    ALTER TABLE team_members
                    ADD COLUMN team VARCHAR(255)
                    """
                )
            )

    if "video_gallery" in existing_tables:
        columns = {
            column["name"]
            for column in inspector.get_columns("video_gallery")
        }

        if "category" not in columns:
            connection.execute(
                text(
                    """
                    ALTER TABLE video_gallery
                    ADD COLUMN category VARCHAR(100)
                    """
                )
            )


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Piplad Welfare Foundation API",
    description="Backend API for Piplad Welfare Foundation",
    version="1.0.0",
)


# ============================================================
# CORS
# ============================================================

CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# API ROUTES
# ============================================================

# Each router already defines its own prefix inside the
# respective route module.
#
# Therefore we intentionally do NOT provide another prefix
# here.

app.include_router(
    causes.router,
    tags=["Causes"],
)

app.include_router(
    contact.router,
    tags=["Contact"],
)

app.include_router(
    donation.router,
    tags=["Donations"],
)

app.include_router(
    admin.router,
    tags=["Admin"],
)

app.include_router(
    team.router,
    tags=["Team"],
)

app.include_router(
    certificates.router,
    tags=["Certificates"],
)

app.include_router(
    blog.router,
    tags=["Blog"],
)

app.include_router(
    about.router,
    tags=["About"],
)

app.include_router(
    media.router,
    tags=["Media"],
)

app.include_router(
    volunteers.router,
    tags=["Volunteers"],
)


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
def root():
    return {
        "message": "Piplad Welfare Foundation API",
        "status": "online",
        "organization": "Piplad Welfare Foundation",
        "tagline": "Creating Opportunities, Creating Lives",
        "docs_url": "/docs",
    }


# ============================================================
# ADMIN PANEL
# ============================================================

setup_admin(app)


# ============================================================
# MEDIA STORAGE
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

MEDIA_DIR = BASE_DIR / "media"

MEDIA_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

(MEDIA_DIR / "gallery").mkdir(
    parents=True,
    exist_ok=True,
)

(MEDIA_DIR / "videos").mkdir(
    parents=True,
    exist_ok=True,
)

(MEDIA_DIR / "projects").mkdir(
    parents=True,
    exist_ok=True,
)

# Team member uploads.
(MEDIA_DIR / "team").mkdir(
    parents=True,
    exist_ok=True,
)

# Certificate uploads.
(MEDIA_DIR / "certificates").mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# STATIC MEDIA
# ============================================================

# /media/... -> backend/media/...
#
# This mount must appear before the frontend catch-all mount.

app.mount(
    "/media",
    StaticFiles(
        directory=MEDIA_DIR,
    ),
    name="media",
)


# ============================================================
# REACT FRONTEND
# ============================================================

# Serve the React production build when it exists locally.
#
# The frontend mount must remain LAST because "/" is a
# catch-all route.

frontend_dist = (
    Path(__file__).resolve().parents[2]
    / "frontend"
    / "dist"
)

if frontend_dist.is_dir():
    app.mount(
        "/",
        StaticFiles(
            directory=frontend_dist,
            html=True,
        ),
        name="frontend",
    )