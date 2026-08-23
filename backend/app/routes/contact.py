from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import ContactInquiry
from ..schemas import ContactCreate, ContactResponse

router = APIRouter(prefix="/api/contact", tags=["Contact"])

@router.post("", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
def submit_contact_form(contact_in: ContactCreate, db: Session = Depends(get_db)):
    inquiry = ContactInquiry(**contact_in.model_dump())
    db.add(inquiry)
    db.commit()
    db.refresh(inquiry)
    return inquiry

@router.get("", response_model=List[ContactResponse])
def list_contact_inquiries(db: Session = Depends(get_db)):
    return db.query(ContactInquiry).order_by(ContactInquiry.created_at.desc()).all()
