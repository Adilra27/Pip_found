from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Cause
from ..schemas import CauseResponse, CauseCreate

router = APIRouter(prefix="/api/causes", tags=["Causes"])

@router.get("", response_model=List[CauseResponse])
def get_all_causes(db: Session = Depends(get_db)):
    return db.query(Cause).all()

@router.get("/{cause_id}", response_model=CauseResponse)
def get_cause_by_id(cause_id: int, db: Session = Depends(get_db)):
    cause = db.query(Cause).filter(Cause.id == cause_id).first()
    if not cause:
        raise HTTPException(status_code=404, detail="Cause not found")
    return cause

@router.post("", response_model=CauseResponse, status_code=status.HTTP_201_CREATED)
def create_cause(cause_in: CauseCreate, db: Session = Depends(get_db)):
    existing = db.query(Cause).filter(Cause.slug == cause_in.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="Slug already exists")
    db_cause = Cause(**cause_in.model_dump())
    db.add(db_cause)
    db.commit()
    db.refresh(db_cause)
    return db_cause
