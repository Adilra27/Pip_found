"""HTML welcome-card generator for accepted volunteers."""

import html
import mimetypes
from datetime import datetime
from pathlib import Path


ORG_NAME = "Piplad Welfare Foundation"
ORG_TAGLINE = "Creating Opportunities, Creating Lives"

PROFILE_IMAGE_MIME = "image/jpeg"


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
) -> str:
    name = html.escape(full_name)
    vid = html.escape(build_volunteer_id(volunteer_id))
    interest = html.escape(interest_area or "General")
    phone_esc = html.escape(phone or "")
    joined = html.escape(_format_date(accepted_at))
    photo = _photo_html(full_name, use_photo_cid)
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
    (None, None) if the image cannot be loaded; the card then falls back
    to an initials avatar.
    """
    if not profile_pic_url:
        return None, None

    try:
        if profile_pic_url.startswith(("/media/", "media/", "./", ".")):
            relative = profile_pic_url.removeprefix("/media/")
            candidate = Path(__file__).resolve().parents[1] / "media" / relative
            if not candidate.is_file():
                return None, None
            mime = mimetypes.guess_type(candidate.name)[0] or PROFILE_IMAGE_MIME
            return candidate.read_bytes(), mime

        import requests

        response = requests.get(
            profile_pic_url,
            timeout=15,
            headers={"User-Agent": "Piplad-Welcome-Card/1.0", "Accept": "image/*"},
        )
        response.raise_for_status()
        mime = (
            (response.headers.get("Content-Type") or PROFILE_IMAGE_MIME)
            .split(";")[0]
            .strip()
            or PROFILE_IMAGE_MIME
        )
        return response.content, mime
    except Exception:
        return None, None