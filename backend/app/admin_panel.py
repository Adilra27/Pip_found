from sqladmin import Admin, ModelView

from .database import engine
from .models import (
    About,
    Blog,
    Cause,
    Certificate,
    ContactInquiry,
    Donation,
    GalleryItem,
    Media,
    TeamMember,
    UpcomingProject,
    VideoGallery,
)


class CauseAdmin(ModelView, model=Cause):
    column_list = [Cause.id, Cause.title, Cause.category, Cause.target_amount, Cause.raised_amount, Cause.created_at]
    icon = "fa-solid fa-hands-holding-child"


class DonationAdmin(ModelView, model=Donation):
    column_list = [Donation.id, Donation.donor_name, Donation.amount, Donation.status, Donation.created_at]
    icon = "fa-solid fa-hand-holding-dollar"


class ContactInquiryAdmin(ModelView, model=ContactInquiry):
    column_list = [ContactInquiry.id, ContactInquiry.name, ContactInquiry.email, ContactInquiry.subject, ContactInquiry.created_at]
    icon = "fa-solid fa-envelope"


class TeamMemberAdmin(ModelView, model=TeamMember):
    column_list = [TeamMember.id, TeamMember.name, TeamMember.role, TeamMember.created_at]
    icon = "fa-solid fa-users"


class CertificateAdmin(ModelView, model=Certificate):
    column_list = [Certificate.id, Certificate.title, Certificate.created_at]
    icon = "fa-solid fa-certificate"


class GalleryItemAdmin(ModelView, model=GalleryItem):
    column_list = [GalleryItem.id, GalleryItem.title, GalleryItem.category, GalleryItem.created_at]
    icon = "fa-solid fa-image"


class VideoGalleryAdmin(ModelView, model=VideoGallery):
    column_list = [VideoGallery.id, VideoGallery.title, VideoGallery.created_at]
    icon = "fa-solid fa-video"


class UpcomingProjectAdmin(ModelView, model=UpcomingProject):
    column_list = [UpcomingProject.id, UpcomingProject.title, UpcomingProject.status, UpcomingProject.expected_date]
    icon = "fa-solid fa-calendar-days"


class BlogAdmin(ModelView, model=Blog):
    column_list = [Blog.id, Blog.title, Blog.published_date]
    icon = "fa-solid fa-newspaper"


class AboutAdmin(ModelView, model=About):
    column_list = [About.id, About.name, About.tagline, About.founded]
    icon = "fa-solid fa-building"


class MediaAdmin(ModelView, model=Media):
    column_list = [Media.id, Media.title, Media.source, Media.published_date]
    icon = "fa-solid fa-newspaper"


def setup_admin(app):
    admin = Admin(app, engine, title="PWF Admin Dashboard")
    admin.add_view(CauseAdmin)
    admin.add_view(DonationAdmin)
    admin.add_view(BlogAdmin)
    admin.add_view(TeamMemberAdmin)
    admin.add_view(GalleryItemAdmin)
    admin.add_view(VideoGalleryAdmin)
    admin.add_view(UpcomingProjectAdmin)
    admin.add_view(CertificateAdmin)
    admin.add_view(MediaAdmin)
    admin.add_view(ContactInquiryAdmin)
    admin.add_view(AboutAdmin)
