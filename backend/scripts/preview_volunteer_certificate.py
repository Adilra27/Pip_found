"""Preview the volunteer certificate render locally so you can fine-tune the
placement constants in backend/app/volunteer_certificate.py.

Run from the repo root (or anywhere):  python backend/scripts/preview_volunteer_certificate.py
Writes Volunteer_Certificate_preview.jpg at the repo root. Inspect the image,
adjust the NAME_*/DATE_* constants, and re-run until it looks right.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.volunteer_certificate import build_volunteer_certificate_image

pixels = build_volunteer_certificate_image(
    full_name="John Doe",
)
out = Path(__file__).resolve().parents[2] / "Volunteer_Certificate_preview.jpg"
out.write_bytes(pixels)
print(f"Preview written to {out} ({len(pixels)} bytes)")