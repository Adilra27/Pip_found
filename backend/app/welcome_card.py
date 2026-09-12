"""Welcome-card generator and welcome e-mail message builder for volunteers."""

import html
import logging
import mimetypes
import os
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

ORG_NAME = "Piplad Welfare Foundation"
ORG_TAGLINE = "Creating Opportunities, Creating Lives"

DEFAULT_CONTACT_WEBSITE = "https://www.pipladfoundation.in"
DEFAULT_CONTACT_EMAIL = "info@pipladfoundation.in"

PROFILE_IMAGE_MIME = "image/jpeg"
MAX_EMAIL_PHOTO_BYTES = 2 * 1024 * 1024


def build_volunteer_id(volunteer_id: str) -> str:
    if volunteer_id:
        return volunteer_id
    return "PWF-VOL-STANDBY"


def _initials(full_name: str) -> str:
    parts = [part for part in full_name.split() if part]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][0].upper()
    return (parts[0][0] + parts[-1][0]).upper()


def _format_date(value) -> str:
    if not value:
        return "Recently accepted"
    if isinstance(value, datetime):
        return value.strftime("%d %B %Y")
    return str(value)


def build_volunteer_qr_png(
    volunteer_id: str,
    scale: int = 6,
    border: int = 2,
) -> bytes | None:
    """Return PNG bytes of the volunteer-ID QR code, or None if generation fails."""
    try:
        import io

        import segno

        qr = segno.make(
            build_volunteer_id(volunteer_id or ""),
            error="m",
            micro=False,
        )
        buffer = io.BytesIO()
        qr.save(buffer, kind="png", scale=scale, border=border)
        return buffer.getvalue()
    except Exception as exc:
        logger.error("Failed to generate volunteer QR code: %s", exc)
        return None


def build_volunteer_qr_data_uri(volunteer_id: str) -> str | None:
    """Return a ``data:image/png;base64,...`` QR code for the volunteer ID.

    Returns None if QR generation fails so the card can still be emailed.
    """
    png = build_volunteer_qr_png(volunteer_id)
    if not png:
        return None
    from base64 import b64encode

    return "data:image/png;base64," + b64encode(png).decode("ascii")


def _qr_html(volunteer_id: str, qr_data_uri: str | None) -> str:
    if not qr_data_uri:
        return ""
    vid = html.escape(build_volunteer_id(volunteer_id))
    return f"""
          <tr>
            <td style="padding:18px 40px;text-align:center;">
              <img src="{qr_data_uri}"
                   alt="Volunteer QR code"
                   style="width:150px;height:150px;display:block;margin:0 auto;border-radius:8px;" />
              <div style="margin-top:8px;font-size:13px;font-weight:700;color:#0f172a;">Scan to verify: {vid}</div>
            </td>
          </tr>"""


def _photo_html(full_name: str, use_photo_cid: bool) -> str:
    if use_photo_cid:
        return (
            '<img src="cid:volunteer_photo" alt="Profile photo" '
            'style="width:120px;height:120px;border-radius:50%;object-fit:cover;'
            'border:4px solid #bef264;display:block;margin:0 auto;" />'
        )
    initials = html.escape(_initials(full_name))
    return (
        f'<div style="width:120px;height:120px;border-radius:50%;'
        f'background:#f7fee7;border:4px solid #bef264;display:flex;'
        f'align-items:center;justify-content:center;margin:0 auto;'
        f'font-size:2.6rem;font-weight:800;color:#3f6212;">'
        f'{initials}</div>'
    )


