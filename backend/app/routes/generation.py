"""Admin API for generating and managing official Piplad documents.

Certificates (4 official templates) and the official Volunteer ID card are
rendered dynamically, stored under media/generated, and exposed for
download (JPEG or PDF). Each document carries a unique QR pointing at the
public verification page.
"""

from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy import or_
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..document_layouts import (
    CERTIFICATE_LABELS,
    CERTIFICATE_TEMPLATE_SLUGS,
    CERTIFICATE_TYPES,
    CERTIFICATE_IMAGES,
)
from ..document_pdf import document_pdf_bytes
from ..document_service import (
    CERT_GENERATED_DIR,
    VOLUNTEER_GENERATED_DIR,
    MEDIA_DIR,
    build_issued_certificate,
    build_volunteer_card,
    certificate_download_name,
    volunteer_card_download_name,
)
from ..qrcode_util import verify_url
from .admin import get_current_admin

router = APIRouter(prefix="/api/admin/generated", tags=["Admin Generated Documents"])


def _cert_to_response(cert) -> schemas.GeneratedCertificateResponse:
    qr_token = cert.certificate_number or cert.qr_verification_token or ""
    return schemas.GeneratedCertificateResponse(
        id=cert.id,
        certificate_number=cert.certificate_number,
        certificate_type=cert.certificate_type,
        recipient_name=cert.recipient_name,
        recipient_email=cert.recipient_email,
        program_name=cert.program_name,
        starting_date=cert.starting_date,
        end_date=cert.end_date,
        organisation_name=cert.organisation_name,
        competition_date=cert.competition_date,
        competition_location=cert.competition_location,
        issue_date=cert.issue_date,
        rendered_url=cert.rendered_url,
        generated_file_path=cert.generated_file_path,
        verified_url=verify_url("certificate", qr_token),
        status=cert.status,
        sent_at=cert.sent_at,
        created_at=cert.created_at,
        revoked=bool(cert.revoked_at),
    )


def _volunteer_to_response(app) -> schemas.GeneratedVolunteerCardResponse:
    qr_token = app.card_qr_token or app.volunteer_id or ""
    return schemas.GeneratedVolunteerCardResponse(
        id=app.id,
        volunteer_id=app.volunteer_id,
        full_name=app.full_name,
        email=app.email,
        profile_pic_url=app.profile_pic_url,
        status=app.status,
        location=app.location,
        issue_date=app.issue_date,
        valid_till=app.valid_till,
        card_file_path=app.card_file_path,
        verified_url=verify_url("volunteer", qr_token),
        card_revoked_at=app.card_revoked_at,
        card_sent_at=app.card_sent_at,
        created_at=app.created_at,
    )


# ============================================================
# Options
# ============================================================

@router.get("/options")
def generation_options(db: Session = Depends(get_db), _=Depends(get_current_admin)):
    templates = {
        doc_type: (
            MEDIA_DIR / "certificate_templates" / Path(image).name
        ).is_file()
        for doc_type, image in CERTIFICATE_IMAGES.items()
    }
    volunteer_image = (
        MEDIA_DIR / "certificate_templates" / "volunteer card.png"
    )
    return {
        "certificate_types": [
            {
                "type": doc_type,
                "label": CERTIFICATE_LABELS[doc_type],
                "image_available": templates[doc_type],
            }
            for doc_type in CERTIFICATE_TYPES
        ],
        "volunteer_card_image_available": volunteer_image.is_file(),
        "template_slugs": CERTIFICATE_TEMPLATE_SLUGS,
    }


# ============================================================
# Certificates
# ============================================================

