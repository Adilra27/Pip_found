from datetime import datetime

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship

from .database import Base


class Cause(Base):
    __tablename__ = "causes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, index=True)
    category = Column(String(100), default="General")
    short_description = Column(Text, nullable=False)
    full_description = Column(Text, nullable=True)
    target_amount = Column(Numeric(12, 2), default=100000.0)
    raised_amount = Column(Numeric(12, 2), default=0.0)
    image_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    donations = relationship("Donation", back_populates="cause")


class Donation(Base):
    __tablename__ = "donations"
    id = Column(Integer, primary_key=True, index=True)
    donor_name = Column(String(255), nullable=False)
    donor_email = Column(String(255), nullable=False)
    donor_phone = Column(String(50), nullable=True)
    amount = Column(Numeric(12, 2), nullable=False)
    cause_id = Column(Integer, ForeignKey("causes.id"), nullable=True)
    razorpay_order_id = Column(String(255), nullable=True)
    razorpay_payment_id = Column(String(255), nullable=True)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    cause = relationship("Cause", back_populates="donations")


class ContactInquiry(Base):
    __tablename__ = "contact_inquiries"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    subject = Column(String(255), nullable=True)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class VolunteerApplication(Base):
    __tablename__ = "volunteer_applications"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=False)
    interest_area = Column(String(255), nullable=False)
    about_yourself = Column(Text, nullable=True)
    profile_pic_url = Column(String(500), nullable=True)
    status = Column(String(50), nullable=False, default="pending", index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class TeamMember(Base):
    __tablename__ = "team_members"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    role = Column(String(255), nullable=True)
    photo_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Certificate(Base):
    __tablename__ = "certificates"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    image_url = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class GalleryItem(Base):
    __tablename__ = "gallery_items"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    image_url = Column(String(500), nullable=False)
    category = Column(String(100), default="Photo Gallery")
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class VideoGallery(Base):
    __tablename__ = "video_gallery"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    video_url = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class UpcomingProject(Base):
    __tablename__ = "upcoming_projects"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)
    expected_date = Column(Date, nullable=True)
    status = Column(String(50), nullable=False, default="upcoming", index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Blog(Base):
    __tablename__ = "blogs"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    summary = Column(Text, nullable=True)
    content = Column(Text, nullable=False)
    image_url = Column(String(500), nullable=True)
    source_url = Column(String(500), nullable=True)
    published_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class About(Base):
    __tablename__ = "about_info"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    tagline = Column(String(255), nullable=True)
    mission = Column(Text, nullable=True)
    vision = Column(Text, nullable=True)
    founded = Column(String(100), nullable=True)
    registration = Column(String(255), nullable=True)


class Media(Base):
    __tablename__ = "media_coverage"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    source = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False)
    image_url = Column(String(500), nullable=True)
    published_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
