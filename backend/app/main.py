from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from .database import engine, Base
from .routes import causes, contact, donation, admin, team, certificates, blog, about, media

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Piplad Welfare Foundation API",
    description="Python FastAPI backend powering Piplad Welfare Foundation web application",
    version="1.0.0"
)

# Enable CORS for React JS frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
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
        "status": "online",
        "organization": "Piplad Welfare Foundation",
        "tagline": "Creating Opportunities, Creating Lives",
        "docs_url": "/docs"
    }

from .admin_panel import setup_admin
setup_admin(app)

# Serve the React build when it is available locally.
frontend_dist = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if frontend_dist.is_dir():
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
