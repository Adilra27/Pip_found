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


def send_volunteer_welcome_email(
    *,
    to_email: str,
    volunteer_name: str,
    card_html: str,
    profile_image_bytes=None,
    profile_image_mime="image/jpeg",
) -> bool:
    """Send the volunteer welcome card email.

    Returns True when the email was accepted by the SMTP server. Always
    returns False (instead of raising) when SMTP is not configured or the
    send fails, logging the reason for the admin panel to show later.
    """
    if not is_smtp_configured():
        logger.warning(
            "SMTP is not configured; welcome card NOT emailed to %s",
            to_email,
        )
        return False

    host = os.getenv("SMTP_HOST", "").strip()
    port = int(os.getenv("SMTP_PORT", "587") or "587")
    username = os.getenv("SMTP_USER", "").strip()
    password = os.getenv("SMTP_PASSWORD", "")
    use_ssl = (os.getenv("SMTP_SSL", "false") or "false").lower() == "true"
    use_starttls = (os.getenv("SMTP_STARTTLS", "true") or "true").lower() != "false"
    no_auth = (os.getenv("SMTP_NO_AUTH", "false") or "false").lower() == "true"

    if not host or not _from_address():
        logger.warning(
            "SMTP host/from not configured; welcome card NOT emailed to %s",
            to_email,
        )
        return False

    try:
        message = EmailMessage()
        message["Subject"] = "Your Volunteer Welcome Card - Piplad Welfare Foundation"
        message["From"] = formataddr(_from_address())
        message["To"] = to_email

        text_body = (
            f"Dear {volunteer_name},\n\n"
            "Congratulations and welcome! Your volunteer application with the "
            "Piplad Welfare Foundation has been accepted. Please find your "
            "Volunteer Welcome Card in this email and keep it handy for future "
            "events and communication.\n\n"
            "Thank you for choosing to serve your community.\n"
            "Piplad Welfare Foundation\nCreating Opportunities, Creating Lives"
        )
        message.set_content(text_body)

        message.add_alternative(
            card_html,
            subtype="html",
        )

        if profile_image_bytes:
            subtype = (profile_image_mime or "image/jpeg").split("/")[-1].lower()
            message.get_payload()[1].add_related(
                profile_image_bytes,
                maintype="image",
                subtype=subtype or "jpeg",
                cid="volunteer_photo",
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

        logger.info("Welcome card emailed to %s", to_email)
        return True
    except Exception as exc:
        logger.error(
            "Failed to email welcome card to %s: %s",
            to_email,
            exc,
        )
        return False