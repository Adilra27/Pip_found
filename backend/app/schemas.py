from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


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


class VolunteerApplicationCreate(BaseModel):
    full_name: str
    email: str
    phone: str
    interest_area: str
    about_yourself: Optional[str] = None


class VolunteerApplicationResponse(VolunteerApplicationCreate):
    id: int
    profile_pic_url: Optional[str] = None
    status: str
    volunteer_id: Optional[str] = None
    card_sent_at: Optional[datetime] = None
    card_emailed: Optional[bool] = None
    rejection_email_sent_at: Optional[datetime] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


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
    razorpay_order_id: Optional[str] = None
    razorpay_payment_id: Optional[str] = None
    receipt_sent_at: Optional[datetime] = None
    certificate_document_path: Optional[str] = None
    invoice_document_path: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DonationListResponse(BaseModel):
    items: List[DonationResponse]
    total: int
    page: int
    page_size: int


class GalleryItemBase(BaseModel):
    title: str
    image_url: str
    category: Optional[str] = "Photo Gallery"
    description: Optional[str] = None


class GalleryItemResponse(GalleryItemBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VideoGalleryResponse(BaseModel):
    id: int
    title: str
    video_url: str
    category: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


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
# TEAM
# ============================================================

class TeamMemberBase(BaseModel):
    name: str
    role: Optional[str] = None
    team: str = "General"
    photo_url: Optional[str] = None
    bio: Optional[str] = None


class TeamMemberResponse(TeamMemberBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# CERTIFICATES
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
# BLOG
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
# ABOUT
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
# MEDIA
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


# ============================================================
# IMPACT METRICS
# ============================================================

class ImpactMetricResponse(BaseModel):
    id: int
    metric_key: str
    metric_name: str
    category: str
    value: float
    unit: Optional[str] = None
    description: Optional[str] = None
    is_published: bool
    display_order: int
    last_updated: datetime

    model_config = ConfigDict(from_attributes=True)


class ImpactMetricUpdate(BaseModel):
    value: float
    is_published: bool = True
    metric_name: Optional[str] = None
    description: Optional[str] = None


class ImpactMetricsUpdateRequest(BaseModel):
    metrics: List[ImpactMetricUpdate]


class PublicImpactMetric(BaseModel):
    key: str
    name: str
    value: float
    unit: Optional[str] = None
    display_order: int


class PublicImpactGroup(BaseModel):
    key: str
    name: str
    metrics: List[PublicImpactMetric]


class PublicImpactResponse(BaseModel):
    last_updated: Optional[date] = None
    groups: List[PublicImpactGroup]
    has_verified_carbon_credits: bool
    verified_carbon_credits_value: Optional[float] = None