import os
import secrets
import uuid
from datetime import date
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import (
    Cause,
    ContactInquiry,
    Donation,
    GalleryItem,
    UpcomingProject,
    VideoGallery,
    VolunteerApplication,
)
from ..schemas import (
    GalleryItemResponse,
    UpcomingProjectResponse,
    VideoGalleryResponse,
    VolunteerApplicationResponse,
)

security = HTTPBasic()
router = APIRouter(prefix="/api/admin", tags=["Admin"])

BASE_DIR = Path(__file__).resolve().parents[2]
MEDIA_DIR = BASE_DIR / "media"
GALLERY_DIR = MEDIA_DIR / "gallery"
VIDEO_DIR = MEDIA_DIR / "videos"
PROJECT_DIR = MEDIA_DIR / "projects"

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".webm", ".mov", ".m4v"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/webm", "video/quicktime", "video/x-m4v"}
MAX_IMAGE_SIZE = 10 * 1024 * 1024
MAX_VIDEO_SIZE = 100 * 1024 * 1024


def get_current_admin(credentials: HTTPBasicCredentials = Depends(security)):
    # Keep these credentials aligned with the existing admin authentication.
    correct_username = secrets.compare_digest(credentials.username, "admin")
    correct_password = secrets.compare_digest(credentials.password, "admin")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


def _safe_name(filename: str | None, default_extension: str) -> str:
    extension = Path(filename or "").suffix.lower()
    return f"{uuid.uuid4().hex}{extension or default_extension}"


def _validate_upload(file: UploadFile, allowed_extensions, allowed_types, max_size: int):
    extension = Path(file.filename or "").suffix.lower()
    if extension not in allowed_extensions:
        raise HTTPException(400, f"Unsupported file type: {extension or 'unknown'}")

    if file.content_type and file.content_type not in allowed_types:
        raise HTTPException(400, f"Unsupported MIME type: {file.content_type}")

    return extension


