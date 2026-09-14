"""Shared service for rendering the official certificate / ID-card documents.

Used by both the admin generation API and the volunteer accept flow, so
certificate issuance and volunteer-card issuance behave identically no
matter which entry point triggered them.
"""

import logging
import mimetypes
import os
import secrets
from datetime import datetime
from pathlib import Path

from . import models
from .certificate_render import build_certificate_image
from .document_layouts import (
    CERTIFICATE_LABELS,
    CERTIFICATE_IMAGES,
    VOLUNTEER_CARD_IMAGE,
    layout_for,
)
from .qrcode_util import build_qr_png, verify_url

logger = logging.getLogger(__name__)

MEDIA_DIR = Path(__file__).resolve().parents[1] / "media"
GENERATED_BASE = MEDIA_DIR / "generated"
CERT_GENERATED_DIR = GENERATED_BASE / "certificates"
VOLUNTEER_GENERATED_DIR = GENERATED_BASE / "volunteers"

DATE_FMT = "%d %B %Y"


def ensure_generated_dirs() -> None:
    CERT_GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    VOLUNTEER_GENERATED_DIR.mkdir(parents=True, exist_ok=True)


def _absolute_template_path(media_path: str) -> str:
    """Resolve a media-relative template path (e.g. ``certificate_templates/...``)
    to an absolute filesystem path for the renderer."""
    clean = media_path.lstrip("/").removeprefix("media/")
    return str(MEDIA_DIR / clean)


def next_certificate_number(db) -> str:
    """Return the next unique certificate number, e.g. CERT-2026-000001."""
    from sqlalchemy import or_

    year = datetime.utcnow().year
    prefix = f"CERT-{year}-"
    existing = (
        db.query(models.IssuedCertificate.certificate_number)
        .filter(
            models.IssuedCertificate.certificate_number.isnot(None),
            models.IssuedCertificate.certificate_number.startswith(prefix),
        )
        .all()
    )
    used = {row[0] for row in existing if row[0] is not None}
    sequence = 1
    while True:
        candidate = f"{prefix}{sequence:06d}"
        if candidate not in used:
            return candidate
        sequence += 1
    # unreachable


def generate_qr_token() -> str:
    """Unguessable URL-safe token embedded in the QR payload."""
    return "piplad-" + secrets.token_urlsafe(18)


def _display_date(value):
    if value in (None, ""):
        return ""
    if isinstance(value, str):
        return value
    return value.strftime(DATE_FMT)


def load_photo_bytes(profile_pic_url):
    """Return raw image bytes for a volunteer photo URL/path or None.

    No size cap (unlike the e-mail helper) so large Cloudinary photos still
    get baked into the stored official card.
    """
    if not profile_pic_url:
        return None
    try:
        import requests

        candidate = None
        if profile_pic_url.startswith(("/media/", "media/", "./", ".")):
            relative = profile_pic_url.removeprefix("/media/")
            candidate = MEDIA_DIR / relative
            if candidate.is_file():
                return candidate.read_bytes()
            logger.warning("Volunteer photo not found on disk: %s", profile_pic_url)
            return None
        response = requests.get(
            profile_pic_url,
            timeout=(3.05, 8),
            headers={"User-Agent": "Piplad-Documents/1.0", "Accept": "image/*"},
        )
        response.raise_for_status()
        return response.content or None
    except Exception as exc:  # noqa: BLE001 - photo must never block issuance
        logger.warning("Could not load volunteer photo for card: %s", exc)
        return None


# ============================================================
# Certificates
# ============================================================

CERT_FIELD_MAP = {
    "appreciation": ("program_name", "issue_date"),
    "internship": ("program_name", "starting_date", "end_date", "issue_date"),
    "completion": (
        "program_name",
        "organisation_name",
        "competition_date",
        "competition_location",
        "issue_date",
    ),
    "participation": (
        "competition_date",
        "competition_location",
        "program_name",
        "issue_date",
    ),
}


def _certificate_fields(document_type: str, cert) -> dict:
    fields = {}
    for key in CERT_FIELD_MAP.get(document_type, ()):
        value = getattr(cert, key, None)
        if value is None:
            continue
        if key.endswith("_date") or key == "issue_date":
            fields[key] = _display_date(value)
        else:
            fields[key] = str(value).strip()
    return fields


def render_certificate_jpeg(cert) -> bytes:
    """Render the official certificate JPEG bytes for an IssuedCertificate."""
    document_type = cert.certificate_type
    if document_type not in CERTIFICATE_IMAGES:
        raise ValueError(f"Unsupported certificate type: {document_type}")

    layout = layout_for(document_type)
    fields = _certificate_fields(document_type, cert)
    name = " ".join(
        part for part in (cert.first_name, cert.last_name) if part
    ) or cert.recipient_name
    fields["name"] = name

    if cert.certificate_number:
        fields["certificate_number"] = cert.certificate_number

    qr_data = None
    if cert.qr_verification_token:
        qr_data = verify_url("certificate", cert.qr_verification_token)

    template_path = _absolute_template_path(CERTIFICATE_IMAGES[document_type])
    return build_certificate_image(
        image_url=template_path,
        layout=layout,
        fields=fields,
        qr_data=qr_data,
    )


