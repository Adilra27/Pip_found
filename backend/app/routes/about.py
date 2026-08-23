from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import About
from ..schemas import AboutResponse

router = APIRouter(prefix="/api/about", tags=["About"])

@router.get("", response_model=AboutResponse)
def get_about_info(db: Session = Depends(get_db)):
    info = db.query(About).first()
    if not info:
        # Fallback if db is empty
        return AboutResponse(
            id=0,
            name="Piplad Welfare Foundation",
            tagline="Creating Opportunities, Creating Lives",
            mission="To empower underprivileged communities through healthcare, education, food security, and women empowerment initiatives.",
            vision="A world where every individual has equal access to basic necessities and opportunities to thrive.",
            founded="2020",
            registration="Registered under Indian Trust Act"
        )
    return info
