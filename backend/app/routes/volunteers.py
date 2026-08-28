from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import VolunteerApplication
from ..schemas import VolunteerApplicationCreate, VolunteerApplicationResponse

router = APIRouter(prefix="/api/volunteers", tags=["Volunteers"])


@router.post("", response_model=VolunteerApplicationResponse, status_code=201)
def create_volunteer_application(application: VolunteerApplicationCreate, db: Session = Depends(get_db)):
    volunteer = VolunteerApplication(
        full_name=application.full_name.strip(),
        email=application.email.strip().lower(),
        phone=application.phone.strip(),
        interest_area=application.interest_area.strip(),
        about_yourself=(application.about_yourself or "").strip() or None,
    )
    if not volunteer.full_name or not volunteer.email or not volunteer.phone or not volunteer.interest_area:
        raise HTTPException(400, "All required volunteer fields must be provided")

    db.add(volunteer)
    db.commit()
    db.refresh(volunteer)
    return volunteer