@router.post("/certificates", response_model=schemas.GeneratedCertificateResponse)
def generate_certificate(
    payload: schemas.CertificateGenerateRequest,
    db: Session = Depends(get_db),
    _=Depends(get_current_admin),
):
    if payload.certificate_type not in CERTIFICATE_IMAGES:
        raise HTTPException(status_code=400, detail="Unsupported certificate type.")
    if payload.end_date and payload.starting_date and payload.end_date < payload.starting_date:
        raise HTTPException(
            status_code=400,
            detail="Internship end date cannot be before the starting date.",
        )
    if payload.certificate_number:
        existing = (
            db.query(models.IssuedCertificate.id)
            .filter(models.IssuedCertificate.certificate_number == payload.certificate_number)
            .first()
        )
        if existing:
            raise HTTPException(status_code=409, detail="Certificate number already exists.")
    try:
        cert = build_issued_certificate(
            db,
            certificate_type=payload.certificate_type,
            first_name=payload.first_name,
            last_name=payload.last_name,
            recipient_email=payload.recipient_email,
            program_name=payload.program_name,
            starting_date=payload.starting_date,
            end_date=payload.end_date,
            organisation_name=payload.organisation_name,
            competition_date=payload.competition_date,
            competition_location=payload.competition_location,
            issue_date=payload.issue_date,
            certificate_number=payload.certificate_number,
            status=payload.status or "issued",
            qr_verification_token=payload.qr_verification_token,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _cert_to_response(cert)


@router.get("/certificates", response_model=schemas.IssuedCertificateListResponse)
def list_certificates(
    type_label: str | None = None,
    search: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _=Depends(get_current_admin),
):
    query = db.query(models.IssuedCertificate)
    if type_label:
        query = query.filter(
            or_(
                models.IssuedCertificate.certificate_type == type_label,
                models.IssuedCertificate.type_label == type_label,
            )
        )
    if search:
        like = f"%{search}%"
        query = query.filter(
            or_(
                models.IssuedCertificate.recipient_name.ilike(like),
                models.IssuedCertificate.certificate_number.ilike(like),
                models.IssuedCertificate.recipient_email.ilike(like),
            )
        )
    total = query.count()
    items = (
        query.order_by(models.IssuedCertificate.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return schemas.IssuedCertificateListResponse(
        items=[_cert_to_response(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/certificates/download", response_class=FileResponse)
def download_certificates(
    certificate_ids: list[int],
    format: str = "jpg",
    db: Session = Depends(get_db),
    _=Depends(get_current_admin),
):
    """Return the JPEG or a combined A4 PDF for the given certificate IDs."""
    if format not in ("jpg", "pdf"):
        raise HTTPException(status_code=400, detail="format must be 'jpg' or 'pdf'.")
    certs = (
        db.query(models.IssuedCertificate)
        .filter(models.IssuedCertificate.id.in_(certificate_ids))
        .all()
    )
    if not certs:
        raise HTTPException(status_code=404, detail="No certificates found.")
    if format == "jpg":
        if len(certs) > 1:
            raise HTTPException(status_code=400, detail="Choose a single certificate for JPG download.")
        cert = certs[0]
        path = CERT_GENERATED_DIR / f"{cert.certificate_number or cert.id}.jpg"
        if not path.is_file():
            cert.rendered_url = None
            from ..document_service import save_rendered_certificate

            save_rendered_certificate(cert)
            db.commit()
        return FileResponse(path, media_type="image/jpeg", filename=certificate_download_name(cert))

    from io import BytesIO

    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfgen import canvas as pdf_canvas

    from fastapi.responses import Response

    buf = BytesIO()
    c = pdf_canvas.Canvas(buf, pagesize=landscape(A4))
    c.setTitle("Piplad Certificates")
    for cert in certs:
        path = CERT_GENERATED_DIR / f"{cert.certificate_number or cert.id}.jpg"
        if not path.is_file():
            cert.rendered_url = None
            from ..document_service import save_rendered_certificate

            save_rendered_certificate(cert)
            db.commit()
        image = ImageReader(str(path))
        iw, ih = image.getSize()
        pw, ph = landscape(A4)
        margin = 8
        scale = min((pw - 2 * margin) / iw, (ph - 2 * margin) / ih)
        w, h = iw * scale, ih * scale
        c.drawImage(image, (pw - w) / 2, (ph - h) / 2, w, h)
        c.showPage()
    c.save()
    buf.seek(0)
    return Response(
        content=buf.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="certificates.pdf"'},
    )


@router.get("/certificates/{cert_id}/download")
def download_certificate(
    cert_id: int,
    format: str = Query("jpg"),
    db: Session = Depends(get_db),
    _=Depends(get_current_admin),
):
    cert = (
        db.query(models.IssuedCertificate)
        .filter(models.IssuedCertificate.id == cert_id)
        .first()
    )
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found.")
    path = CERT_GENERATED_DIR / f"{cert.certificate_number or cert.id}.jpg"
    if not path.is_file():
        cert.rendered_url = None
        from ..document_service import save_rendered_certificate

        save_rendered_certificate(cert)
        db.commit()
    if format == "pdf":
        pdf_bytes = document_pdf_bytes(
            path.read_bytes(),
            orientation="landscape",
            title=f"Certificate {cert.certificate_number}",
        )
        from fastapi.responses import Response

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": (
                    f'attachment; filename="{certificate_download_name(cert)}"'
                    .replace(".jpg", ".pdf")
                )
            },
        )
    return FileResponse(
        path,
        media_type="image/jpeg",
        filename=certificate_download_name(cert),
    )


@router.post("/certificates/{cert_id}/revoke", response_model=schemas.GeneratedCertificateResponse)
def revoke_certificate(
    cert_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_admin),
):
    cert = (
        db.query(models.IssuedCertificate)
        .filter(models.IssuedCertificate.id == cert_id)
        .first()
    )
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found.")
    cert.revoked_at = cert.revoked_at or datetime.utcnow()
    cert.status = "revoked"
    db.commit()
    db.refresh(cert)
    return _cert_to_response(cert)


# ============================================================
# Volunteer ID cards
# ============================================================

@router.get("/volunteers", response_model=list[schemas.GeneratedVolunteerCardResponse])
def list_volunteer_cards(
    status: str | None = "accepted",
    search: str | None = None,
    only_with_cards: bool = False,
    db: Session = Depends(get_db),
    _=Depends(get_current_admin),
):
    query = db.query(models.VolunteerApplication)
    if status and status != "all":
        query = query.filter(models.VolunteerApplication.status == status)
    else:
        query = query.filter(
            models.VolunteerApplication.status.in_(["accepted", "merged", "settings"])
        )
    if only_with_cards:
        query = query.filter(models.VolunteerApplication.card_file_path.isnot(None))
    if search:
        like = f"%{search}%"
        query = query.filter(
            or_(
                models.VolunteerApplication.full_name.ilike(like),
                models.VolunteerApplication.email.ilike(like),
                models.VolunteerApplication.volunteer_id.ilike(like),
            )
        )
    items = query.order_by(models.VolunteerApplication.id.desc()).all()
    return [_volunteer_to_response(item) for item in items]


@router.post(
    "/volunteers/{application_id}/card",
    response_model=schemas.GeneratedVolunteerCardResponse,
)
def generate_volunteer_card(
    application_id: int,
    payload: schemas.VolunteerCardGenerateRequest | None = None,
    db: Session = Depends(get_db),
    _=Depends(get_current_admin),
):
    app = (
        db.query(models.VolunteerApplication)
        .filter(models.VolunteerApplication.id == application_id)
        .first()
    )
    if not app:
        raise HTTPException(status_code=404, detail="Volunteer application not found.")
    if not app.volunteer_id:
        raise HTTPException(status_code=400, detail="Volunteer has no volunteer ID yet.")
    if app.status not in ("accepted", "merged", "settings", "issued"):
        raise HTTPException(status_code=400, detail="Only accepted volunteers can have a card.")

    try:
        build_volunteer_card(
            db,
            app,
            issue_date=payload.issue_date if payload else None,
            valid_till=payload.valid_till if payload else None,
            location=payload.location if payload else None,
            status="issued",
            qr_verification_token=(
                payload.qr_verification_token if payload else None
            ),
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _volunteer_to_response(app)


@router.get("/volunteers/{application_id}/download")
def download_volunteer_card(
    application_id: int,
    format: str = Query("jpg"),
    db: Session = Depends(get_db),
    _=Depends(get_current_admin),
):
    app = (
        db.query(models.VolunteerApplication)
        .filter(models.VolunteerApplication.id == application_id)
        .first()
    )
    if not app or not app.card_file_path:
        raise HTTPException(status_code=404, detail="Volunteer card not found.")
    path = VOLUNTEER_GENERATED_DIR / f"{app.volunteer_id or app.id}.jpg"
    if not path.is_file():
        from ..document_service import save_rendered_volunteer_card

        app.card_file_path = None
        save_rendered_volunteer_card(app)
        db.commit()
    if format == "pdf":
        pdf_path = VOLUNTEER_GENERATED_DIR / f"{app.volunteer_id or app.id}.pdf"
        if not pdf_path.is_file():
            from ..document_service import save_rendered_volunteer_card

            app.card_file_path = None
            save_rendered_volunteer_card(app)
            db.commit()
        from fastapi.responses import Response

        return Response(
            content=pdf_path.read_bytes(),
            media_type="application/pdf",
            headers={
                "Content-Disposition": (
                    f'attachment; filename="{volunteer_card_download_name(app)}"'
                    .replace(".jpg", ".pdf")
                )
            },
        )
    return FileResponse(
        path,
        media_type="image/jpeg",
        filename=volunteer_card_download_name(app),
    )


@router.post("/volunteers/{application_id}/revoke", response_model=schemas.GeneratedVolunteerCardResponse)
def revoke_volunteer_card(
    application_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_admin),
):
    app = (
        db.query(models.VolunteerApplication)
        .filter(models.VolunteerApplication.id == application_id)
        .first()
    )
    if not app:
        raise HTTPException(status_code=404, detail="Volunteer application not found.")
    app.card_revoked_at = app.card_revoked_at or datetime.utcnow()
    app.status = "revoked"
    db.commit()
    db.refresh(app)
    return _volunteer_to_response(app)