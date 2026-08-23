from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from ..database import get_db
from ..models import Cause, Donation, ContactInquiry, GalleryItem
from ..schemas import GalleryItemResponse, GalleryItemBase
from fastapi import HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

security = HTTPBasic()

def get_current_admin(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "admin")
    correct_password = secrets.compare_digest(credentials.password, "admin")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username
router = APIRouter(prefix="/api/admin", tags=["Admin"])

@router.get("/stats")
def get_admin_dashboard_stats(db: Session = Depends(get_db), _: str = Depends(get_current_admin)):
    total_donations = db.query(func.sum(Donation.amount)).filter(Donation.status == "completed").scalar() or 0.0
    total_donors = db.query(Donation).filter(Donation.status == "completed").count()
    active_causes = db.query(Cause).count()
    inquiries_count = db.query(ContactInquiry).count()

    return {
        "total_donations": total_donations,
        "total_donors": total_donors,
        "active_causes": active_causes,
        "inquiries_count": inquiries_count
    }

@router.get("/gallery", response_model=List[GalleryItemResponse])
def get_gallery_items(db: Session = Depends(get_db), _: str = Depends(get_current_admin)):
    return db.query(GalleryItem).order_by(GalleryItem.id.desc()).all()

@router.post("/gallery", response_model=GalleryItemResponse)
def add_gallery_item(item: GalleryItemBase, db: Session = Depends(get_db), _: str = Depends(get_current_admin)):
    db_item = GalleryItem(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
