from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


# ============================================================
# CAUSE SCHEMAS
# ============================================================

class CauseBase(BaseModel):
    title: str
    category: Optional[str] = "General"
    short_description: str
    full_description: Optional[str] = None
    target_amount: float
    raised_amount: Optional[float] = 0.0
    image_url: Optional[str] = None


class CauseCreate(CauseBase):
    slug: str


class CauseResponse(CauseBase):
    id: int
    slug: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# CONTACT SCHEMAS
# ============================================================

class ContactCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    subject: Optional[str] = None
    message: str


class ContactResponse(ContactCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# DONATION SCHEMAS
# ============================================================

class DonationCreate(BaseModel):
    donor_name: str
    donor_email: str
    donor_phone: Optional[str] = None
    amount: float
    cause_id: Optional[int] = None


class RazorpayOrderCreate(BaseModel):
    amount: float
    currency: str = "INR"
    donor_name: str
    donor_email: str
    donor_phone: Optional[str] = None
    cause_id: Optional[int] = None


class RazorpayVerifyRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    donation_id: int


class DonationResponse(BaseModel):
    id: int
    donor_name: str
    donor_email: str
    donor_phone: Optional[str] = None
    amount: float
    cause_id: Optional[int] = None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# GALLERY / PHOTO SCHEMAS
# ============================================================

class GalleryItemBase(BaseModel):
    title: str
    image_url: str
    category: Optional[str] = "Photo Gallery"
    description: Optional[str] = None


class GalleryItemResponse(GalleryItemBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# VIDEO GALLERY SCHEMAS
# ============================================================

class VideoGalleryResponse(BaseModel):
    id: int
    title: str
    video_url: str
    description: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# UPCOMING PROJECT SCHEMAS
# ============================================================

class UpcomingProjectResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    expected_date: Optional[date] = None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# TEAM MEMBER SCHEMAS
# ============================================================

class TeamMemberBase(BaseModel):
    name: str
    role: Optional[str] = None
    photo_url: Optional[str] = None
    bio: Optional[str] = None


class TeamMemberResponse(TeamMemberBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# CERTIFICATE SCHEMAS
# ============================================================

class CertificateBase(BaseModel):
    title: str
    image_url: Optional[str] = None
    description: Optional[str] = None


class CertificateResponse(CertificateBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# BLOG SCHEMAS
# ============================================================

class BlogBase(BaseModel):
    title: str
    summary: Optional[str] = None
    content: str
    image_url: Optional[str] = None
    published_date: Optional[datetime] = None


class BlogResponse(BlogBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# ABOUT SCHEMAS
# ============================================================

class AboutBase(BaseModel):
    name: str
    tagline: Optional[str] = None
    mission: Optional[str] = None
    vision: Optional[str] = None
    founded: Optional[str] = None
    registration: Optional[str] = None


class AboutResponse(AboutBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# MEDIA SCHEMAS
# ============================================================

class MediaBase(BaseModel):
    title: str
    source: str
    url: str
    image_url: Optional[str] = None
    published_date: Optional[datetime] = None


class MediaResponse(MediaBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)