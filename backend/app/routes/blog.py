from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Blog
from ..schemas import BlogResponse

router = APIRouter(prefix="/api/blog", tags=["Blog"])

@router.get("", response_model=List[BlogResponse])
def get_blog_posts(db: Session = Depends(get_db)):
    return db.query(Blog).order_by(Blog.published_date.desc()).all()
