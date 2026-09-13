"""Email sending via the Brevo HTTPS API only.

Render's free tier blocks outbound SMTP ports (25, 465, 587), so all email
sends through Brevo's REST API over HTTPS (port 443), which is never blocked.

When BREVO_API_KEY is missing the send is skipped with a logged warning so the
failure is visible (e.g. in the admin panel) instead of raising.
"""

import base64
import logging
import os

import requests

logger = logging.getLogger(__name__)

DEFAULT_FROM_NAME = "Piplad Welfare Foundation"
BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"


def is_brevo_configured() -> bool:
    return bool(os.getenv("BREVO_API_KEY"))


def _from_address() -> tuple[str, str] | None:
    display = os.getenv("EMAIL_FROM_NAME") or DEFAULT_FROM_NAME
    address = os.getenv("EMAIL_FROM")
    if not address:
        return None
    return display, address


def _brevo_attachment(attachment: dict) -> dict:
    return {
        "name": attachment["filename"],
        "content": base64.b64encode(attachment["data"]).decode("ascii"),
    }


def _deliver_via_brevo(
    *,
    to_email: str,
    subject: str,
    text_body: str,
    html_body: str | None = None,
    attachments: list[dict] | None = None,
) -> bool:
    """Send via Brevo's transactional email API (POST over HTTPS, port 443).

    Returns False instead of raising when the API call fails, logging the
    reason so the admin panel can retry later.
    """
    api_key = os.getenv("BREVO_API_KEY", "").strip()
    from_addr = _from_address()
    if not api_key or not from_addr:
        logger.warning("Brevo API key/from not configured; email NOT sent to %s", to_email)
        return False

    payload = {
        "sender": {"name": from_addr[0], "email": from_addr[1]},
        "to": [{"email": to_email}],
        "subject": subject,
        "textContent": text_body,
    }
    if html_body:
        payload["htmlContent"] = html_body
    if attachments:
        payload["attachment"] = [_brevo_attachment(a) for a in attachments]

    try:
        response = requests.post(
            BREVO_API_URL,
            headers={
                "api-key": api_key,
                "Content-Type": "application/json",
                "accept": "application/json",
            },
            json=payload,
            timeout=60,
        )
        if response.status_code not in (200, 201):
            logger.error(
                "Brevo API error (%s) for %s (%s): %s",
                response.status_code,
                to_email,
                subject,
                response.text[:2000],
            )
            return False
        logger.info("Email sent via Brevo to %s: %s", to_email, subject)
        return True
    except Exception as exc:
        logger.error(
            "Failed to send email via Brevo to %s (%s): %s",
            to_email,
            subject,
            exc,
        )
        return False


def _deliver_email(
    *,
    to_email: str,
    subject: str,
    text_body: str,
    html_body: str | None = None,
    attachments: list[dict] | None = None,
) -> bool:
    """Core sender supporting HTML bodies and attachments via the Brevo API.

    `attachments` is a list of {"filename", "data", "maintype", "subtype"}.

    Requires BREVO_API_KEY to be configured; otherwise the send is skipped
    with a logged warning (returns False) so failures stay visible.

    Always returns False (instead of raising) when email is unavailable or the
    send fails, logging the reason for the admin panel to show later.
    """
    if is_brevo_configured():
        return _deliver_via_brevo(
            to_email=to_email,
            subject=subject,
            text_body=text_body,
            html_body=html_body,
            attachments=attachments,
        )

    logger.warning(
        "Email not configured (BREVO_API_KEY missing); email NOT sent to %s",
        to_email,
    )
    return False


def send_volunteer_welcome_email(
    *,
    to_email: str,
    volunteer_name: str,
    volunteer_email: str,
    volunteer_id: str,
    joined_date,
    card_jpg: bytes,
    certificate_image: bytes | None = None,
) -> bool:
    """Send the volunteer welcome e-mail: message body + card JPG + certificate.

    The e-mail body is the friendly welcome message (HTML + plain text); the
    graphical welcome card (QR + profile photo) and the official certificate
    are attached as JPEG files so they display in every e-mail client.
    """
    from .welcome_card import build_welcome_message_html, build_welcome_message_text

    text_body = build_welcome_message_text(
        full_name=volunteer_name,
        volunteer_email=volunteer_email,
        volunteer_id=volunteer_id,
        joined_date=joined_date,
    )
    html_body = build_welcome_message_html(
        full_name=volunteer_name,
        volunteer_email=volunteer_email,
        volunteer_id=volunteer_id,
        joined_date=joined_date,
    )

    attachments = [
        {
            "filename": "Volunteer_Card.jpg",
            "data": card_jpg,
            "maintype": "image",
            "subtype": "jpeg",
        }
    ]
    if certificate_image:
        attachments.append(
            {
                "filename": "Volunteer_Certificate.jpg",
                "data": certificate_image,
                "maintype": "image",
                "subtype": "jpeg",
            }
        )

    return _deliver_email(
        to_email=to_email,
        subject="Welcome to Piplad Welfare Foundation!",
        text_body=text_body,
        html_body=html_body,
        attachments=attachments,
    )