def _save_upload(file: UploadFile, destination_dir: Path, filename: str, max_size: int) -> Path:
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / filename
    total = 0

    try:
        with destination.open("wb") as output:
            while True:
                chunk = file.file.read(1024 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                if total > max_size:
                    raise HTTPException(413, f"File is too large. Maximum allowed size is {max_size // (1024 * 1024)} MB.")
                output.write(chunk)
    except HTTPException:
        if destination.exists():
            destination.unlink(missing_ok=True)
        raise
    except Exception as exc:
        if destination.exists():
            destination.unlink(missing_ok=True)
        raise HTTPException(500, f"Could not save uploaded file: {exc}") from exc

    return destination


def _delete_local_file(url: str | None):
    if not url or not url.startswith("/media/"):
        return
    relative = url.removeprefix("/media/")
    candidate = (MEDIA_DIR / relative).resolve()
    media_root = MEDIA_DIR.resolve()
    if candidate == media_root or media_root not in candidate.parents:
        return
    if candidate.exists() and candidate.is_file():
        candidate.unlink(missing_ok=True)


def _public_url(folder: str, filename: str) -> str:
    return f"/media/{folder}/{filename}"


@router.get("/stats")
def get_admin_dashboard_stats(db: Session = Depends(get_db), _: str = Depends(get_current_admin)):
    total_donations = db.query(func.sum(Donation.amount)).filter(Donation.status == "completed").scalar() or 0.0
    total_donors = db.query(Donation).filter(Donation.status == "completed").count()
    active_causes = db.query(Cause).count()
    inquiries_count = db.query(ContactInquiry).count()
    volunteer_applications_count = db.query(VolunteerApplication).filter(VolunteerApplication.status == "pending").count()
    return {
        "total_donations": total_donations,
        "total_donors": total_donors,
        "active_causes": active_causes,
        "inquiries_count": inquiries_count,
        "volunteer_applications_count": volunteer_applications_count,
    }


# ---------------------------------------------------------------------------
# VOLUNTEER APPLICATIONS ADMIN
# ---------------------------------------------------------------------------

@router.get("/volunteers", response_model=List[VolunteerApplicationResponse])
def get_volunteer_applications(db: Session = Depends(get_db), _: str = Depends(get_current_admin)):
    return db.query(VolunteerApplication).order_by(VolunteerApplication.created_at.desc(), VolunteerApplication.id.desc()).all()


@router.patch("/volunteers/{application_id}/status", response_model=VolunteerApplicationResponse)
def update_volunteer_status(
    application_id: int,
    status_value: str,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    if status_value not in {"pending", "accepted", "rejected"}:
        raise HTTPException(400, "Status must be pending, accepted, or rejected")
    application = db.query(VolunteerApplication).filter(VolunteerApplication.id == application_id).first()
    if not application:
        raise HTTPException(404, "Volunteer application not found")
    application.status = status_value
    db.commit()
    db.refresh(application)
    return application


@router.delete("/volunteers/{application_id}", status_code=204)
def delete_volunteer_application(
    application_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    application = db.query(VolunteerApplication).filter(VolunteerApplication.id == application_id).first()
    if not application:
        raise HTTPException(404, "Volunteer application not found")
    db.delete(application)
    db.commit()


# ---------------------------------------------------------------------------
# PHOTO GALLERY ADMIN
# ---------------------------------------------------------------------------

@router.get("/gallery", response_model=List[GalleryItemResponse])
def get_gallery_items(db: Session = Depends(get_db), _: str = Depends(get_current_admin)):
    return (
        db.query(GalleryItem)
        .filter(GalleryItem.category == "Photo Gallery")
        .order_by(GalleryItem.created_at.desc(), GalleryItem.id.desc())
        .all()
    )


@router.post("/gallery/upload", response_model=GalleryItemResponse)
def upload_gallery_image(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    _validate_upload(file, ALLOWED_IMAGE_EXTENSIONS, ALLOWED_IMAGE_TYPES, MAX_IMAGE_SIZE)
    filename = _safe_name(file.filename, ".jpg")
    _save_upload(file, GALLERY_DIR, filename, MAX_IMAGE_SIZE)
    image_url = _public_url("gallery", filename)

    item = GalleryItem(
        title=title.strip(),
        image_url=image_url,
        category="Photo Gallery",
        description=(description or "").strip() or None,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/gallery/{item_id}")
def delete_gallery_image(
    item_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    item = (
        db.query(GalleryItem)
        .filter(GalleryItem.id == item_id, GalleryItem.category == "Photo Gallery")
        .first()
    )
    if not item:
        raise HTTPException(404, "Gallery image not found")

    old_url = item.image_url
    db.delete(item)
    db.commit()
    _delete_local_file(old_url)
    return {"message": "Gallery image deleted"}


# ---------------------------------------------------------------------------
# VIDEO GALLERY ADMIN
# ---------------------------------------------------------------------------

@router.get("/videos", response_model=List[VideoGalleryResponse])
def get_video_items(db: Session = Depends(get_db), _: str = Depends(get_current_admin)):
    return db.query(VideoGallery).order_by(VideoGallery.created_at.desc(), VideoGallery.id.desc()).all()


@router.post("/videos/upload", response_model=VideoGalleryResponse)
def upload_video(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    _validate_upload(file, ALLOWED_VIDEO_EXTENSIONS, ALLOWED_VIDEO_TYPES, MAX_VIDEO_SIZE)
    filename = _safe_name(file.filename, ".mp4")
    _save_upload(file, VIDEO_DIR, filename, MAX_VIDEO_SIZE)
    video_url = _public_url("videos", filename)

    item = VideoGallery(
        title=title.strip(),
        video_url=video_url,
        description=(description or "").strip() or None,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/videos/{video_id}")
def delete_video(
    video_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    item = db.query(VideoGallery).filter(VideoGallery.id == video_id).first()
    if not item:
        raise HTTPException(404, "Video not found")

    old_url = item.video_url
    db.delete(item)
    db.commit()
    _delete_local_file(old_url)
    return {"message": "Video deleted"}


# ---------------------------------------------------------------------------
# UPCOMING PROJECTS ADMIN
# ---------------------------------------------------------------------------

@router.get("/projects", response_model=List[UpcomingProjectResponse])
def get_projects(db: Session = Depends(get_db), _: str = Depends(get_current_admin)):
    return db.query(UpcomingProject).order_by(UpcomingProject.expected_date.asc(), UpcomingProject.id.desc()).all()


@router.post("/projects", response_model=UpcomingProjectResponse)
def create_project(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    expected_date: Optional[date] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    image_url = None
    if file and file.filename:
        _validate_upload(file, ALLOWED_IMAGE_EXTENSIONS, ALLOWED_IMAGE_TYPES, MAX_IMAGE_SIZE)
        filename = _safe_name(file.filename, ".jpg")
        _save_upload(file, PROJECT_DIR, filename, MAX_IMAGE_SIZE)
        image_url = _public_url("projects", filename)

    project = UpcomingProject(
        title=title.strip(),
        description=(description or "").strip() or None,
        image_url=image_url,
        expected_date=expected_date,
        status="upcoming",
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.put("/projects/{project_id}", response_model=UpcomingProjectResponse)
def update_project(
    project_id: int,
    title: str = Form(...),
    description: Optional[str] = Form(None),
    expected_date: Optional[date] = Form(None),
    remove_image: bool = Form(False),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    project = db.query(UpcomingProject).filter(UpcomingProject.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")

    old_image = project.image_url
    project.title = title.strip()
    project.description = (description or "").strip() or None
    project.expected_date = expected_date
    project.status = "upcoming"

    if file and file.filename:
        _validate_upload(file, ALLOWED_IMAGE_EXTENSIONS, ALLOWED_IMAGE_TYPES, MAX_IMAGE_SIZE)
        filename = _safe_name(file.filename, ".jpg")
        _save_upload(file, PROJECT_DIR, filename, MAX_IMAGE_SIZE)
        project.image_url = _public_url("projects", filename)
    elif remove_image:
        project.image_url = None

    db.commit()
    db.refresh(project)

    if old_image and old_image != project.image_url:
        _delete_local_file(old_image)

    return project


@router.delete("/projects/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    project = db.query(UpcomingProject).filter(UpcomingProject.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")

    old_image = project.image_url
    db.delete(project)
    db.commit()
    _delete_local_file(old_image)
    return {"message": "Project deleted"}
