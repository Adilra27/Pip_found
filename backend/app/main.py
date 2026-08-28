import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

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
)

# Creates newly introduced tables without changing existing data.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Piplad Welfare Foundation API",
    description="Backend API for Piplad Welfare Foundation",
    version="1.0.0",
)

CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS or ["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(causes.router)
app.include_router(contact.router)
app.include_router(donation.router)
app.include_router(admin.router)
app.include_router(team.router)
app.include_router(certificates.router)
app.include_router(blog.router)
app.include_router(about.router)
app.include_router(media.router)


@app.get("/")
def root():
    return {
        "message": "Piplad Welfare Foundation API",
        "status": "online",
        "organization": "Piplad Welfare Foundation",
        "tagline": "Creating Opportunities, Creating Lives",
        "docs_url": "/docs",
    }


setup_admin(app)

BASE_DIR = Path(__file__).resolve().parent.parent
MEDIA_DIR = BASE_DIR / "media"

MEDIA_DIR.mkdir(parents=True, exist_ok=True)
(MEDIA_DIR / "gallery").mkdir(parents=True, exist_ok=True)
(MEDIA_DIR / "videos").mkdir(parents=True, exist_ok=True)
(MEDIA_DIR / "projects").mkdir(parents=True, exist_ok=True)

# Media must be mounted before the catch-all frontend mount.
app.mount(
    "/media",
    StaticFiles(directory=MEDIA_DIR),
    name="media",
)

# Serve the React build when it is available locally.
frontend_dist = Path(__file__).resolve().parents[2] / "frontend" / "dist"

if frontend_dist.is_dir():
    app.mount(
        "/",
        StaticFiles(directory=frontend_dist, html=True),
        name="frontend",
    )