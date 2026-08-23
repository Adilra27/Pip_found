from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Media
from ..schemas import MediaResponse

router = APIRouter(prefix="/api/media", tags=["Media"])

@router.get("", response_model=List[MediaResponse])
def get_media_coverage(db: Session = Depends(get_db)):
    return db.query(Media).order_by(Media.published_date.desc()).all()
