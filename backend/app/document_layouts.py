"""Document layout coordinates for the official Piplad templates.

Single source of truth for where each dynamic field is stamped onto:

* the 4 official certificate backgrounds (1536 x 1024 landscape) and
* the official volunteer ID card background (1388 x 1133 portrait).

Each field anchor supports: x, y, font_size, max_width, color, anchor
(PIL text anchor, default "mm" = centered) and an optional box that is
blanked out before the real text is drawn.

The ``qr`` anchor controls the overlay position for the dynamic
verification QR code.
"""

# Official volunteer ID card background.
VOLUNTEER_CARD_IMAGE = "certificate_templates/volunteer card.png"

# Official certificate backgrounds, keyed by certificate document type.
CERTIFICATE_IMAGES = {
    "appreciation": "certificate_templates/Certificate of Appriciation.png",
    "completion": "certificate_templates/Certificate of Completion.png",
    "internship": "certificate_templates/Certificate of Internship.png",
    "participation": "certificate_templates/Certificate of Participation.jpeg",
}

# Valid certificate document types that can be issued through the generator.
CERTIFICATE_TYPES = tuple(CERTIFICATE_IMAGES.keys())

# CertificateTemplate slug used when seeding / resolving each certificate type.
CERTIFICATE_TEMPLATE_SLUGS = {
    "appreciation": "certificate-of-appreciation",
    "completion": "certificate-of-completion",
    "internship": "certificate-of-internship",
    "participation": "certificate-of-participation",
}

# Human-facing label used in the admin generator dropdowns.
CERTIFICATE_LABELS = {
    "appreciation": "Certificate of Appreciation",
    "completion": "Certificate of Completion",
    "internship": "Certificate of Internship",
    "participation": "Certificate of Participation",
}

_FIELD_META = {
    "name": {
        "x": 768, "font_size": 52, "max_width": 860, "color": "#1f2937", "anchor": "mm",
    },
    "program_name": {
        "x": 768, "font_size": 24, "max_width": 760, "color": "#334155", "anchor": "mm",
    },
    "certificate_number": {
        "x": 600, "font_size": 18, "max_width": 230, "color": "#475569", "anchor": "mm",
    },
    "issue_date": {
        "x": 936, "font_size": 18, "max_width": 230, "color": "#475569", "anchor": "mm",
    },
    "date_line": {
        "x": 768, "font_size": 20, "max_width": 560, "color": "#475569", "anchor": "mm",
    },
}

# Shared QR slot = bottom-right corner of the certificate.
_CERT_QR = {"x": 1410, "y": 848, "size": 140, "anchor": "mm"}

DOCUMENT_LAYOUTS = {
    "appreciation": {
        "name": {**_FIELD_META["name"], "y": 427},
        "program_name": {**_FIELD_META["program_name"], "y": 608},
        "certificate_number": {**_FIELD_META["certificate_number"], "y": 738},
        "issue_date": {**_FIELD_META["issue_date"], "y": 739},
        "qr": {**_CERT_QR},
    },
    "internship": {
        "name": {**_FIELD_META["name"], "y": 425},
        "program_name": {**_FIELD_META["program_name"], "y": 661},
        "starting_date": {
            "x": 580, "y": 585, **_FIELD_META["date_line"], "max_width": 430,
        },
        "end_date": {
            "x": 956, "y": 585, **_FIELD_META["date_line"], "max_width": 430,
        },
        "certificate_number": {**_FIELD_META["certificate_number"], "y": 735},
        "issue_date": {**_FIELD_META["issue_date"], "y": 736},
        "qr": {**_CERT_QR},
    },
    "completion": {
        "name": {**_FIELD_META["name"], "y": 424},
        "program_name": {**_FIELD_META["program_name"], "y": 556},
        "organisation_name": {
            "x": 585, "y": 605, **_FIELD_META["date_line"], "max_width": 330,
        },
        "competition_date": {
            "x": 768, "y": 605, **_FIELD_META["date_line"], "max_width": 330,
        },
        "competition_location": {
            "x": 951, "y": 605, **_FIELD_META["date_line"], "max_width": 330,
        },
        "certificate_number": {**_FIELD_META["certificate_number"], "y": 734},
        "issue_date": {**_FIELD_META["issue_date"], "y": 735},
        "qr": {**_CERT_QR},
    },
    "participation": {
        "name": {**_FIELD_META["name"], "y": 422},
        "program_name": {**_FIELD_META["program_name"], "y": 558},
        "competition_date": {
            "x": 768, "y": 563, **_FIELD_META["date_line"], "max_width": 560,
        },
        "competition_location": {
            "x": 768, "y": 665, **_FIELD_META["date_line"], "max_width": 560,
        },
        "certificate_number": {**_FIELD_META["certificate_number"], "y": 746},
        "issue_date": {**_FIELD_META["issue_date"], "y": 746},
        "qr": {**_CERT_QR},
    },
    "volunteer": {
        "name": {
            "x": 1065, "y": 358, "font_size": 44, "max_width": 640,
            "color": "#1f2937", "anchor": "mm", "box": None,
        },
        "volunteer_id": {
            "x": 1140, "y": 610, "font_size": 22, "max_width": 300,
            "color": "#047857", "anchor": "lm", "box": None,
        },
        "programme": {
            "x": 1140, "y": 688, "font_size": 20, "max_width": 300,
            "color": "#334155", "anchor": "lm", "box": None,
        },
        "location": {
            "x": 1140, "y": 760, "font_size": 20, "max_width": 300,
            "color": "#334155", "anchor": "lm", "box": None,
        },
        "issue_date": {
            "x": 860, "y": 640, "font_size": 19, "max_width": 280,
            "color": "#475569", "anchor": "mm", "box": None,
        },
        "valid_till": {
            "x": 860, "y": 710, "font_size": 19, "max_width": 280,
            "color": "#475569", "anchor": "mm", "box": None,
        },
        "photo": {
            "x": 340, "y": 350, "size": 240, "anchor": "mm",
        },
        "qr": {
            "x": 870, "y": 900, "size": 140, "anchor": "mm",
        },
    },
}


def layout_for(document_type: str) -> dict:
    """Return a deep-copied layout dict for a document type (safe to mutate)."""
    import copy

    base = DOCUMENT_LAYOUTS[document_type]
    return copy.deepcopy(base)


def certificate_image_url(document_type: str) -> str:
    return CERTIFICATE_IMAGES[document_type]