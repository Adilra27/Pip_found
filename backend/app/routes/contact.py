from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import ContactInquiry
from ..schemas import ContactCreate, ContactResponse
from .admin import get_current_admin

router = APIRouter(prefix="/api/contact", tags=["Contact"])

@router.post("", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
def submit_contact_form(contact_in: ContactCreate, db: Session = Depends(get_db)):
    inquiry = ContactInquiry(**contact_in.model_dump())
    db.add(inquiry)
    db.commit()
    db.refresh(inquiry)
    return inquiry

@router.get("", response_model=List[ContactResponse])
def list_contact_inquiries(
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    return db.query(ContactInquiry).order_by(ContactInquiry.created_at.desc()).all()

@router.delete("/{inquiry_id}", status_code=status.HTTP_200_OK)
def delete_contact_inquiry(
    inquiry_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    inquiry = (
        db.query(ContactInquiry)
        .filter(ContactInquiry.id == inquiry_id)
        .first()
    )

    if not inquiry:
        raise HTTPException(
            status_code=404,
            detail="Contact inquiry not found",
        )

    db.delete(inquiry)
    db.commit()

    return {"message": "Contact inquiry deleted"}