def send_volunteer_rejection_email(
    *,
    to_email: str,
    volunteer_name: str,
    interest_area: str,
) -> bool:
    """Inform a volunteer that their application was declined by the admin."""
    text_body = (
        f"Dear {volunteer_name},\n\n"
        "Thank you for your interest in volunteering with the Piplad Welfare "
        "Foundation. After careful review, we regret to inform you that your "
        "volunteer application"
        + (f" for the area of {interest_area}" if interest_area else "")
        + " has not been accepted at this time.\n\n"
        "We encourage you to apply again in the future. If you have any "
        "questions, please reach out to us at info@pipladfoundation.in.\n\n"
        "With regards,\n"
        "Piplad Welfare Foundation\nCreating Opportunities, Creating Lives"
    )

    return _deliver_email(
        to_email=to_email,
        subject="Update on your Volunteer Application - Piplad Welfare Foundation",
        text_body=text_body,
    )


def send_donation_documents_email(
    *,
    to_email: str,
    donor_name: str,
    receipt_html: str,
    receipt_pdf: bytes | None = None,
) -> bool:
    """Send the donation receipt e-mail: HTML receipt + 80G receipt PDF."""
    text_body = (
        f"Dear {donor_name},\n\n"
        "Thank you for your generous donation to the Piplad Welfare "
        "Foundation. Please find attached your Donation Receipt (80G) in "
        "PDF format. Keep it safe for your records and tax filing purposes.\n\n"
        "Thank you for making a difference.\n"
        "Piplad Welfare Foundation\nCreating Opportunities, Creating Lives"
    )

    attachments = []
    if receipt_pdf:
        attachments.append(
            {
                "filename": "Donation_Receipt_80G.pdf",
                "data": receipt_pdf,
                "maintype": "application",
                "subtype": "pdf",
            }
        )

    return _deliver_email(
        to_email=to_email,
        subject="Your Donation Receipt - Piplad Welfare Foundation",
        text_body=text_body,
        html_body=receipt_html,
        attachments=attachments,
    )


def send_certificate_email(
    *,
    to_email: str,
    recipient_name: str,
    type_label: str,
    event_topic: str,
    event_date: str,
    image_bytes: bytes,
    filename: str,
) -> bool:
    """Email a rendered certificate/card image to a recipient."""
    clean_type = (type_label or "Certificate").strip() or "Certificate"
    body_lines = [
        f"Dear {recipient_name},",
        "",
        f"We are pleased to share your {clean_type} from the Piplad "
        "Welfare Foundation.",
        "",
    ]
    if event_topic:
        body_lines.append(f"Event / Topic: {event_topic}")
    if event_date:
        body_lines.append(f"Date: {event_date}")
    body_lines += [
        "",
        "The certificate is attached to this e-mail. Please keep it safe "
        "and feel free to share it on your social profiles.",
        "",
        "With regards,",
        "Piplad Welfare Foundation",
        "Creating Opportunities, Creating Lives",
    ]

    return _deliver_email(
        to_email=to_email,
        subject=f"Your {clean_type} - Piplad Welfare Foundation",
        text_body="\n".join(body_lines),
        attachments=[
            {
                "filename": filename,
                "data": image_bytes,
                "maintype": "image",
                "subtype": "jpeg",
            }
        ],
    )


def send_team_card_email(
    *,
    to_email: str,
    recipient_name: str,
    member_id: str,
    image_bytes: bytes,
) -> bool:
    """Email a rendered team member ID card to the member."""
    text_body = (
        f"Dear {recipient_name},\n\n"
        "Welcome to the Piplad Welfare Foundation family! Please find your "
        "Team Member ID Card attached to this e-mail.\n"
        f"Member ID: {member_id}\n\n"
        "Keep your ID card handy for team events, meetings and official "
        "communication.\n\n"
        "With regards,\n"
        "Piplad Welfare Foundation\nCreating Opportunities, Creating Lives"
    )

    return _deliver_email(
        to_email=to_email,
        subject="Your Team Member ID Card - Piplad Welfare Foundation",
        text_body=text_body,
        attachments=[
            {
                "filename": "Team_Member_ID_Card.jpg",
                "data": image_bytes,
                "maintype": "image",
                "subtype": "jpeg",
            }
        ],
    )