def build_welcome_card_html(
    *,
    full_name: str,
    volunteer_id: str,
    interest_area: str,
    phone: str,
    accepted_at,
    use_photo_cid: bool = False,
    qr_data_uri: str | None = None,
) -> str:
    name = html.escape(full_name)
    vid = html.escape(build_volunteer_id(volunteer_id))
    interest = html.escape(interest_area or "General")
    phone_esc = html.escape(phone or "")
    joined = html.escape(_format_date(accepted_at))
    photo = _photo_html(full_name, use_photo_cid)
    qr_section = _qr_html(volunteer_id, qr_data_uri)
    reach_note = (
        f" and to reach him/her at {phone_esc}" if phone_esc else ""
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Volunteer Welcome Card</title>
</head>
<body style="margin:0;padding:0;background:#f1f5f9;font-family:Arial,Helvetica,sans-serif;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#f1f5f9;padding:24px 0;">
    <tr>
      <td align="center">
        <table role="presentation" width="600" cellspacing="0" cellpadding="0" style="width:600px;max-width:100%;background:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 12px 32px rgba(15,23,42,0.12);">
          <tr>
            <td style="background:#0f172a;padding:28px 36px;text-align:center;">
              <div style="display:inline-block;background:#84cc16;color:#ffffff;font-size:13px;font-weight:800;letter-spacing:1px;padding:6px 16px;border-radius:999px;text-transform:uppercase;">{ORG_NAME}</div>
              <div style="color:#a3e635;font-size:13px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;margin-top:12px;">Volunteer Welcome Card</div>
            </td>
          </tr>
          <tr>
            <td style="padding:36px 40px 12px;text-align:center;">
              {photo}
              <h1 style="margin:20px 0 6px;font-size:26px;color:#0f172a;">Welcome aboard, {name}!</h1>
              <p style="margin:0;color:#64748b;font-size:15px;line-height:1.7;">
                We are thrilled to formally welcome you to the {ORG_NAME} volunteer family.
              </p>
            </td>
          </tr>
          <tr>
            <td style="padding:24px 40px;">
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:12px;">
                <tr>
                  <td style="padding:14px 18px;">
                    <div style="font-size:12px;font-weight:700;color:#94a3b8;text-transform:uppercase;letter-spacing:0.5px;">Volunteer Name</div>
                    <div style="font-size:16px;font-weight:700;color:#0f172a;margin-top:4px;">{name}</div>
                  </td>
                </tr>
                <tr>
                  <td style="padding:14px 18px;border-top:1px solid #e2e8f0;">
                    <div style="font-size:12px;font-weight:700;color:#94a3b8;text-transform:uppercase;letter-spacing:0.5px;">Volunteer ID</div>
                    <div style="font-size:16px;font-weight:700;color:#059669;margin-top:4px;">{vid}</div>
                  </td>
                </tr>
                <tr>
                  <td style="padding:14px 18px;border-top:1px solid #e2e8f0;">
                    <div style="font-size:12px;font-weight:700;color:#94a3b8;text-transform:uppercase;letter-spacing:0.5px;">Area of Interest</div>
                    <div style="font-size:16px;font-weight:700;color:#0f172a;margin-top:4px;">{interest}</div>
                  </td>
                </tr>
                <tr>
                  <td style="padding:14px 18px;border-top:1px solid #e2e8f0;">
                    <div style="font-size:12px;font-weight:700;color:#94a3b8;text-transform:uppercase;letter-spacing:0.5px;">Joined</div>
                    <div style="font-size:16px;font-weight:700;color:#0f172a;margin-top:4px;">{joined}</div>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          {qr_section}
          <tr>
            <td style="padding:0 40px 8px;">
              <p style="margin:0;color:#334155;font-size:14px;line-height:1.7;">
                Your coordinator will reach out shortly with details of orientation, upcoming
                volunteer sessions, and how you can begin making a difference. Please keep your
                Volunteer ID handy for future events and communication{reach_note}.
              </p>
            </td>
          </tr>
          <tr>
            <td style="background:#0f172a;padding:20px 40px;text-align:center;margin-top:16px;">
              <div style="color:#cbd5e1;font-size:12px;line-height:1.6;">
                Thank you for choosing to serve your community.<br />
                <span style="color:#ffffff;font-weight:700;font-size:14px;">{ORG_TAGLINE}</span>
              </div>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


def load_profile_photo(profile_pic_url: str):
    """Return (content_bytes, mime) for a volunteer profile picture.

    Supports Cloudinary/http(s) URLs and local /media/ paths. Returns
    (None, None) if the image cannot be loaded or is not a valid image;
    the card then falls back to an initials avatar. Failures are logged.
    """
    if not profile_pic_url:
        return None, None

    try:
        mime = None
        if profile_pic_url.startswith(("/media/", "media/", "./", ".")):
            relative = profile_pic_url.removeprefix("/media/")
            candidate = Path(__file__).resolve().parents[1] / "media" / relative
            if not candidate.is_file():
                logger.warning("Profile photo not found on disk: %s", profile_pic_url)
                return None, None
            if candidate.stat().st_size > MAX_EMAIL_PHOTO_BYTES:
                logger.warning("Profile photo too large to email: %s", profile_pic_url)
                return None, None
            mime = mimetypes.guess_type(candidate.name)[0] or PROFILE_IMAGE_MIME
            data = candidate.read_bytes()
        else:
            import requests

            session = requests.Session()
            adapter = requests.adapters.HTTPAdapter(max_retries=1)
            session.mount("http://", adapter)
            session.mount("https://", adapter)

            response = session.get(
                profile_pic_url,
                timeout=(3.05, 5),
                headers={"User-Agent": "Piplad-Welcome-Card/1.0", "Accept": "image/*"},
            )
            response.raise_for_status()
            if len(response.content) > MAX_EMAIL_PHOTO_BYTES:
                logger.warning("Profile photo too large to email: %s", profile_pic_url)
                return None, None
            mime = (
                (response.headers.get("Content-Type") or PROFILE_IMAGE_MIME)
                .split(";")[0]
                .strip()
                or PROFILE_IMAGE_MIME
            )
            data = response.content

        if not mime.lower().startswith("image/"):
            logger.warning("Profile photo has non-image MIME %r: %s", mime, profile_pic_url)
            return None, None
        return data, mime
    except Exception as exc:
        logger.warning("Could not load profile photo %s: %s", profile_pic_url, exc)
        return None, None


def _contact_info() -> tuple[str, str, str]:
    """Return (website, contact_email, contact_phone) from env, with defaults.

    Website/email fall back to the organisation defaults; the phone number is
    only shown when CONTACT_PHONE is configured.
    """
    website = (
        os.getenv("CONTACT_WEBSITE") or DEFAULT_CONTACT_WEBSITE
    ) or DEFAULT_CONTACT_WEBSITE
    contact_email = (
        os.getenv("CONTACT_EMAIL") or DEFAULT_CONTACT_EMAIL
    ) or DEFAULT_CONTACT_EMAIL
    contact_phone = os.getenv("CONTACT_PHONE", "") or ""
    return website.strip(), contact_email.strip(), contact_phone.strip()


def build_welcome_message_text(
    *,
    full_name: str,
    volunteer_email: str,
    volunteer_id: str,
    joined_date,
) -> str:
    """Plain-text version of the volunteer welcome e-mail (no card markup)."""
    website, contact_email, contact_phone = _contact_info()
    vid = build_volunteer_id(volunteer_id)

    lines = [
        f"Dear {full_name},",
        "",
        "A very warm welcome to the Piplad Family!",
        "",
        "We are delighted to have you join us as a volunteer at the Piplad "
        "Welfare Foundation. Your decision to contribute your time, skills, "
        "and energy toward creating a positive impact means a lot to us.",
        "",
        "As a volunteer, you are now an important part of our mission to "
        "create opportunities and create lives. Together, we can work toward "
        "making a meaningful difference in the lives of individuals and "
        "communities who need support.",
        "",
        "We look forward to your ideas, enthusiasm, and active participation "
        "in our upcoming initiatives and activities.",
        "",
        "Your Volunteer Details",
        f"Name: {full_name}",
        f"Email: {volunteer_email}",
        f"Volunteer ID: {vid}",
        f"Joining Date: {_format_date(joined_date)}",
        "",
        "If you have any questions or need assistance, please feel free to "
        "reach out to our team.",
        "",
        f"Once again, welcome to the Piplad Family! We are happy to have you "
        "with us and look forward to making a difference together.",
        "",
        "Warm regards,",
        f"Team {ORG_NAME}",
        ORG_TAGLINE,
        website,
        contact_email,
    ]
    if contact_phone:
        lines.append(contact_phone)

    return "\n".join(lines) + "\n"


def build_welcome_message_html(
    *,
    full_name: str,
    volunteer_email: str,
    volunteer_id: str,
    joined_date,
) -> str:
    """HTML version of the volunteer welcome e-mail (no card markup).

    This is the readable message shown in the e-mail body; the graphical
    volunteer card is sent as a JPG attachment.
    """
    website, contact_email, contact_phone = _contact_info()
    vid = build_volunteer_id(volunteer_id)
    esc = html.escape
    website_href = esc(website)

    contact_lines = [f'<a href="{website_href}" style="color:#3f6212;">{esc(website)}</a>', esc(contact_email)]
    if contact_phone:
        contact_lines.append(esc(contact_phone))
    contact_footer = "<br/>".join(contact_lines)

    details_rows = "".join(
        f"""
            <tr>
              <td style="padding:12px 18px;border-top:1px solid #e2e8f0;">
                <div style="font-size:11px;font-weight:700;color:#94a3b8;text-transform:uppercase;letter-spacing:0.5px;">{label}</div>
                <div style="font-size:15px;font-weight:700;color:#0f172a;margin-top:3px;">{esc(value)}</div>
              </td>
            </tr>"""
        for label, value in (
            ("Name", full_name),
            ("Email", volunteer_email),
            ("Volunteer ID", vid),
            ("Joining Date", _format_date(joined_date)),
        )
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Welcome to Piplad</title>
</head>
<body style="margin:0;padding:0;background:#f8fafc;font-family:Arial,Helvetica,sans-serif;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#f8fafc;padding:24px 0;">
    <tr>
      <td align="center">
        <table role="presentation" width="600" cellspacing="0" cellpadding="0" style="width:600px;max-width:100%;background:#ffffff;border-radius:12px;overflow:hidden;border:1px solid #e2e8f0;">
          <tr>
            <td style="background:#0f172a;padding:22px 32px;text-align:center;">
              <div style="color:#ffffff;font-size:18px;font-weight:700;">{esc(ORG_NAME)}</div>
              <div style="color:#a3e635;font-size:12px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;margin-top:4px;">Welcome to the Piplad Family</div>
            </td>
          </tr>
          <tr>
            <td style="padding:28px 32px;font-size:15px;line-height:1.8;color:#334155;">
              <p style="margin:0 0 16px;">Dear <strong>{esc(full_name)}</strong>,</p>
              <p style="margin:0 0 16px;">A very warm welcome to the <strong>Piplad Family!</strong></p>
              <p style="margin:0 0 16px;">We are delighted to have you join us as a volunteer at the <strong>Piplad Welfare Foundation</strong>. Your decision to contribute your time, skills, and energy toward creating a positive impact means a lot to us.</p>
              <p style="margin:0 0 16px;">As a volunteer, you are now an important part of our mission to <strong>create opportunities and create lives</strong>. Together, we can work toward making a meaningful difference in the lives of individuals and communities who need support.</p>
              <p style="margin:0 0 16px;">We look forward to your ideas, enthusiasm, and active participation in our upcoming initiatives and activities.</p>

              <div style="font-size:14px;font-weight:800;color:#3f6212;text-transform:uppercase;letter-spacing:0.5px;margin:20px 0 8px;">Your Volunteer Details</div>
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="border:1px solid #e2e8f0;border-radius:10px;">{details_rows}</table>

              <p style="margin:16px 0 0;">If you have any questions or need assistance, please feel free to reach out to our team.</p>
              <p style="margin:16px 0 0;">Once again, <strong>welcome to the Piplad Family!</strong> We are happy to have you with us and look forward to making a difference together.</p>
              <p style="margin:20px 0 0;">Warm regards,<br />
                <strong>Team {esc(ORG_NAME)}</strong><br />
                <em>{esc(ORG_TAGLINE)}</em>
              </p>
            </td>
          </tr>
          <tr>
            <td style="background:#f8fafc;border-top:1px solid #e2e8f0;padding:16px 32px;text-align:center;font-size:13px;line-height:1.7;color:#64748b;">
              {contact_footer}
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""
