"""SMTP email sending via Python's standard library smtplib."""

import logging
import os
import smtplib
from email.message import EmailMessage
from email.utils import formataddr

logger = logging.getLogger(__name__)

DEFAULT_FROM_NAME = "Piplad Welfare Foundation"


def is_smtp_configured() -> bool:
    return bool(os.getenv("SMTP_HOST"))


def _from_address() -> tuple[str, str] | None:
    display = os.getenv("SMTP_FROM_NAME", DEFAULT_FROM_NAME) or DEFAULT_FROM_NAME
    address = os.getenv("SMTP_FROM") or os.getenv("SMTP_USER")
    if not address:
        return None
    return display, address


def _deliver_email(
    *,
    to_email: str,
    subject: str,
    text_body: str,
    html_body: str | None = None,
    attachments: list[dict] | None = None,
    related: list[dict] | None = None,
) -> bool:
    """Core SMTP sender supporting HTML bodies, CID images, and attachments.

    `attachments` is a list of {"filename", "data", "maintype", "subtype"}.
    `related`    is a list of {"cid", "data", "maintype", "subtype"} whose
                 items are embedded into the HTML part (e.g. profile photo).

    Always returns False (instead of raising) when SMTP is unavailable or the
    send fails, logging the reason for the admin panel to show later.
    """
    if not is_smtp_configured():
        logger.warning("SMTP is not configured; email NOT sent to %s", to_email)
        return False

    host = os.getenv("SMTP_HOST", "").strip()
    try:
        port = int(os.getenv("SMTP_PORT", "587") or "587")
    except ValueError:
        logger.error("Invalid SMTP_PORT value; not emailing welcome card to %s", to_email)
        return False
    username = os.getenv("SMTP_USER", "").strip()
    password = os.getenv("SMTP_PASSWORD", "")
    use_ssl = (os.getenv("SMTP_SSL", "false") or "false").lower() == "true"
    use_starttls = (os.getenv("SMTP_STARTTLS", "true") or "true").lower() != "false"
    no_auth = (os.getenv("SMTP_NO_AUTH", "false") or "false").lower() == "true"

    if not host or not _from_address():
        logger.warning(
            "SMTP host/from not configured; email NOT sent to %s",
            to_email,
        )
        return False

    try:
        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = formataddr(_from_address())
        message["To"] = to_email
        message.set_content(text_body)

        if html_body:
            message.add_alternative(html_body, subtype="html")

        for image in related or []:
            subtype = image.get("subtype") or ""
            message.get_payload()[-1].add_related(
                image["data"],
                maintype=image.get("maintype", "image"),
                subtype=subtype or "jpeg",
                cid=image["cid"],
            )

        for attachment in attachments or []:
            message.add_attachment(
                attachment["data"],
                maintype=attachment.get("maintype", "application"),
                subtype=attachment.get("subtype", "octet-stream"),
                filename=attachment["filename"],
            )

        if use_ssl:
            smtp = smtplib.SMTP_SSL(host, port, timeout=30)
        else:
            smtp = smtplib.SMTP(host, port, timeout=30)
            if use_starttls:
                smtp.starttls()

        with smtp:
            if not no_auth and username:
                smtp.login(username, password)
            smtp.send_message(message)

        logger.info("Email sent to %s: %s", to_email, subject)
        return True
    except Exception as exc:
        logger.error(
            "Failed to send email to %s (%s): %s",
            to_email,
            subject,
            exc,
        )
        return False


def send_volunteer_welcome_email(
    *,
    to_email: str,
    volunteer_name: str,
    card_html: str,
    certificate_pdf: bytes | None = None,
    profile_image_bytes=None,
    profile_image_mime="image/jpeg",
) -> bool:
    """Send the volunteer welcome card email with a PDF certificate attached."""
    text_body = (
        f"Dear {volunteer_name},\n\n"
        "Congratulations and welcome! Your volunteer application with the "
        "Piplad Welfare Foundation has been accepted. Please find your "
        "Volunteer Certificate attached to this email and keep it handy for "
        "future events and communication.\n\n"
        "Thank you for choosing to serve your community.\n"
        "Piplad Welfare Foundation\nCreating Opportunities, Creating Lives"
    )

    attachments = []
    if certificate_pdf:
        attachments.append(
            {
                "filename": "Volunteer_Certificate.pdf",
                "data": certificate_pdf,
                "maintype": "application",
                "subtype": "pdf",
            }
        )

    related = []
    if profile_image_bytes:
        related.append(
            {
                "cid": "volunteer_photo",
                "data": profile_image_bytes,
                "maintype": "image",
                "subtype": (profile_image_mime or "image/jpeg").split("/")[-1] or "jpeg",
            }
        )

    return _deliver_email(
        to_email=to_email,
        subject="Your Volunteer Certificate - Piplad Welfare Foundation",
        text_body=text_body,
        html_body=card_html,
        attachments=attachments,
        related=related,
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
    certificate_pdf: bytes | None = None,
    receipt_pdf: bytes | None = None,
) -> bool:
    """Send the donation PDF certificate, PDF receipt, and an HTML receipt."""
    text_body = (
        f"Dear {donor_name},\n\n"
        "Thank you for your generous donation to the Piplad Welfare "
        "Foundation. Please find attached your Donation Certificate and "
        "Donation Receipt (80G) in PDF format. Keep them safe for your "
        "records and tax filing purposes.\n\n"
        "Thank you for making a difference.\n"
        "Piplad Welfare Foundation\nCreating Opportunities, Creating Lives"
    )

    attachments = []
    if certificate_pdf:
        attachments.append(
            {
                "filename": "Donation_Certificate.pdf",
                "data": certificate_pdf,
                "maintype": "application",
                "subtype": "pdf",
            }
        )
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
        subject="Your Donation Certificate & Receipt - Piplad Welfare Foundation",
        text_body=text_body,
        html_body=receipt_html,
        attachments=attachments,
    )