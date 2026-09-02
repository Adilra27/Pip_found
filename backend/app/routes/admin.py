import os
import secrets
import uuid

from datetime import date
from pathlib import Path
from typing import List, Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)

from fastapi.security import HTTPBasic, HTTPBasicCredentials

from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db

from ..models import (
    Cause,
    Certificate,
    ContactInquiry,
    Donation,
    GalleryItem,
    TeamMember,
    UpcomingProject,
    VideoGallery,
    VolunteerApplication,
)

from ..schemas import (
    CertificateResponse,
    GalleryItemResponse,
    TeamMemberResponse,
    UpcomingProjectResponse,
    VideoGalleryResponse,
    VolunteerApplicationResponse,
)


security = HTTPBasic()

router = APIRouter(
    prefix="/api/admin",
    tags=["Admin"],
)


# ============================================================
# MEDIA DIRECTORIES
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

MEDIA_DIR = BASE_DIR / "media"

GALLERY_DIR = MEDIA_DIR / "gallery"
VIDEO_DIR = MEDIA_DIR / "videos"
PROJECT_DIR = MEDIA_DIR / "projects"
TEAM_DIR = MEDIA_DIR / "team"
CERTIFICATE_DIR = MEDIA_DIR / "certificates"


# ============================================================
# UPLOAD RULES
# ============================================================

ALLOWED_IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".gif",
}

ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
}

ALLOWED_VIDEO_EXTENSIONS = {
    ".mp4",
    ".webm",
    ".mov",
    ".m4v",
}

ALLOWED_VIDEO_TYPES = {
    "video/mp4",
    "video/webm",
    "video/quicktime",
    "video/x-m4v",
}

MAX_IMAGE_SIZE = 10 * 1024 * 1024
MAX_VIDEO_SIZE = 100 * 1024 * 1024


# ============================================================
# GALLERY CATEGORIES
# ============================================================

DEFAULT_GALLERY_CATEGORIES = [
    "Photo Gallery",
    "Education",
    "Healthcare",
    "Environment",
    "Agriculture",
    "Sports",
    "Culture",
    "Social Welfare",
    "Finance & Legal",
    "General",
]


# ============================================================
# ADMIN AUTHENTICATION
# ============================================================

def get_current_admin(
    credentials: HTTPBasicCredentials = Depends(security),
):
    correct_username = secrets.compare_digest(
        credentials.username,
        os.getenv("ADMIN_USER", "admin"),
    )

    correct_password = secrets.compare_digest(
        credentials.password,
         os.getenv("ADMIN_PASSWORD", "admin"),
    )

    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={
                "WWW-Authenticate": "Basic",
            },
        )

    return credentials.username


# ============================================================
# FILE HELPERS
# ============================================================

def _safe_name(
    filename: str | None,
    default_extension: str,
) -> str:
    extension = Path(
        filename or ""
    ).suffix.lower()

    return (
        f"{uuid.uuid4().hex}"
        f"{extension or default_extension}"
    )


def _validate_upload(
    file: UploadFile,
    allowed_extensions,
    allowed_types,
    max_size: int,
):
    extension = Path(
        file.filename or ""
    ).suffix.lower()

    if extension not in allowed_extensions:
        raise HTTPException(
            400,
            f"Unsupported file type: "
            f"{extension or 'unknown'}",
        )

    if (
        file.content_type
        and file.content_type not in allowed_types
    ):
        raise HTTPException(
            400,
            f"Unsupported MIME type: "
            f"{file.content_type}",
        )

    return extension


def _save_upload(
    file: UploadFile,
    destination_dir: Path,
    filename: str,
    max_size: int,
) -> Path:
    destination_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    destination = destination_dir / filename

    total = 0

    try:
        with destination.open("wb") as output:

            while True:
                chunk = file.file.read(
                    1024 * 1024
                )

                if not chunk:
                    break

                total += len(chunk)

                if total > max_size:
                    raise HTTPException(
                        413,
                        "File is too large. "
                        f"Maximum allowed size is "
                        f"{max_size // (1024 * 1024)} MB.",
                    )

                output.write(chunk)

    except HTTPException:

        if destination.exists():
            destination.unlink(
                missing_ok=True
            )

        raise

    except Exception as exc:

        if destination.exists():
            destination.unlink(
                missing_ok=True
            )

        raise HTTPException(
            500,
            f"Could not save uploaded file: {exc}",
        ) from exc

    return destination


def _delete_local_file(
    url: str | None,
):
    if not url or not url.startswith("/media/"):
        return

    relative = url.removeprefix("/media/")

    candidate = (
        MEDIA_DIR / relative
    ).resolve()

    media_root = MEDIA_DIR.resolve()

    if (
        candidate == media_root
        or media_root not in candidate.parents
    ):
        return

    if (
        candidate.exists()
        and candidate.is_file()
    ):
        candidate.unlink(
            missing_ok=True
        )


