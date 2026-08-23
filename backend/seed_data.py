import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine, Base
from app.models import Cause, GalleryItem, ContactInquiry, Donation

def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Check if causes exist
    if db.query(Cause).count() == 0:
        causes_data = [
            {
                "title": "Childhood Cancer Support & Treatment",
                "slug": "childhood-cancer-support",
                "category": "Healthcare",
                "short_description": "Helping children fight cancer and critical health illnesses with vital medical financial assistance and care.",
                "full_description": "Piplad Welfare Foundation supports underprivileged children fighting cancer and severe heart diseases. We provide access to specialized treatment, medications, and emotional support for families.",
                "target_amount": 500000.0,
                "raised_amount": 285000.0,
                "image_url": "https://images.unsplash.com/photo-1576765608535-5f04d1e3f289?auto=format&fit=crop&q=80&w=800"
            },
            {
                "title": "Education for All - Empowering Young Minds",
                "slug": "education-for-all",
                "category": "Education",
                "short_description": "Providing quality education materials, tuition support, and school supplies to bright children in need.",
                "full_description": "Every child deserves a chance to learn and grow. We provide school kits, textbooks, digital learning tools, and scholarships to ensure underprivileged children stay in school and build a bright future.",
                "target_amount": 300000.0,
                "raised_amount": 190000.0,
                "image_url": "https://images.unsplash.com/photo-1509062522246-3755977927d7?auto=format&fit=crop&q=80&w=800"
            },
            {
                "title": "Zero Hunger & Food Distribution Drive",
                "slug": "food-distribution-drive",
                "category": "Relief",
                "short_description": "Distributing warm meals, ration kits, and nutritional food to vulnerable communities and children daily.",
                "full_description": "Proper nutrition is vital for physical and mental development. Our foundation organizes daily and weekly food drives providing wholesome meals to destitute families, street kids, and rural communities.",
                "target_amount": 250000.0,
                "raised_amount": 142000.0,
                "image_url": "https://images.unsplash.com/photo-1488521787991-ed7bbaae773c?auto=format&fit=crop&q=80&w=800"
            },
            {
                "title": "Women Empowerment & Skill Development",
                "slug": "women-empowerment",
                "category": "Empowerment",
                "short_description": "Training women in vocational skills like sewing, handicrafts, and computer literacy to gain financial freedom.",
                "full_description": "Empowering a woman empowers an entire family. We offer skill development workshops, micro-entrepreneurship support, and self-reliance programs for women in rural and semi-urban areas.",
                "target_amount": 200000.0,
                "raised_amount": 85000.0,
                "image_url": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&q=80&w=800"
            }
        ]

        for c in causes_data:
            db.add(Cause(**c))
        print("Seeded Causes successfully!")

    # Check if gallery items exist
    if db.query(GalleryItem).count() == 0:
        gallery_data = [
            {
                "title": "Health Checkup & Medical Camp",
                "image_url": "https://images.unsplash.com/photo-1584515979956-d9f6e5d09982?auto=format&fit=crop&q=80&w=800",
                "category": "Healthcare"
            },
            {
                "title": "School Kit Distribution Event",
                "image_url": "https://images.unsplash.com/photo-1509062522246-3755977927d7?auto=format&fit=crop&q=80&w=800",
                "category": "Education"
            },
            {
                "title": "Community Meal & Ration Drive",
                "image_url": "https://images.unsplash.com/photo-1488521787991-ed7bbaae773c?auto=format&fit=crop&q=80&w=800",
                "category": "Food Drive"
            },
            {
                "title": "Annual Excellence & Recognition Award",
                "image_url": "https://images.unsplash.com/photo-1511578314322-379afb476865?auto=format&fit=crop&q=80&w=800",
                "category": "Awards"
            }
        ]

        for g in gallery_data:
            db.add(GalleryItem(**g))
        print("Seeded Gallery items successfully!")

    # Add sample seed donations if empty
    if db.query(Donation).count() == 0:
        sample_donations = [
            Donation(donor_name="Rajesh Sharma", donor_email="rajesh@example.com", amount=5000.0, cause_id=1, status="completed"),
            Donation(donor_name="Ananya Gupta", donor_email="ananya@example.com", amount=2500.0, cause_id=2, status="completed"),
            Donation(donor_name="Vikram Verma", donor_email="vikram@example.com", amount=10000.0, cause_id=3, status="completed"),
        ]
        for d in sample_donations:
            db.add(d)
        print("Seeded sample donations!")

    db.commit()
    db.close()
    print("Database seeding finished!")

if __name__ == "__main__":
    seed_database()
