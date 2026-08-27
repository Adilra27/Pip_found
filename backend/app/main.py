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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(causes.router, prefix="/api/causes", tags=["Causes"])
app.include_router(contact.router, prefix="/api/contact", tags=["Contact"])
app.include_router(donation.router, prefix="/api/donate", tags=["Donations"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(team.router, prefix="/api/team", tags=["Team"])
app.include_router(certificates.router, prefix="/api/certificates", tags=["Certificates"])
app.include_router(blog.router, prefix="/api/blog", tags=["Blog"])
app.include_router(about.router, prefix="/api/about", tags=["About"])
app.include_router(media.router, prefix="/api", tags=["Media"])


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