def _public_url(
    folder: str,
    filename: str,
) -> str:
    return f"/media/{folder}/{filename}"


# ============================================================
# DASHBOARD STATS
# ============================================================

@router.get("/stats")
def get_admin_dashboard_stats(
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    total_donations = (
        db.query(
            func.sum(Donation.amount)
        )
        .filter(
            Donation.status == "completed"
        )
        .scalar()
        or 0.0
    )

    total_donors = (
        db.query(Donation)
        .filter(
            Donation.status == "completed"
        )
        .count()
    )

    active_causes = (
        db.query(Cause).count()
    )

    inquiries_count = (
        db.query(ContactInquiry).count()
    )

    return {
        "total_donations": total_donations,
        "total_donors": total_donors,
        "active_causes": active_causes,
        "inquiries_count": inquiries_count,
    }


# ============================================================
# PHOTO GALLERY ADMIN
# ============================================================

@router.get(
    "/gallery",
    response_model=List[GalleryItemResponse],
)
def get_gallery_items(
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    return (
        db.query(GalleryItem)
        .order_by(
            GalleryItem.created_at.desc(),
            GalleryItem.id.desc(),
        )
        .all()
    )


@router.post(
    "/gallery/upload",
    response_model=List[GalleryItemResponse],
)
def upload_gallery_image(
    title: str = Form(...),
    category: str = Form("Photo Gallery"),
    description: Optional[str] = Form(None),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    saved_paths = []
    items = []

    try:
        for file in files:
            _validate_upload(
                file,
                ALLOWED_IMAGE_EXTENSIONS,
                ALLOWED_IMAGE_TYPES,
                MAX_IMAGE_SIZE,
            )

            filename = _safe_name(
                file.filename,
                ".jpg",
            )

            saved_path = _save_upload(
                file,
                GALLERY_DIR,
                filename,
                MAX_IMAGE_SIZE,
            )

            saved_paths.append(saved_path)

            image_url = _public_url(
                "gallery",
                filename,
            )

            item = GalleryItem(
                title=title.strip(),
                image_url=image_url,
                category=(category or "").strip() or "Photo Gallery",
                description=(
                    (description or "").strip()
                    or None
                ),
            )

            db.add(item)
            items.append(item)

        db.commit()

        for item in items:
            db.refresh(item)

    except Exception as exc:
        db.rollback()

        for path in saved_paths:
            path.unlink(missing_ok=True)

        if isinstance(exc, HTTPException):
            raise

        raise HTTPException(
            500,
            f"Could not upload images: {exc}",
        ) from exc

    return items


@router.delete(
    "/gallery/{item_id}"
)
def delete_gallery_image(
    item_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    item = (
        db.query(GalleryItem)
        .filter(
            GalleryItem.id == item_id,
            GalleryItem.category
            == "Photo Gallery",
        )
        .first()
    )

    if not item:
        raise HTTPException(
            404,
            "Gallery image not found",
        )

    old_url = item.image_url

    db.delete(item)
    db.commit()

    _delete_local_file(old_url)

    return {
        "message": "Gallery image deleted"
    }


# ============================================================
# VIDEO GALLERY ADMIN
# ============================================================

@router.get(
    "/videos",
    response_model=List[VideoGalleryResponse],
)
def get_video_items(
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    return (
        db.query(VideoGallery)
        .order_by(
            VideoGallery.created_at.desc(),
            VideoGallery.id.desc(),
        )
        .all()
    )


@router.post(
    "/videos/upload",
    response_model=List[VideoGalleryResponse],
)
def upload_video(
    title: str = Form(...),
    category: str = Form("Video Gallery"),
    description: Optional[str] = Form(None),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    saved_paths = []
    items = []

    try:
        for file in files:
            _validate_upload(
                file,
                ALLOWED_VIDEO_EXTENSIONS,
                ALLOWED_VIDEO_TYPES,
                MAX_VIDEO_SIZE,
            )

            filename = _safe_name(
                file.filename,
                ".mp4",
            )

            saved_path = _save_upload(
                file,
                VIDEO_DIR,
                filename,
                MAX_VIDEO_SIZE,
            )

            saved_paths.append(saved_path)

            video_url = _public_url(
                "videos",
                filename,
            )

            item = VideoGallery(
                title=title.strip(),
                video_url=video_url,
                category=(category or "").strip() or "Video Gallery",
                description=(
                    (description or "").strip()
                    or None
                ),
            )

            db.add(item)
            items.append(item)

        db.commit()

        for item in items:
            db.refresh(item)

    except Exception as exc:
        db.rollback()

        for path in saved_paths:
            path.unlink(missing_ok=True)

        if isinstance(exc, HTTPException):
            raise

        raise HTTPException(
            500,
            f"Could not upload videos: {exc}",
        ) from exc

    return items


@router.delete(
    "/videos/{video_id}"
)
def delete_video(
    video_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    item = (
        db.query(VideoGallery)
        .filter(
            VideoGallery.id == video_id
        )
        .first()
    )

    if not item:
        raise HTTPException(
            404,
            "Video not found",
        )

    old_url = item.video_url

    db.delete(item)
    db.commit()

    _delete_local_file(old_url)

    return {
        "message": "Video deleted"
    }


# ============================================================
# GALLERY CATEGORIES
# ============================================================

def _merge_categories(
    defaults: List[str],
    used: List[str],
) -> List[str]:
    result = []
    seen = set()

    for value in defaults + used:
        normalized = (value or "").strip()

        if not normalized or normalized in seen:
            continue

        seen.add(normalized)
        result.append(normalized)

    return result


@router.get(
    "/gallery/categories"
)
def get_gallery_categories(
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    used = [
        row[0]
        for row in db.query(
            GalleryItem.category
        )
        .distinct()
        .all()
    ]

    return _merge_categories(
        DEFAULT_GALLERY_CATEGORIES,
        used,
    )


@router.get(
    "/videos/categories"
)
def get_video_categories(
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    used = [
        row[0]
        for row in db.query(
            VideoGallery.category
        )
        .distinct()
        .all()
    ]

    return _merge_categories(
        ["Video Gallery"]
        + DEFAULT_GALLERY_CATEGORIES,
        used,
    )


# ============================================================
# UPCOMING PROJECTS ADMIN
# ============================================================

@router.get(
    "/projects",
    response_model=List[UpcomingProjectResponse],
)
def get_projects(
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    return (
        db.query(UpcomingProject)
        .order_by(
            UpcomingProject.expected_date.asc(),
            UpcomingProject.id.desc(),
        )
        .all()
    )


@router.post(
    "/projects",
    response_model=UpcomingProjectResponse,
)
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
        _validate_upload(
            file,
            ALLOWED_IMAGE_EXTENSIONS,
            ALLOWED_IMAGE_TYPES,
            MAX_IMAGE_SIZE,
        )

        filename = _safe_name(
            file.filename,
            ".jpg",
        )

        _save_upload(
            file,
            PROJECT_DIR,
            filename,
            MAX_IMAGE_SIZE,
        )

        image_url = _public_url(
            "projects",
            filename,
        )

    project = UpcomingProject(
        title=title.strip(),
        description=(
            (description or "").strip()
            or None
        ),
        image_url=image_url,
        expected_date=expected_date,
        status="upcoming",
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    return project


@router.put(
    "/projects/{project_id}",
    response_model=UpcomingProjectResponse,
)
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
    project = (
        db.query(UpcomingProject)
        .filter(
            UpcomingProject.id
            == project_id
        )
        .first()
    )

    if not project:
        raise HTTPException(
            404,
            "Project not found",
        )

    old_image = project.image_url

    project.title = title.strip()

    project.description = (
        (description or "").strip()
        or None
    )

    project.expected_date = expected_date
    project.status = "upcoming"

    if file and file.filename:

        _validate_upload(
            file,
            ALLOWED_IMAGE_EXTENSIONS,
            ALLOWED_IMAGE_TYPES,
            MAX_IMAGE_SIZE,
        )

        filename = _safe_name(
            file.filename,
            ".jpg",
        )

        _save_upload(
            file,
            PROJECT_DIR,
            filename,
            MAX_IMAGE_SIZE,
        )

        project.image_url = _public_url(
            "projects",
            filename,
        )

    elif remove_image:
        project.image_url = None

    db.commit()
    db.refresh(project)

    if (
        old_image
        and old_image != project.image_url
    ):
        _delete_local_file(old_image)

    return project


@router.delete(
    "/projects/{project_id}"
)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    project = (
        db.query(UpcomingProject)
        .filter(
            UpcomingProject.id
            == project_id
        )
        .first()
    )

    if not project:
        raise HTTPException(
            404,
            "Project not found",
        )

    old_image = project.image_url

    db.delete(project)
    db.commit()

    _delete_local_file(old_image)

    return {
        "message": "Project deleted"
    }

# ============================================================
# TEAM MEMBERS ADMIN
# ============================================================

@router.get(
    "/team",
    response_model=List[TeamMemberResponse],
)
def get_team_members(
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    return (
        db.query(TeamMember)
        .order_by(
            TeamMember.team.asc(),
            TeamMember.created_at.asc(),
            TeamMember.id.asc(),
        )
        .all()
    )


@router.post(
    "/team",
    response_model=TeamMemberResponse,
)
def create_team_member(
    name: str = Form(...),
    role: Optional[str] = Form(None),
    team: str = Form("General"),
    bio: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    name = name.strip()
    team = team.strip() or "General"

    if not name:
        raise HTTPException(
            status_code=400,
            detail="Team member name is required",
        )

    photo_url = None

    # Photo is optional.
    if file and file.filename:
        _validate_upload(
            file,
            ALLOWED_IMAGE_EXTENSIONS,
            ALLOWED_IMAGE_TYPES,
            MAX_IMAGE_SIZE,
        )

        filename = _safe_name(
            file.filename,
            ".jpg",
        )

        _save_upload(
            file,
            TEAM_DIR,
            filename,
            MAX_IMAGE_SIZE,
        )

        photo_url = _public_url(
            "team",
            filename,
        )

    member = TeamMember(
        name=name,
        role=(
            (role or "").strip()
            or None
        ),
        team=team,
        photo_url=photo_url,
        bio=(
            (bio or "").strip()
            or None
        ),
    )

    db.add(member)
    db.commit()
    db.refresh(member)

    return member


@router.delete(
    "/team/{member_id}",
)
def delete_team_member(
    member_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    member = (
        db.query(TeamMember)
        .filter(
            TeamMember.id == member_id
        )
        .first()
    )

    if not member:
        raise HTTPException(
            status_code=404,
            detail="Team member not found",
        )

    old_photo = member.photo_url

    db.delete(member)
    db.commit()

    _delete_local_file(old_photo)

    return {
        "message": "Team member deleted"
    }


# ============================================================
# CERTIFICATES ADMIN
# ============================================================

@router.get(
    "/certificates",
    response_model=List[CertificateResponse],
)
def get_certificates(
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    return (
        db.query(Certificate)
        .order_by(
            Certificate.created_at.desc(),
            Certificate.id.desc(),
        )
        .all()
    )


@router.post(
    "/certificates",
    response_model=CertificateResponse,
)
def create_certificate(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    title = title.strip()

    if not title:
        raise HTTPException(
            status_code=400,
            detail="Certificate title is required",
        )

    image_url = None

    if file and file.filename:
        _validate_upload(
            file,
            ALLOWED_IMAGE_EXTENSIONS,
            ALLOWED_IMAGE_TYPES,
            MAX_IMAGE_SIZE,
        )

        filename = _safe_name(
            file.filename,
            ".jpg",
        )

        _save_upload(
            file,
            CERTIFICATE_DIR,
            filename,
            MAX_IMAGE_SIZE,
        )

        image_url = _public_url(
            "certificates",
            filename,
        )

    certificate = Certificate(
        title=title,
        image_url=image_url,
        description=(
            (description or "").strip()
            or None
        ),
    )

    db.add(certificate)
    db.commit()
    db.refresh(certificate)

    return certificate


@router.put(
    "/certificates/{certificate_id}",
    response_model=CertificateResponse,
)
def update_certificate(
    certificate_id: int,
    title: str = Form(...),
    description: Optional[str] = Form(None),
    remove_image: bool = Form(False),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    certificate = (
        db.query(Certificate)
        .filter(
            Certificate.id == certificate_id
        )
        .first()
    )

    if not certificate:
        raise HTTPException(
            404,
            "Certificate not found",
        )

    title = title.strip()

    if not title:
        raise HTTPException(
            status_code=400,
            detail="Certificate title is required",
        )

    old_image = certificate.image_url

    certificate.title = title

    certificate.description = (
        (description or "").strip()
        or None
    )

    if file and file.filename:
        _validate_upload(
            file,
            ALLOWED_IMAGE_EXTENSIONS,
            ALLOWED_IMAGE_TYPES,
            MAX_IMAGE_SIZE,
        )

        filename = _safe_name(
            file.filename,
            ".jpg",
        )

        _save_upload(
            file,
            CERTIFICATE_DIR,
            filename,
            MAX_IMAGE_SIZE,
        )

        certificate.image_url = _public_url(
            "certificates",
            filename,
        )

    elif remove_image:
        certificate.image_url = None

    db.commit()
    db.refresh(certificate)

    if (
        old_image
        and old_image != certificate.image_url
    ):
        _delete_local_file(old_image)

    return certificate


@router.delete(
    "/certificates/{certificate_id}",
)
def delete_certificate(
    certificate_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    certificate = (
        db.query(Certificate)
        .filter(
            Certificate.id == certificate_id
        )
        .first()
    )

    if not certificate:
        raise HTTPException(
            404,
            "Certificate not found",
        )

    old_image = certificate.image_url

    db.delete(certificate)
    db.commit()

    _delete_local_file(old_image)

    return {
        "message": "Certificate deleted"
    }
