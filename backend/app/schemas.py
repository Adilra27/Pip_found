from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Cause Schemas

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

    class Config:
        from_attributes = True

# Contact Inquiry Schemas
class ContactCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    subject: Optional[str] = None
    message: str

class ContactResponse(ContactCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Donation Schemas
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

    class Config:
        from_attributes = True

# Gallery Item Schemas
class GalleryItemBase(BaseModel):
    title: str
    image_url: str
    category: Optional[str] = "Events"

class GalleryItemResponse(GalleryItemBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Team Member Schemas
class TeamMemberBase(BaseModel):
    name: str
    role: Optional[str] = None
    photo_url: Optional[str] = None
    bio: Optional[str] = None

class TeamMemberResponse(TeamMemberBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Certificate Schemas
class CertificateBase(BaseModel):
    title: str
    image_url: Optional[str] = None
    description: Optional[str] = None

class CertificateResponse(CertificateBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Blog Schemas

class BlogBase(BaseModel):
    title: str
    summary: Optional[str] = None
    content: str
    image_url: Optional[str] = None
    published_date: Optional[datetime] = None


class BlogResponse(BlogBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
        
# About Schemas
class AboutBase(BaseModel):
    name: str
    tagline: Optional[str] = None
    mission: Optional[str] = None
    vision: Optional[str] = None
    founded: Optional[str] = None
    registration: Optional[str] = None

class AboutResponse(AboutBase):
    id: int

    class Config:
        from_attributes = True

# Media Schemas
class MediaBase(BaseModel):
    title: str
    source: str
    url: str
    image_url: Optional[str] = None
    published_date: Optional[datetime] = None

class MediaResponse(MediaBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