def save_rendered_certificate(cert) -> str:
    """Write the rendered certificate JPEG to disk and return the media path."""
    ensure_generated_dirs()
    filename = f"{cert.certificate_number or cert.id}.jpg"
    path = CERT_GENERATED_DIR / filename
    path.write_bytes(render_certificate_jpeg(cert))
    relative = f"/media/generated/certificates/{filename}"
    cert.generated_file_path = relative
    return relative


def build_issued_certificate(
    db,
    *,
    certificate_type: str,
    first_name: str,
    last_name: str | None = None,
    recipient_email: str | None = None,
    program_name: str | None = None,
    starting_date=None,
    end_date=None,
    organisation_name: str | None = None,
    competition_date=None,
    competition_location: str | None = None,
    issue_date=None,
    certificate_number: str | None = None,
    status: str = "issued",
    qr_verification_token: str | None = None,
) -> models.IssuedCertificate:
    """Create, render and persist an official certificate."""
    ensure_generated_dirs()

    if certificate_type not in CERTIFICATE_IMAGES:
        raise ValueError(f"Unsupported certificate type: {certificate_type}")

    if end_date and starting_date and end_date < starting_date:
        raise ValueError("Internship end date cannot be before the starting date.")

    cert = models.IssuedCertificate(
        certificate_type=certificate_type,
        certificate_number=certificate_number or "",
        first_name=first_name,
        last_name=last_name,
        recipient_name=" ".join(
            part for part in (first_name, last_name) if part
        ),
        recipient_email=recipient_email,
        program_name=program_name,
        starting_date=starting_date,
        end_date=end_date,
        organisation_name=organisation_name,
        competition_date=competition_date,
        competition_location=competition_location,
        issue_date=issue_date or datetime.utcnow().date(),
        type_label=CERTIFICATE_LABELS.get(certificate_type),
        status=status,
        qr_verification_token=qr_verification_token or generate_qr_token(),
    )

    if not cert.certificate_number:
        cert.certificate_number = next_certificate_number(db)

    # Make sure the number will pass the unique index cleanly.
    conflicts = (
        db.query(models.IssuedCertificate.id)
        .filter(models.IssuedCertificate.certificate_number == cert.certificate_number)
        .first()
    )
    while conflicts:
        cert.certificate_number = next_certificate_number(db)
        conflicts = (
            db.query(models.IssuedCertificate.id)
            .filter(models.IssuedCertificate.certificate_number == cert.certificate_number)
            .first()
        )

    db.add(cert)
    db.flush()
    cert.rendered_url = save_rendered_certificate(cert)
    db.commit()
    db.refresh(cert)
    return cert


def certificate_download_name(cert) -> str:
    slug = (cert.certificate_type or "certificate").replace("_", "-")
    return f"{slug}-{cert.certificate_number}.jpg"


# ============================================================
# Volunteer ID cards
# ============================================================

def render_volunteer_card_jpeg(app) -> bytes:
    """Render the official volunteer ID card JPEG bytes."""
    layout = layout_for("volunteer")

    photo_bytes = load_photo_bytes(app.profile_pic_url)
    overlay_pngs = []
    if photo_bytes:
        overlay_pngs.append((photo_bytes, layout.get("photo")))

    fields = {
        "name": (app.full_name or "").strip(),
        "position": (app.position or "").strip(),
        "volunteer_id": app.volunteer_id or "",
        "programme": app.interest_area or "",
        "location": app.location or "",
        "valid_till": _display_date(app.valid_till),
    }

    qr_data = None
    if app.card_qr_token:
        qr_data = verify_url("volunteer", app.card_qr_token)

    template_path = _absolute_template_path(VOLUNTEER_CARD_IMAGE)
    return build_certificate_image(
        image_url=template_path,
        layout=layout,
        fields=fields,
        qr_data=qr_data,
        overlay_pngs=overlay_pngs,
    )


def save_rendered_volunteer_card(app) -> str:
    """Render, save and return the media path of a volunteer ID card."""
    ensure_generated_dirs()
    filename = f"{app.volunteer_id or app.id}.jpg"
    path = VOLUNTEER_GENERATED_DIR / filename
    path.write_bytes(render_volunteer_card_jpeg(app))
    relative = f"/media/generated/volunteers/{filename}"
    app.card_file_path = relative
    return relative


def build_volunteer_card(
    db,
    app,
    *,
    issue_date=None,
    valid_till=None,
    location: str | None = None,
    position: str | None = None,
    status: str = "issued",
    qr_verification_token: str | None = None,
) -> models.VolunteerApplication:
    """Set card fields, render the official ID card and persist it."""
    from datetime import timedelta

    from sqlalchemy.orm.attributes import flag_modified

    ensure_generated_dirs()
    app.issue_date = issue_date or datetime.utcnow().date()
    app.valid_till = valid_till or (app.issue_date + timedelta(days=365 * 2))
    if location is not None:
        app.location = location
    if position is not None:
        app.position = position or None
    app.status = status
    app.card_qr_token = app.card_qr_token or qr_verification_token or generate_qr_token()

    save_rendered_volunteer_card(app)
    flag_modified(app, "card_file_path")
    db.commit()
    db.refresh(app)
    return app


def volunteer_card_download_name(app) -> str:
    return f"volunteer-id-card-{app.volunteer_id or app.id}.jpg"